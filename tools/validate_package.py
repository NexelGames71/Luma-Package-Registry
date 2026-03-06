#!/usr/bin/env python3
"""
Luma Package Registry - Validate Package Script
Checks package.json schema compliance.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

PACKAGE_NAME_PATTERN = re.compile(r"^[a-z0-9]+(\.[a-z0-9]+)+$")
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
VERSION_CONSTRAINT_TOKEN_PATTERN = re.compile(r"^(>=|<=|>|<|=|\^|~)?\d+\.\d+\.\d+$")
VALID_CATEGORIES = {"registry", "assets-store"}
LEGACY_CATEGORIES = {"core", "third-party"}


def is_valid_semver(value: str) -> bool:
    return isinstance(value, str) and SEMVER_PATTERN.fullmatch(value) is not None


def is_valid_http_url(value: str) -> bool:
    return isinstance(value, str) and (value.startswith("http://") or value.startswith("https://"))


def is_valid_version_constraint(value: str) -> bool:
    """Allow a single token or a space-separated range."""
    if not isinstance(value, str):
        return False
    tokens = [token.strip() for token in value.split() if token.strip()]
    if not tokens:
        return False
    return all(VERSION_CONSTRAINT_TOKEN_PATTERN.fullmatch(token) for token in tokens)


def validate_package_data(package: dict[str, Any], source_label: str = "package.json") -> tuple[bool, list[str]]:
    """Validate parsed package metadata."""
    errors: list[str] = []

    required_fields: dict[str, type] = {
        "name": str,
        "version": str,
        "displayName": str,
        "description": str,
        "engine": dict,
    }

    for field, field_type in required_fields.items():
        if field not in package:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(package[field], field_type):
            errors.append(f"Invalid type for {field}: expected {field_type.__name__}")

    if "name" in package and isinstance(package["name"], str):
        name = package["name"].strip()
        if not name:
            errors.append("name cannot be empty")
        elif PACKAGE_NAME_PATTERN.fullmatch(name) is None:
            errors.append("name must follow reverse-domain notation (e.g., com.nexel.package)")

    if "version" in package and isinstance(package["version"], str):
        version = package["version"].strip()
        if not version:
            errors.append("version cannot be empty")
        elif not is_valid_semver(version):
            errors.append("version must follow SemVer format MAJOR.MINOR.PATCH (e.g., 1.0.0)")

    if "displayName" in package and isinstance(package["displayName"], str):
        if not package["displayName"].strip():
            errors.append("displayName cannot be empty")

    if "description" in package and isinstance(package["description"], str):
        if not package["description"].strip():
            errors.append("description cannot be empty")

    if "engine" in package and isinstance(package["engine"], dict):
        if "luma" not in package["engine"]:
            errors.append("engine.luma is required")
        else:
            luma_version = package["engine"]["luma"]
            if not isinstance(luma_version, str):
                errors.append("engine.luma must be a string")
            elif not is_valid_version_constraint(luma_version):
                errors.append(
                    "engine.luma must be a valid version constraint "
                    "(examples: >=1.0.0, ^1.0.0, >=1.0.0 <2.0.0)"
                )

    if "author" in package:
        author = package["author"]
        if isinstance(author, dict):
            if "name" not in author or not isinstance(author.get("name"), str) or not author.get("name", "").strip():
                errors.append("author.name is required when author is an object")
            if "url" in author and not is_valid_http_url(author["url"]):
                errors.append("author.url must be a valid HTTP/HTTPS URL")
        elif not isinstance(author, str):
            errors.append("author must be a string or an object with 'name' and optional 'url'")

    if "dependencies" in package:
        dependencies = package["dependencies"]
        if not isinstance(dependencies, dict):
            errors.append("dependencies must be an object")
        else:
            for dep_name, dep_version in dependencies.items():
                if not isinstance(dep_name, str) or PACKAGE_NAME_PATTERN.fullmatch(dep_name) is None:
                    errors.append(f"Invalid dependency name format: {dep_name}")
                if not isinstance(dep_version, str) or not is_valid_version_constraint(dep_version):
                    errors.append(f"Invalid dependency version for {dep_name}: '{dep_version}'")

    if "keywords" in package:
        keywords = package["keywords"]
        if not isinstance(keywords, list):
            errors.append("keywords must be an array")
        else:
            for keyword in keywords:
                if not isinstance(keyword, str):
                    errors.append(f"Invalid keyword type: {keyword} must be a string")

    if "category" in package:
        category = package["category"]
        if not isinstance(category, str):
            errors.append("category must be a string")
        elif category not in VALID_CATEGORIES and category not in LEGACY_CATEGORIES:
            errors.append("category must be one of: registry, assets-store, core, third-party")

    if "homepage" in package and not is_valid_http_url(package["homepage"]):
        errors.append("homepage must be a valid HTTP/HTTPS URL")

    if "samples" in package:
        samples = package["samples"]
        if not isinstance(samples, list):
            errors.append("samples must be an array")
        else:
            for i, sample in enumerate(samples):
                if not isinstance(sample, dict):
                    errors.append(f"Sample {i} must be an object")
                    continue
                if "displayName" not in sample or not isinstance(sample.get("displayName"), str):
                    errors.append(f"Sample {i} missing required field: displayName")
                if "path" not in sample or not isinstance(sample.get("path"), str):
                    errors.append(f"Sample {i} missing required field: path")

    if "postInstall" in package:
        post_install = package["postInstall"]
        if not isinstance(post_install, list):
            errors.append("postInstall must be an array")
        else:
            for script in post_install:
                if not isinstance(script, str):
                    errors.append(f"postInstall script must be a string: {script}")

    return len(errors) == 0, [f"{source_label}: {error}" for error in errors]


def validate_package_json(package_json_path: Path) -> tuple[bool, list[str]]:
    """Validate a package.json file against the schema."""
    if not package_json_path.exists():
        return False, [f"package.json not found: {package_json_path}"]

    try:
        with package_json_path.open("r", encoding="utf-8") as f:
            package = json.load(f)
    except json.JSONDecodeError as exc:
        return False, [f"{package_json_path}: Invalid JSON: {exc}"]
    except Exception as exc:
        return False, [f"{package_json_path}: Error reading file: {exc}"]

    return validate_package_data(package, str(package_json_path))


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: validate_package.py <package.json_path>")
        sys.exit(1)

    package_json_path = Path(sys.argv[1])
    is_valid, errors = validate_package_json(package_json_path)

    if is_valid:
        print(f"[OK] package.json is valid: {package_json_path}")
        sys.exit(0)

    print(f"[FAIL] package.json validation failed: {package_json_path}")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)


if __name__ == "__main__":
    main()

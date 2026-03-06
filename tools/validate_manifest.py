#!/usr/bin/env python3
"""
Luma Package Registry - Validate Manifest Script
Checks schema compliance, archive integrity, and dependency constraints.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

PACKAGE_NAME_PATTERN = re.compile(r"^[a-z0-9]+(\.[a-z0-9]+)+$")
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
VERSION_CONSTRAINT_TOKEN_PATTERN = re.compile(r"^(>=|<=|>|<|=|\^|~)?(\d+\.\d+\.\d+)$")
VALID_CATEGORIES = {"registry", "assets-store", "core", "third-party"}

REQUIRED_MANIFEST_FIELDS: dict[str, type] = {
    "name": str,
    "versions": list,
}

REQUIRED_VERSION_FIELDS: dict[str, type] = {
    "version": str,
    "shasum": str,
    "url": str,
    "published": str,
}

OPTIONAL_VERSION_FIELDS: Dict[str, Union[Tuple[type, ...], type]] = {
    "dependencies": dict,
    "engineVersion": (str, dict),
    "description": str,
    "size": int,
    "category": str,
}


def parse_semver(value: str) -> Optional[Tuple[int, int, int]]:
    if not isinstance(value, str) or SEMVER_PATTERN.fullmatch(value) is None:
        return None
    major, minor, patch = value.split(".")
    return int(major), int(minor), int(patch)


def compare_semver(left: Tuple[int, int, int], right: Tuple[int, int, int]) -> int:
    if left < right:
        return -1
    if left > right:
        return 1
    return 0


def is_valid_version_constraint(value: str) -> bool:
    if not isinstance(value, str):
        return False
    tokens = [token.strip() for token in value.split() if token.strip()]
    if not tokens:
        return False
    return all(VERSION_CONSTRAINT_TOKEN_PATTERN.fullmatch(token) for token in tokens)


def _caret_upper_bound(version: Tuple[int, int, int]) -> Tuple[int, int, int]:
    major, minor, patch = version
    if major > 0:
        return major + 1, 0, 0
    if minor > 0:
        return 0, minor + 1, 0
    return 0, 0, patch + 1


def _tilde_upper_bound(version: Tuple[int, int, int]) -> Tuple[int, int, int]:
    major, minor, _ = version
    return major, minor + 1, 0


def _satisfies_token(
    version: Tuple[int, int, int],
    operator: Optional[str],
    rhs: Tuple[int, int, int],
) -> bool:
    cmp = compare_semver(version, rhs)
    if operator in (None, "", "="):
        return cmp == 0
    if operator == ">":
        return cmp > 0
    if operator == ">=":
        return cmp >= 0
    if operator == "<":
        return cmp < 0
    if operator == "<=":
        return cmp <= 0
    if operator == "^":
        return cmp >= 0 and compare_semver(version, _caret_upper_bound(rhs)) < 0
    if operator == "~":
        return cmp >= 0 and compare_semver(version, _tilde_upper_bound(rhs)) < 0
    return False


def satisfies_constraint(version: str, constraint: str) -> bool:
    version_tuple = parse_semver(version)
    if version_tuple is None or not is_valid_version_constraint(constraint):
        return False

    tokens = [token.strip() for token in constraint.split() if token.strip()]
    for token in tokens:
        match = VERSION_CONSTRAINT_TOKEN_PATTERN.fullmatch(token)
        if match is None:
            return False
        operator = match.group(1)
        rhs = parse_semver(match.group(2))
        if rhs is None or not _satisfies_token(version_tuple, operator, rhs):
            return False
    return True


def is_valid_http_url(value: str) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def is_valid_iso8601_utc(value: str) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def compute_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def expected_archive_path(registry_root: Path, package_name: str, version: str) -> Path:
    filename = f"{package_name}-{version}.zip"
    return registry_root / "packages" / package_name / version / filename


def build_dependency_index(registry_root: Path) -> Dict[str, List[str]]:
    manifests_root = registry_root / "manifests"
    versions_by_package: Dict[str, List[str]] = {}

    if not manifests_root.exists():
        return versions_by_package

    for manifest_path in manifests_root.glob("*/index.json"):
        try:
            with manifest_path.open("r", encoding="utf-8") as handle:
                manifest = json.load(handle)
        except Exception:
            continue

        package_name = manifest.get("name")
        if not isinstance(package_name, str):
            continue

        versions: List[str] = []
        for version_entry in manifest.get("versions", []):
            if isinstance(version_entry, dict) and isinstance(version_entry.get("version"), str):
                versions.append(version_entry["version"])
        versions_by_package[package_name] = versions

    return versions_by_package


def validate_engine_version(engine_version: Any) -> list[str]:
    errors: list[str] = []
    if isinstance(engine_version, str):
        if not is_valid_version_constraint(engine_version):
            errors.append("engineVersion string must be a valid version constraint")
        return errors

    if isinstance(engine_version, dict):
        has_min = "min" in engine_version
        has_max = "max" in engine_version
        if not has_min and not has_max:
            errors.append("engineVersion object must contain 'min' or 'max'")
            return errors

        if has_min:
            if not isinstance(engine_version["min"], str) or parse_semver(engine_version["min"]) is None:
                errors.append("engineVersion.min must be a SemVer string (e.g., 1.0.0)")
        if has_max:
            if not isinstance(engine_version["max"], str) or parse_semver(engine_version["max"]) is None:
                errors.append("engineVersion.max must be a SemVer string (e.g., 2.0.0)")

        if has_min and has_max:
            min_semver = parse_semver(engine_version["min"])
            max_semver = parse_semver(engine_version["max"])
            if min_semver and max_semver and compare_semver(min_semver, max_semver) > 0:
                errors.append("engineVersion.min cannot be greater than engineVersion.max")
        return errors

    errors.append("engineVersion must be either a string or an object")
    return errors


def _validate_dependencies(
    dependencies: Any,
    dependency_versions: Optional[Dict[str, List[str]]],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(dependencies, dict):
        return ["dependencies must be an object"]

    for dep_name, dep_constraint in dependencies.items():
        if not isinstance(dep_name, str) or PACKAGE_NAME_PATTERN.fullmatch(dep_name) is None:
            errors.append(f"Invalid dependency name '{dep_name}'")
            continue
        if not isinstance(dep_constraint, str) or not is_valid_version_constraint(dep_constraint):
            errors.append(f"Dependency '{dep_name}' has invalid version constraint '{dep_constraint}'")
            continue

        if dependency_versions is None:
            continue

        available_versions = dependency_versions.get(dep_name)
        if not available_versions:
            errors.append(f"Dependency '{dep_name}' is not present in manifests/")
            continue

        if not any(satisfies_constraint(version, dep_constraint) for version in available_versions):
            errors.append(
                f"Dependency '{dep_name}' constraint '{dep_constraint}' does not match any available version"
            )

    return errors


def _validate_archive_integrity(
    package_name: str,
    version_entry: dict[str, Any],
    registry_root: Path,
) -> list[str]:
    errors: list[str] = []
    version = version_entry.get("version")
    if not isinstance(version, str):
        return errors

    archive_path = expected_archive_path(registry_root, package_name, version)
    if not archive_path.exists():
        return [f"Package archive not found: {archive_path}"]

    if "size" in version_entry:
        size = version_entry["size"]
        if not isinstance(size, int) or size < 0:
            errors.append("size must be a non-negative integer")
        else:
            actual_size = archive_path.stat().st_size
            if actual_size != size:
                errors.append(f"size mismatch: manifest={size}, actual={actual_size}")

    shasum = version_entry.get("shasum")
    if isinstance(shasum, str) and SHA256_PATTERN.fullmatch(shasum):
        actual_sha = compute_sha256(archive_path)
        if actual_sha != shasum:
            errors.append(f"shasum mismatch: manifest={shasum}, actual={actual_sha}")

    url = version_entry.get("url")
    if isinstance(url, str):
        expected_suffix = f"/packages/{package_name}/{version}/{package_name}-{version}.zip"
        if not url.endswith(expected_suffix):
            errors.append(f"url does not match package location convention: expected suffix '{expected_suffix}'")

    return errors


def validate_version(
    version_entry: dict[str, Any],
    package_name: str,
    registry_root: Optional[Path] = None,
    dependency_versions: Optional[Dict[str, List[str]]] = None,
) -> list[str]:
    errors: list[str] = []

    for field, field_type in REQUIRED_VERSION_FIELDS.items():
        if field not in version_entry:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(version_entry[field], field_type):
            errors.append(f"Invalid type for {field}: expected {field_type.__name__}")

    for field, field_type in OPTIONAL_VERSION_FIELDS.items():
        if field not in version_entry:
            continue
        if isinstance(field_type, tuple):
            if not isinstance(version_entry[field], field_type):
                expected = " or ".join(t.__name__ for t in field_type)
                errors.append(f"Invalid type for {field}: expected {expected}")
        elif not isinstance(version_entry[field], field_type):
            errors.append(f"Invalid type for {field}: expected {field_type.__name__}")

    version = version_entry.get("version")
    if isinstance(version, str):
        if parse_semver(version) is None:
            errors.append("version must follow strict SemVer format MAJOR.MINOR.PATCH")
    else:
        version = None

    shasum = version_entry.get("shasum")
    if isinstance(shasum, str) and SHA256_PATTERN.fullmatch(shasum) is None:
        errors.append("shasum must be 64 lowercase hexadecimal characters")

    url = version_entry.get("url")
    if isinstance(url, str) and not is_valid_http_url(url):
        errors.append("url must be a valid HTTP/HTTPS URL")

    published = version_entry.get("published")
    if isinstance(published, str) and not is_valid_iso8601_utc(published):
        errors.append("published must be a valid ISO-8601 timestamp")

    if "category" in version_entry:
        category = version_entry["category"]
        if not isinstance(category, str) or category not in VALID_CATEGORIES:
            errors.append("category must be one of: registry, assets-store, core, third-party")

    if "dependencies" in version_entry:
        errors.extend(_validate_dependencies(version_entry["dependencies"], dependency_versions))

    if "engineVersion" in version_entry:
        errors.extend(validate_engine_version(version_entry["engineVersion"]))

    if registry_root is not None and version is not None:
        errors.extend(_validate_archive_integrity(package_name, version_entry, registry_root))

    return errors


def validate_manifest(
    manifest_path: Path,
    registry_root: Optional[Path] = None,
    dependency_versions: Optional[Dict[str, List[str]]] = None,
) -> tuple[bool, list[str]]:
    errors: list[str] = []

    if not manifest_path.exists():
        return False, [f"Manifest file not found: {manifest_path}"]

    try:
        with manifest_path.open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)
    except json.JSONDecodeError as exc:
        return False, [f"Invalid JSON: {exc}"]
    except Exception as exc:
        return False, [f"Error reading file: {exc}"]

    for field, field_type in REQUIRED_MANIFEST_FIELDS.items():
        if field not in manifest:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(manifest[field], field_type):
            errors.append(f"Invalid type for {field}: expected {field_type.__name__}")

    package_name = manifest.get("name")
    if isinstance(package_name, str):
        if PACKAGE_NAME_PATTERN.fullmatch(package_name) is None:
            errors.append("name must follow reverse-domain notation (e.g., com.nexel.package)")
    else:
        package_name = "unknown"

    versions = manifest.get("versions")
    if not isinstance(versions, list):
        errors.append("'versions' must be an array")
        versions = []

    seen_versions: set[str] = set()
    parsed_versions: List[Tuple[int, int, int]] = []
    for i, version_entry in enumerate(versions):
        if not isinstance(version_entry, dict):
            errors.append(f"Version entry {i} is not an object")
            continue

        version_errors = validate_version(
            version_entry,
            package_name,
            registry_root=registry_root,
            dependency_versions=dependency_versions,
        )
        version_label = version_entry.get("version", f"index {i}")
        for error in version_errors:
            errors.append(f"Version {version_label}: {error}")

        version_string = version_entry.get("version")
        if isinstance(version_string, str):
            if version_string in seen_versions:
                errors.append(f"Duplicate version entry '{version_string}'")
            seen_versions.add(version_string)
            parsed = parse_semver(version_string)
            if parsed is not None:
                parsed_versions.append(parsed)

    if parsed_versions:
        sorted_desc = sorted(parsed_versions, reverse=True)
        if parsed_versions != sorted_desc:
            errors.append("versions should be sorted from newest to oldest")

    return len(errors) == 0, errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a package manifest")
    parser.add_argument("manifest_path", type=Path, help="Path to manifests/<package>/index.json")
    parser.add_argument(
        "--registry-root",
        type=Path,
        default=None,
        help="Registry root path for checksum and dependency resolution (optional)",
    )
    args = parser.parse_args()

    dependency_versions: Optional[Dict[str, List[str]]] = None
    registry_root: Optional[Path] = args.registry_root
    if registry_root is not None:
        dependency_versions = build_dependency_index(registry_root)

    is_valid, errors = validate_manifest(
        args.manifest_path,
        registry_root=registry_root,
        dependency_versions=dependency_versions,
    )

    if is_valid:
        print(f"[OK] Manifest is valid: {args.manifest_path}")
        sys.exit(0)

    print(f"[FAIL] Manifest validation failed: {args.manifest_path}")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)


if __name__ == "__main__":
    main()

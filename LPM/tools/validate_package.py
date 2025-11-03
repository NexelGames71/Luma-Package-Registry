#!/usr/bin/env python3
"""
Luma Package Registry - Validate Package Script
Checks package.json schema compliance
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Any

def validate_package_json(package_json_path: Path) -> tuple[bool, List[str]]:
    """Validate a package.json file against the schema"""
    errors = []
    
    if not package_json_path.exists():
        return False, [f"package.json not found: {package_json_path}"]
    
    try:
        with open(package_json_path, 'r', encoding='utf-8') as f:
            package = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]
    except Exception as e:
        return False, [f"Error reading file: {e}"]
    
    # Required fields
    required_fields = {
        "name": str,
        "version": str,
        "displayName": str,
        "description": str,
        "engine": dict
    }
    
    for field, field_type in required_fields.items():
        if field not in package:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(package[field], field_type):
            errors.append(f"Invalid type for {field}: expected {field_type.__name__}")
    
    # Validate name pattern (reverse-domain)
    if "name" in package:
        name_pattern = r"^[a-z0-9]+(\.[a-z0-9]+)+$"
        if not re.match(name_pattern, package["name"]):
            errors.append("Package name must follow reverse-domain notation (e.g., com.nexel.package)")
    
    # Validate version pattern (SemVer)
    if "version" in package:
        version_pattern = r"^\d+\.\d+\.\d+$"
        if not re.match(version_pattern, package["version"]):
            errors.append("Version must follow SemVer format (e.g., 1.0.0)")
    
    # Validate engine field
    if "engine" in package and isinstance(package["engine"], dict):
        if "luma" not in package["engine"]:
            errors.append("engine.luma is required")
        else:
            luma_version = package["engine"]["luma"]
            if not isinstance(luma_version, str):
                errors.append("engine.luma must be a string")
            else:
                # Validate version constraint pattern
                version_pattern = r"^(>=|<=|>|<|=|\^|~)?\d+\.\d+\.\d+"
                if not re.match(version_pattern, luma_version):
                    errors.append("engine.luma must match pattern: (>=|<=|>|<|=|^|~)?X.Y.Z")
    
    # Validate author (if present)
    if "author" in package:
        if isinstance(package["author"], dict):
            if "name" not in package["author"]:
                errors.append("author.name is required when author is an object")
            if "url" in package["author"]:
                url = package["author"]["url"]
                if not isinstance(url, str) or not (url.startswith("http://") or url.startswith("https://")):
                    errors.append("author.url must be a valid HTTP/HTTPS URL")
        elif not isinstance(package["author"], str):
            errors.append("author must be a string or an object with 'name' and optional 'url'")
    
    # Validate dependencies (if present)
    if "dependencies" in package:
        if not isinstance(package["dependencies"], dict):
            errors.append("dependencies must be an object")
        else:
            dep_pattern = r"^[a-z0-9]+(\.[a-z0-9]+)+$"
            for dep_name, dep_version in package["dependencies"].items():
                if not re.match(dep_pattern, dep_name):
                    errors.append(f"Invalid dependency name format: {dep_name}")
                if not isinstance(dep_version, str):
                    errors.append(f"Invalid dependency version type for {dep_name}: must be string")
    
    # Validate keywords (if present)
    if "keywords" in package:
        if not isinstance(package["keywords"], list):
            errors.append("keywords must be an array")
        else:
            for keyword in package["keywords"]:
                if not isinstance(keyword, str):
                    errors.append(f"Invalid keyword type: {keyword} must be a string")
    
    # Validate homepage (if present)
    if "homepage" in package:
        homepage = package["homepage"]
        if not isinstance(homepage, str) or not (homepage.startswith("http://") or homepage.startswith("https://")):
            errors.append("homepage must be a valid HTTP/HTTPS URL")
    
    # Validate samples (if present)
    if "samples" in package:
        if not isinstance(package["samples"], list):
            errors.append("samples must be an array")
        else:
            for i, sample in enumerate(package["samples"]):
                if not isinstance(sample, dict):
                    errors.append(f"Sample {i} must be an object")
                else:
                    if "displayName" not in sample:
                        errors.append(f"Sample {i} missing required field: displayName")
                    if "path" not in sample:
                        errors.append(f"Sample {i} missing required field: path")
    
    # Validate postInstall (if present)
    if "postInstall" in package:
        if not isinstance(package["postInstall"], list):
            errors.append("postInstall must be an array")
        else:
            for script in package["postInstall"]:
                if not isinstance(script, str):
                    errors.append(f"postInstall script must be a string: {script}")
    
    return len(errors) == 0, errors

def main():
    """Main validation function"""
    if len(sys.argv) < 2:
        print("Usage: validate_package.py <package.json_path>")
        sys.exit(1)
    
    package_json_path = Path(sys.argv[1])
    is_valid, errors = validate_package_json(package_json_path)
    
    if is_valid:
        print(f"✓ package.json is valid: {package_json_path}")
        sys.exit(0)
    else:
        print(f"✗ package.json validation failed: {package_json_path}")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()


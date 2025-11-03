#!/usr/bin/env python3
"""
Luma Package Registry - Validate Manifest Script
Checks schema compliance for package manifests
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Schema definition
REQUIRED_MANIFEST_FIELDS = {
    "name": str,
    "versions": list
}

REQUIRED_VERSION_FIELDS = {
    "version": str,
    "shasum": str,
    "url": str,
    "published": str
}

OPTIONAL_VERSION_FIELDS = {
    "dependencies": dict,
    "engineVersion": (str, dict),
    "description": str,
    "size": int
}

def validate_version(version: Dict[str, Any], package_name: str) -> List[str]:
    """Validate a single version entry"""
    errors = []
    
    # Check required fields
    for field, field_type in REQUIRED_VERSION_FIELDS.items():
        if field not in version:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(version[field], field_type):
            errors.append(f"Invalid type for {field}: expected {field_type.__name__}")
    
    # Validate version format (SemVer)
    version_str = version.get("version", "")
    if version_str:
        parts = version_str.split(".")
        if len(parts) != 3:
            errors.append(f"Invalid version format '{version_str}': must be SemVer (e.g., 1.0.0)")
        else:
            try:
                for part in parts:
                    int(part)
            except ValueError:
                errors.append(f"Invalid version format '{version_str}': parts must be numeric")
    
    # Validate SHA256 format
    shasum = version.get("shasum", "")
    if shasum and len(shasum) != 64:
        errors.append(f"Invalid SHA256 format: must be 64 hexadecimal characters")
    
    # Validate URL format
    url = version.get("url", "")
    if url and not url.startswith("http"):
        errors.append(f"Invalid URL format: must start with http:// or https://")
    
    # Validate engineVersion format
    engine_version = version.get("engineVersion")
    if engine_version:
        if isinstance(engine_version, str):
            # Simple version string
            pass
        elif isinstance(engine_version, dict):
            # Version range: { "min": "1.0.0", "max": "2.0.0" }
            if "min" not in engine_version and "max" not in engine_version:
                errors.append("engineVersion object must contain 'min' or 'max' field")
    
    return errors

def validate_manifest(manifest_path: Path) -> tuple[bool, List[str]]:
    """Validate a manifest file"""
    errors = []
    
    if not manifest_path.exists():
        return False, [f"Manifest file not found: {manifest_path}"]
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]
    except Exception as e:
        return False, [f"Error reading file: {e}"]
    
    # Check required top-level fields
    for field, field_type in REQUIRED_MANIFEST_FIELDS.items():
        if field not in manifest:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(manifest[field], field_type):
            errors.append(f"Invalid type for {field}: expected {field_type.__name__}")
    
    # Validate versions array
    if "versions" in manifest:
        if not isinstance(manifest["versions"], list):
            errors.append("'versions' must be an array")
        else:
            package_name = manifest.get("name", "unknown")
            for i, version in enumerate(manifest["versions"]):
                if not isinstance(version, dict):
                    errors.append(f"Version entry {i} is not an object")
                else:
                    version_errors = validate_version(version, package_name)
                    for error in version_errors:
                        errors.append(f"Version {i} ({version.get('version', 'unknown')}): {error}")
    
    return len(errors) == 0, errors

def main():
    """Main validation function"""
    if len(sys.argv) < 2:
        print("Usage: validate_manifest.py <manifest_path>")
        sys.exit(1)
    
    manifest_path = Path(sys.argv[1])
    is_valid, errors = validate_manifest(manifest_path)
    
    if is_valid:
        print(f"✓ Manifest is valid: {manifest_path}")
        sys.exit(0)
    else:
        print(f"✗ Manifest validation failed: {manifest_path}")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()


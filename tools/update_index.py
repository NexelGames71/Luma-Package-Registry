#!/usr/bin/env python3
"""
Luma Package Registry - Update Index Script
Regenerates index.json by scanning manifests/
"""

import json
import os
import hashlib
from pathlib import Path
from datetime import datetime, timezone

def get_latest_version(versions):
    """Get the latest version from a list of version strings"""
    if not versions:
        return None
    
    # Sort versions by SemVer (simple numeric comparison)
    def version_key(v):
        try:
            parts = v.split('.')
            return tuple(int(p) for p in parts)
        except:
            return (0, 0, 0)
    
    sorted_versions = sorted(versions, key=version_key, reverse=True)
    return sorted_versions[0]

def update_index(registry_path="."):
    """Update the global index.json from manifests"""
    
    registry_path = Path(registry_path)
    manifests_dir = registry_path / "manifests"
    index_path = registry_path / "index.json"
    
    if not manifests_dir.exists():
        print(f"Error: manifests directory not found at {manifests_dir}")
        return False
    
    # Load existing index or create new
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            index = json.load(f)
        # Preserve existing revision or increment it
        if "revision" in index:
            if isinstance(index["revision"], int):
                index["revision"] += 1
            else:
                # If it's a string/hash, use a hash of current timestamp
                index["revision"] = hashlib.sha256(
                    datetime.now(timezone.utc).isoformat().encode()
                ).hexdigest()[:16]
        else:
            index["revision"] = 1
    else:
        index = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "registry": "Luma Package Registry",
            "revision": 1,
            "packages": {}
        }
    
    # Ensure packages is an object
    if "packages" not in index or not isinstance(index["packages"], dict):
        index["packages"] = {}
    
    # Scan manifests directory
    packages = {}
    for manifest_dir in manifests_dir.iterdir():
        if manifest_dir.is_dir():
            manifest_file = manifest_dir / "index.json"
            if manifest_file.exists():
                try:
                    with open(manifest_file, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                    package_name = manifest.get("name", manifest_dir.name)
                    
                    # Extract versions from manifest
                    versions_list = []
                    if "versions" in manifest and isinstance(manifest["versions"], list):
                        for version_entry in manifest["versions"]:
                            if isinstance(version_entry, dict) and "version" in version_entry:
                                versions_list.append(version_entry["version"])
                            elif isinstance(version_entry, str):
                                versions_list.append(version_entry)
                    
                    # Get latest version
                    latest = get_latest_version(versions_list)
                    
                    if latest:
                        packages[package_name] = {
                            "latest": latest,
                            "versions": sorted(versions_list, key=lambda v: tuple(int(p) for p in v.split('.')) if v.replace('.', '').isdigit() else (0, 0, 0), reverse=True)
                        }
                        print(f"Found package: {package_name} (latest: {latest})")
                    else:
                        print(f"Warning: No versions found for {package_name}")
                        
                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON in {manifest_file}: {e}")
                except Exception as e:
                    print(f"Warning: Error reading {manifest_file}: {e}")
    
    # Update packages object
    index["packages"] = packages
    
    # Write updated index
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"\nIndex updated: {len(packages)} packages found")
    print(f"Updated index.json at {index_path}")
    print(f"Revision: {index['revision']}")
    return True

if __name__ == "__main__":
    import sys
    registry_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success = update_index(registry_path)
    exit(0 if success else 1)

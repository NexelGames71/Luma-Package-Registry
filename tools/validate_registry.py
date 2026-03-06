#!/usr/bin/env python3
"""
Luma Package Registry - Full Registry Validation
Validates manifests, archive integrity, embedded package.json, and index consistency.
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from validate_manifest import (
    SEMVER_PATTERN,
    build_dependency_index,
    expected_archive_path,
    parse_semver,
    validate_manifest,
)
from validate_package import validate_package_data


def _sort_versions_desc(versions: List[str]) -> List[str]:
    def sort_key(value: str) -> Tuple[int, int, int]:
        parsed = parse_semver(value)
        if parsed is None:
            return (0, 0, 0)
        return parsed

    return sorted(versions, key=sort_key, reverse=True)


def _normalize_category(category: Optional[str], package_name: str) -> str:
    if category == "core":
        return "registry"
    if category == "third-party":
        return "assets-store"
    if category in {"registry", "assets-store"}:
        return category
    return "registry" if package_name.startswith("com.nexel.") else "assets-store"


def _extract_manifest_versions(manifest: Dict[str, Any]) -> List[str]:
    versions: List[str] = []
    for version_entry in manifest.get("versions", []):
        if isinstance(version_entry, dict) and isinstance(version_entry.get("version"), str):
            versions.append(version_entry["version"])
    return versions


def validate_archive_package_json(
    archive_path: Path,
    expected_name: str,
    expected_version: str,
) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    if not archive_path.exists():
        return False, [f"Archive not found: {archive_path}"]

    try:
        with zipfile.ZipFile(archive_path, "r") as zf:
            package_json_candidates = [
                name
                for name in zf.namelist()
                if Path(name).name == "package.json" and not name.endswith("/")
            ]
            if not package_json_candidates:
                return False, [f"{archive_path}: package.json not found in archive"]

            candidate = package_json_candidates[0]
            with zf.open(candidate, "r") as package_stream:
                package_data = json.loads(package_stream.read().decode("utf-8"))
    except zipfile.BadZipFile:
        return False, [f"{archive_path}: invalid zip archive"]
    except json.JSONDecodeError as exc:
        return False, [f"{archive_path}: package.json is not valid JSON ({exc})"]
    except UnicodeDecodeError:
        return False, [f"{archive_path}: package.json is not valid UTF-8"]
    except Exception as exc:
        return False, [f"{archive_path}: failed to read archive ({exc})"]

    is_valid, package_errors = validate_package_data(package_data, f"{archive_path}!package.json")
    errors.extend(package_errors)

    package_name = package_data.get("name")
    if package_name != expected_name:
        errors.append(f"{archive_path}: package.json name '{package_name}' does not match manifest '{expected_name}'")

    package_version = package_data.get("version")
    if package_version != expected_version:
        errors.append(
            f"{archive_path}: package.json version '{package_version}' does not match manifest '{expected_version}'"
        )

    return is_valid and not errors, errors


def validate_index_consistency(
    registry_root: Path,
    manifests_by_package: Dict[str, Dict[str, Any]],
) -> List[str]:
    errors: List[str] = []
    index_path = registry_root / "index.json"

    if not index_path.exists():
        return [f"index.json not found at {index_path}"]

    try:
        with index_path.open("r", encoding="utf-8") as handle:
            index_data = json.load(handle)
    except json.JSONDecodeError as exc:
        return [f"index.json invalid JSON: {exc}"]
    except Exception as exc:
        return [f"index.json read error: {exc}"]

    packages = index_data.get("packages")
    if not isinstance(packages, dict):
        return ["index.json: 'packages' must be an object"]

    registry_packages = packages.get("registry")
    assets_store_packages = packages.get("assets-store")
    if not isinstance(registry_packages, dict) or not isinstance(assets_store_packages, dict):
        errors.append("index.json: packages.registry and packages.assets-store must be objects")
        return errors

    index_union = {}
    index_union.update({k: ("registry", v) for k, v in registry_packages.items()})
    index_union.update({k: ("assets-store", v) for k, v in assets_store_packages.items()})

    for package_name, manifest in manifests_by_package.items():
        versions = _sort_versions_desc(_extract_manifest_versions(manifest))
        if not versions:
            errors.append(f"{package_name}: manifest has no versions")
            continue

        latest = versions[0]
        latest_entry = next(
            (
                entry
                for entry in manifest.get("versions", [])
                if isinstance(entry, dict) and entry.get("version") == latest
            ),
            None,
        )
        manifest_category = _normalize_category(
            latest_entry.get("category") if isinstance(latest_entry, dict) else None,
            package_name,
        )

        if package_name not in index_union:
            errors.append(f"index.json: missing package '{package_name}'")
            continue

        indexed_category, indexed_entry = index_union[package_name]
        if indexed_category != manifest_category:
            errors.append(
                f"index.json: package '{package_name}' in wrong category "
                f"('{indexed_category}' vs manifest '{manifest_category}')"
            )

        if not isinstance(indexed_entry, dict):
            errors.append(f"index.json: package '{package_name}' entry must be an object")
            continue

        indexed_latest = indexed_entry.get("latest")
        if indexed_latest != latest:
            errors.append(
                f"index.json: package '{package_name}' latest mismatch "
                f"(index '{indexed_latest}' vs manifest '{latest}')"
            )

        indexed_versions = indexed_entry.get("versions")
        if indexed_versions != versions:
            errors.append(
                f"index.json: package '{package_name}' versions mismatch "
                f"(index {indexed_versions} vs manifest {versions})"
            )

    manifest_package_names = set(manifests_by_package.keys())
    for indexed_name in index_union:
        if indexed_name not in manifest_package_names:
            errors.append(f"index.json: package '{indexed_name}' has no matching manifest")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the entire Luma package registry")
    parser.add_argument(
        "registry_root",
        nargs="?",
        default=".",
        help="Path to Luma-Package-Registry root (default: current directory)",
    )
    args = parser.parse_args()

    registry_root = Path(args.registry_root).resolve()
    manifests_root = registry_root / "manifests"
    if not manifests_root.exists():
        print(f"[FAIL] manifests directory not found: {manifests_root}")
        sys.exit(1)

    manifest_paths = sorted(manifests_root.glob("*/index.json"))
    if not manifest_paths:
        print("[FAIL] no manifest files found under manifests/*/index.json")
        sys.exit(1)

    dependency_versions = build_dependency_index(registry_root)
    manifests_by_package: Dict[str, Dict[str, Any]] = {}
    all_errors: List[str] = []

    for manifest_path in manifest_paths:
        try:
            with manifest_path.open("r", encoding="utf-8") as handle:
                manifest_data = json.load(handle)
        except Exception as exc:
            all_errors.append(f"{manifest_path}: failed to load JSON ({exc})")
            continue

        package_name = manifest_data.get("name")
        if isinstance(package_name, str):
            manifests_by_package[package_name] = manifest_data

        is_valid, manifest_errors = validate_manifest(
            manifest_path,
            registry_root=registry_root,
            dependency_versions=dependency_versions,
        )
        if not is_valid:
            all_errors.extend(f"{manifest_path}: {error}" for error in manifest_errors)

        if not isinstance(package_name, str):
            continue

        for version_entry in manifest_data.get("versions", []):
            if not isinstance(version_entry, dict):
                continue
            version = version_entry.get("version")
            if not isinstance(version, str) or SEMVER_PATTERN.fullmatch(version) is None:
                continue
            archive_path = expected_archive_path(registry_root, package_name, version)
            archive_ok, archive_errors = validate_archive_package_json(archive_path, package_name, version)
            if not archive_ok:
                all_errors.extend(archive_errors)

    all_errors.extend(validate_index_consistency(registry_root, manifests_by_package))

    if all_errors:
        print("[FAIL] Registry validation failed:")
        for error in all_errors:
            print(f"  - {error}")
        sys.exit(1)

    print(f"[OK] Registry validation passed ({len(manifest_paths)} manifests)")
    sys.exit(0)


if __name__ == "__main__":
    main()

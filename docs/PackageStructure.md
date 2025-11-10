# Package Structure

This document describes the required structure for packages in the Luma Package Registry.

## Directory Structure

Each package must follow this directory structure:

```
<package-name>-<version>.zip
├── package.json          # Package metadata (required)
├── Runtime/              # Runtime implementation files
├── Editor/               # Editor-specific files (optional)
├── Docs/                 # Documentation files (optional)
└── Samples/              # Example code and samples (optional)
```

## package.json

The `package.json` file is required and must conform to the [JSON Schema](https://schemas.nexel.games/lpm/package.schema.json).

### Required Fields

- **name** (string): Unique package identifier following reverse-domain notation
  - Pattern: `^[a-z0-9]+(\.[a-z0-9]+)+$`
  - Example: `com.nexel.core.reflection`
- **version** (string): Package version following SemVer
  - Pattern: `^\d+\.\d+\.\d+$`
  - Example: `1.0.0`, `2.1.3`, `0.3.0`
  - Note: Pre-release and build metadata are not allowed in the version field
- **displayName** (string): Human-readable package name shown in the editor
- **description** (string): Brief description of the package
- **engine** (object): Luma Engine version compatibility
  - Required field: **luma** (string): Version constraint pattern
    - Pattern: `^(>=|<=|>|<|=|\^|~)?\d+\.\d+\.\d+`
    - Examples: `>=1.0.0`, `^1.0.0`, `~2.1.0`, `=1.0.0`, `1.0.0`

### Optional Fields

- **author** (object or string): Package author information
  - Object format:
    ```json
    {
      "name": "Nexel Games",
      "url": "https://nexel.games"
    }
    ```
  - `name` (required): Author name
  - `url` (optional): Author website (must be valid HTTP/HTTPS URL)
  - String format: Simple string (e.g., `"Nexel Games"`)
- **license** (string): License identifier
- **homepage** (string): Package homepage (must be valid HTTP/HTTPS URL)
- **keywords** (array): Searchable keywords for the package
  - Example: `["reflection", "core", "runtime"]`
- **category** (string): Package category
  - Values: `"registry"` or `"assets-store"`
  - Default: `"assets-store"` if not specified
  - `"registry"`: Official Luma Engine packages maintained by Nexel Games (e.g., AI, Landscape, Luminite, Animation)
  - `"assets-store"`: Packages created by community developers
- **dependencies** (object): Package dependencies
  - Format: `{ "package-name": "version" }`
  - Package names must follow reverse-domain notation
  - Example: `{ "com.nexel.core.reflection": "1.0.0" }`
- **samples** (array): Sample code and examples
  - Each sample must have:
    - **displayName** (string): Sample name
    - **path** (string): Relative path to sample directory
  - Example:
    ```json
    [
      {
        "displayName": "Basic Example",
        "path": "Samples/Basic"
      }
    ]
    ```
- **postInstall** (array): Scripts to run after installation
  - Array of relative script paths
  - Example: `["Scripts/postinstall.js"]`

### Example package.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "name": "com.nexel.core.reflection",
  "version": "1.0.0",
  "displayName": "Core Reflection",
  "description": "Base reflection system for Luma Engine. Provides runtime type information and reflection capabilities.",
  "author": {
    "name": "Nexel Games",
    "url": "https://nexel.games"
  },
  "license": "MIT",
  "homepage": "https://github.com/nexelgames/luma-core-reflection",
  "engine": {
    "luma": ">=1.0.0"
  },
  "dependencies": {},
  "keywords": [
    "reflection",
    "core",
    "runtime",
    "type-info"
  ],
  "category": "registry",
  "samples": [
    {
      "displayName": "Basic Reflection Example",
      "path": "Samples/Basic"
    }
  ]
}
```

## Directory Contents

### Runtime/

Contains runtime implementation files that are used in the final application. This typically includes:
- Compiled libraries
- Scripts
- Assets
- Configuration files

### Editor/

Contains editor-specific files that are only used during development. This typically includes:
- Editor extensions
- Custom inspectors
- Editor tools
- UI definitions

### Docs/

Contains documentation for the package. This typically includes:
- API documentation
- Usage guides
- Tutorials
- Examples

### Samples/

Contains example code and samples demonstrating how to use the package. This typically includes:
- Sample scenes
- Example scripts
- Tutorial projects
- Reference implementations

## Package Naming

Package names must follow reverse domain notation:
- Format: `com.<organization>.<package-name>`
- Pattern: `^[a-z0-9]+(\.[a-z0-9]+)+$`
- Example: `com.nexel.core.reflection`
- Must be lowercase
- Use dots (`.`) to separate segments
- Use alphanumeric characters only

## Version Format

Package versions must follow [Semantic Versioning](VersioningPolicy.md) (SemVer):
- Format: `MAJOR.MINOR.PATCH`
- Pattern: `^\d+\.\d+\.\d+$`
- Example: `1.0.0`, `2.1.3`, `0.3.0`
- **Note**: Pre-release versions (e.g., `1.0.0-alpha.1`) and build metadata (e.g., `1.0.0+20240101`) are not allowed in the version field

## Engine Version Constraints

The `engine.luma` field supports version constraints:
- `>=1.0.0` - Greater than or equal to
- `<=2.0.0` - Less than or equal to
- `>1.0.0` - Greater than
- `<2.0.0` - Less than
- `=1.0.0` - Exact version
- `^1.0.0` - Compatible with (>=1.0.0 <2.0.0)
- `~1.0.0` - Approximately equivalent (>=1.0.0 <1.1.0)
- `1.0.0` - Exact version (shorthand for `=1.0.0`)

## Zip Archive

Packages must be distributed as ZIP archives:
- Filename format: `<package-name>-<version>.zip`
- Example: `com.nexel.core.reflection-1.0.0.zip`
- Contents should be the package directory structure (not wrapped in an extra folder)
- Use standard ZIP compression (DEFLATE)

## Validation

All packages are validated before being accepted into the registry:
- Structure compliance
- `package.json` schema validation (using JSON Schema)
- SHA256 checksum verification
- Dependency resolution

Use the `validate_package.py` tool to validate your package before submission.

See [Security.md](Security.md) for more information on package integrity.

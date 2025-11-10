# Luma Package Registry

Official package registry for [Luma Engine](https://github.com/NexelGames71) maintained by Nexel Games.

**Repository:** https://github.com/NexelGames71/Luma-Package-Registry.git

## What is the Luma Package Registry?

The Luma Package Registry is the central repository for discovering, distributing, and managing packages for the Luma Engine ecosystem. It provides a standardized way to:

- **Discover packages** - Browse available packages for Luma Engine
- **Install packages** - Easily add packages to your projects
- **Distribute packages** - Share your own packages with the community
- **Manage dependencies** - Handle package dependencies automatically

## Quick Start

### For Package Users

1. **Browse packages** in the [index.json](index.json) file
2. **Download packages** from the `packages/` directory
3. **Install packages** into your Luma Engine project

### For Package Authors

1. **Prepare your package** following the [Package Structure guide](docs/PackageStructure.md)
2. **Use the packaging tool** to create your package:
   ```powershell
   .\tools\pack.ps1 -PackagePath "path/to/your/package" -Version "1.0.0"
   ```
3. **Submit a Pull Request** with your package files

## Repository Structure

```
Luma-Package-Registry/
├── index.json                    # Global package index (all available packages)
├── manifests/                    # Package manifests (version history)
│   └── <package-name>/
│       └── index.json           # Detailed manifest for each package
├── packages/                     # Package archives (ZIP files)
│   └── <package-name>/
│       └── <version>/
│           └── <package>-<version>.zip
├── tools/                        # Automation and packaging tools
│   ├── pack.ps1                 # Package creation script
│   ├── update_index.py          # Index regeneration tool
│   ├── validate_manifest.py    # Manifest validation
│   └── validate_package.py     # Package validation
├── docs/                         # Documentation
│   ├── PackageStructure.md      # Package format specifications
│   ├── PublishingGuide.md       # How to publish packages
│   ├── VersioningPolicy.md      # Semantic versioning rules
│   └── Security.md              # Security and integrity checks
└── .github/
    └── workflows/                # GitHub Actions automation
        └── validate-and-update.yml
```

## Package Categories

The registry supports two types of packages:

### Luma Core Packages

Official packages maintained by Nexel Games that provide essential functionality for Luma Engine. These include:

- **AI** - Artificial intelligence and behavior systems
- **Landscape** - Landscape generation and editing tools
- **Luminite** - Advanced rendering and lighting systems
- **Animation** - Animation and rigging tools
- **Core** - Core engine functionality (reflection, utilities, etc.)
- **Terrain** - Terrain generation and editing

Core packages are identified by the `"category": "core"` field in their `package.json` and typically use the `com.nexel.*` naming convention.

### Third-Party Packages

Community-created packages developed by independent developers. These packages extend Luma Engine with additional functionality, tools, and integrations.

Third-party packages are identified by the `"category": "third-party"` field in their `package.json` (or default to third-party if not specified).

## Available Packages

Currently available packages:

**Core Packages:**
- `com.nexel.core.reflection` - Base reflection system for Luma Engine
- `com.nexel.render.luminite` - Luminite Environment rendering tools
- `com.nexel.terrain.core` - Terrain node and editor

**Third-Party Packages:**
- `com.nexel.lighting.dynamic` - Dynamic lighting system (test package)

See [index.json](index.json) for the complete list of all available packages organized by category.

## Package Format

Each package in the registry follows a standardized structure:

```
<package-name>-<version>.zip
├── package.json          # Package metadata (required)
├── Runtime/              # Runtime implementation files
├── Editor/               # Editor-specific files (optional)
├── Docs/                 # Documentation (optional)
└── Samples/              # Example code (optional)
```

The `package.json` file must conform to the [package schema](https://schemas.nexel.games/lpm/package.schema.json).

## Contributing

### Requirements

- Package must follow the [Package Structure](docs/PackageStructure.md) guidelines
- Package must include a valid `package.json` with all required fields
- Package must pass validation checks (see [Security.md](docs/Security.md))
- Package must follow [Semantic Versioning](docs/VersioningPolicy.md)

### Publishing Process

1. **Create your package** following the structure guidelines
2. **Validate your package**:
   ```powershell
   python tools\validate_package.py path\to\package\package.json
   ```
3. **Package your files**:
   ```powershell
   .\tools\pack.ps1 -PackagePath "path/to/your/package" -Version "1.0.0"
   ```
4. **Update the index**:
   ```bash
   python tools\update_index.py
   ```
5. **Submit a Pull Request** with:
   - Your package ZIP file in `packages/<package-name>/<version>/`
   - Updated manifest in `manifests/<package-name>/index.json`
   - Updated global index in `index.json`

For detailed instructions, see the [Publishing Guide](docs/PublishingGuide.md).

## Documentation

- **[Package Structure](docs/PackageStructure.md)** - Complete guide to package format and requirements
- **[Publishing Guide](docs/PublishingGuide.md)** - Step-by-step instructions for publishing packages
- **[Versioning Policy](docs/VersioningPolicy.md)** - Semantic versioning rules and best practices
- **[Security](docs/Security.md)** - Package integrity, checksums, and security measures

## Automation Tools

The registry includes several automation tools:

### Packaging Tool (`pack.ps1`)
Creates package ZIP archives, computes SHA256 checksums, and updates manifests automatically.

**Usage:**
```powershell
.\tools\pack.ps1 -PackagePath "path/to/package" -Version "1.0.0"
```

### Index Update Tool (`update_index.py`)
Regenerates the global `index.json` by scanning all manifests.

**Usage:**
```bash
python tools\update_index.py
```

### Validation Tools
- `validate_package.py` - Validates `package.json` against the schema
- `validate_manifest.py` - Validates manifest files

## GitHub Actions

The repository includes automated CI/CD workflows:

- **Package Validation** - Validates all packages and manifests on Pull Requests
- **Index Auto-Update** - Automatically updates `index.json` when changes are merged

## Security

All packages include SHA256 checksums for integrity verification. See [Security.md](docs/Security.md) for detailed information about:

- Package integrity verification
- Checksum validation
- Dependency security
- Best practices

## License

Packages in this registry may have individual licenses. Please refer to each package's documentation for licensing information.

The registry itself is maintained by Nexel Games.

## Support

- **Issues**: Open an issue on [GitHub](https://github.com/NexelGames71/Luma-Package-Registry/issues)
- **Questions**: Check the documentation in the `docs/` folder
- **Contributions**: Submit a Pull Request following the [Publishing Guide](docs/PublishingGuide.md)

## Links

- **Repository**: https://github.com/NexelGames71/Luma-Package-Registry
- **Package Schema**: https://schemas.nexel.games/lpm/package.schema.json
- **Index Schema**: https://schemas.nexel.games/lpm/index.schema.json

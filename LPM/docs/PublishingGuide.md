# Publishing Guide

This guide explains how to publish a new package or update an existing package in the Luma Package Registry.

## Prerequisites

- A GitHub account
- Your package follows the [Package Structure](PackageStructure.md)
- Your package adheres to [Semantic Versioning](VersioningPolicy.md)

## Publishing a New Package

### Step 1: Prepare Your Package

1. **Create the package structure** following the [Package Structure](PackageStructure.md) guidelines
2. **Create a valid `package.json`** with all required fields
3. **Organize your files** into `Runtime/`, `Editor/`, `Docs/`, and `Samples/` directories as needed

### Step 2: Package Your Files

Use the packaging tool to create your package archive:

**Windows (PowerShell):**
```powershell
.\tools\pack.ps1 -PackagePath "path/to/your/package" -Version "1.0.0"
```

**Manual Process:**
1. Create a ZIP archive of your package directory
2. Name it: `<package-name>-<version>.zip`
3. Compute the SHA256 checksum
4. Create or update the manifest file

### Step 3: Update the Manifest

Create or update the manifest file at:
```
manifests/<package-name>/index.json
```

The manifest should include:
- Package name
- All versions (including the new one)
- SHA256 checksum
- File size
- Download URL
- Dependencies
- Engine version compatibility
- Description
- Publication date

### Step 4: Update the Global Index

Run the index update script:
```bash
python tools/update_index.py
```

Or manually add your package to `index.json`:
```json
{
  "packages": {
    "com.nexel.yourpackage": {
      "latest": "1.0.0",
      "versions": ["1.0.0"]
    }
  }
}
```

### Step 5: Submit a Pull Request

1. **Fork the repository** or create a new branch
2. **Add your files**:
   - `packages/<package-name>/<version>/<package-name>-<version>.zip`
   - `manifests/<package-name>/index.json`
   - Updated `index.json`
3. **Commit your changes**:
   ```bash
   git add packages/<package-name>/
   git add manifests/<package-name>/
   git add index.json
   git commit -m "Add package <package-name> version <version>"
   ```
4. **Push to your fork** and create a Pull Request
5. **Wait for validation** - GitHub Actions will automatically validate your package

## Updating an Existing Package

### Step 1: Increment Version

Follow [Semantic Versioning](VersioningPolicy.md) to determine the new version number.

### Step 2: Package New Version

Follow the same packaging process as for a new package, using the new version number.

### Step 3: Update Manifest

Add the new version entry to the existing manifest:
```
manifests/<package-name>/index.json
```

The new version entry should be added to the `versions` array. Versions are automatically sorted by the packaging tool.

### Step 4: Submit Pull Request

Follow the same PR process as for new packages.

## Package Validation

Your package will be automatically validated when you submit a Pull Request:

1. **Structure Validation**: Checks that the package follows the required structure
2. **Manifest Validation**: Validates the manifest JSON schema
3. **Checksum Verification**: Verifies that the SHA256 checksum matches the package file
4. **Dependency Resolution**: Checks that all dependencies are available in the registry

If validation fails, the PR will be marked as failed and you'll receive error messages.

## Best Practices

### Before Publishing

- [ ] Test your package thoroughly
- [ ] Verify all dependencies are available in the registry
- [ ] Ensure your package follows the structure guidelines
- [ ] Validate your `package.json` manually
- [ ] Test the package in a clean Luma Engine installation

### Versioning

- [ ] Use Semantic Versioning consistently
- [ ] Document breaking changes in patch notes
- [ ] Don't republish existing versions (use a new version instead)

### Documentation

- [ ] Include clear documentation in the `Docs/` folder
- [ ] Provide example code in the `Samples/` folder
- [ ] Write a clear description in `package.json`
- [ ] Add relevant keywords for discoverability

### Security

- [ ] Ensure your package doesn't contain malicious code
- [ ] Verify checksums are correct
- [ ] Review dependencies for security vulnerabilities

## Automated Publishing

After your PR is merged to `main`, the following happens automatically:

1. **Index Update**: The global `index.json` is automatically updated
2. **Artifact Publishing**: Your package is available via raw.githubusercontent.com
3. **Registry Update**: The registry is now serving your package

## Troubleshooting

### Package Validation Fails

- Check that your `package.json` has all required fields
- Verify the package structure matches the guidelines
- Ensure the SHA256 checksum is correct
- Check that all dependencies exist in the registry

### Manifest Validation Fails

- Verify the JSON syntax is correct
- Check that all required fields are present
- Ensure version numbers follow SemVer
- Verify checksum format is correct (64 hex characters)

### Index Update Fails

- Check that the package name is added to `index.json`
- Verify the package name matches the manifest
- Ensure there are no duplicate package names

## Support

If you encounter issues or have questions:
- Open an issue in the repository
- Check existing documentation
- Review similar packages for examples


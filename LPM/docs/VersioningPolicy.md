# Versioning Policy

The Luma Package Registry uses [Semantic Versioning (SemVer)](https://semver.org/) for all packages.

## Semantic Versioning

Version numbers follow the format: `MAJOR.MINOR.PATCH`

- **MAJOR**: Increment for incompatible API changes
- **MINOR**: Increment when adding functionality in a backward-compatible manner
- **PATCH**: Increment for backward-compatible bug fixes

### Examples

- `1.0.0` - Initial release
- `1.0.1` - Bug fix (patch)
- `1.1.0` - New feature, backward compatible (minor)
- `2.0.0` - Breaking changes (major)

## Version Pattern

The version field in `package.json` must match the pattern: `^\d+\.\d+\.\d+$`
- Only numeric versions are allowed (e.g., `1.0.0`)
- Pre-release versions (e.g., `1.0.0-alpha.1`) are **not allowed** in the version field
- Build metadata (e.g., `1.0.0+20240101`) is **not allowed** in the version field

**Note**: While SemVer allows pre-release and build metadata, the Luma Package Registry requires strict numeric versioning in the `package.json` version field for consistency and compatibility.

## Version Constraints

When specifying dependencies, you can use version constraints:

### Exact Version
```
"com.nexel.core.reflection": "1.0.0"
```
Matches exactly version `1.0.0`.

### Version Range
```
"com.nexel.core.reflection": "^1.0.0"
```
Matches any version compatible with `1.0.0` (>= 1.0.0 < 2.0.0).

### Greater Than or Equal
```
"com.nexel.core.reflection": ">=1.0.0"
```
Matches any version >= 1.0.0.

### Less Than
```
"com.nexel.core.reflection": "<2.0.0"
```
Matches any version < 2.0.0.

### Range
```
"com.nexel.core.reflection": ">=1.0.0 <2.0.0"
```
Matches any version >= 1.0.0 and < 2.0.0.

## Versioning Guidelines

### When to Bump MAJOR

- Breaking API changes
- Removing functionality
- Changing behavior in a way that breaks existing code
- Major architectural changes

### When to Bump MINOR

- Adding new features
- Adding new APIs (backward compatible)
- Deprecating functionality (not removing)
- Performance improvements

### When to Bump PATCH

- Bug fixes
- Security patches
- Documentation updates
- Minor improvements that don't change behavior

## Version History

Once a version is published, it should not be changed or republished. Instead:

- **Fix bugs**: Publish a new patch version (`1.0.0` → `1.0.1`)
- **Add features**: Publish a new minor version (`1.0.0` → `1.1.0`)
- **Breaking changes**: Publish a new major version (`1.0.0` → `2.0.0`)

## Version Comparison

Versions are compared numerically:
- `1.0.0` < `1.0.1` < `1.1.0` < `2.0.0`

## Engine Version Compatibility

Packages specify engine version compatibility in `package.json` using the `engine` field:

```json
{
  "engine": {
    "luma": ">=1.0.0"
  }
}
```

The `engine.luma` field supports version constraints:
- `>=1.0.0` - Greater than or equal to
- `<=2.0.0` - Less than or equal to
- `>1.0.0` - Greater than
- `<2.0.0` - Less than
- `=1.0.0` - Exact version
- `^1.0.0` - Compatible with (>=1.0.0 <2.0.0)
- `~1.0.0` - Approximately equivalent (>=1.0.0 <1.1.0)
- `1.0.0` - Exact version (shorthand for `=1.0.0`)

The registry uses SemVer comparison to determine compatibility.

## Best Practices

1. **Start at 1.0.0**: Don't use `0.x.x` unless you're in early development
2. **Be consistent**: Use the same versioning strategy across all your packages
3. **Document changes**: Include a changelog with version releases
4. **Don't skip versions**: Don't jump from `1.0.0` to `3.0.0` without `2.0.0`
5. **Pre-release for testing**: Use pre-release versions for testing before official releases

## Examples

### Valid Versions
- `1.0.0`
- `1.2.3`
- `0.3.0` (early development)
- `2.0.0`

### Invalid Versions
- `1.0` (missing patch)
- `v1.0.0` (no prefix)
- `1.0.0.0` (too many segments)
- `latest` (not a version number)
- `1.0.0-alpha.1` (pre-release not allowed)
- `1.0.0+build.123` (build metadata not allowed)
- `1.0.0-SNAPSHOT` (invalid format)


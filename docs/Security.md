# Security

This document describes security measures and best practices for the Luma Package Registry.

## Package Integrity

### SHA256 Checksums

All packages in the registry include SHA256 checksums to ensure integrity:

- **Purpose**: Verify that packages haven't been tampered with
- **Location**: Stored in manifest files (`manifests/<package>/index.json`)
- **Format**: 64 hexadecimal characters (lowercase)
- **Verification**: Automatically verified during package validation

### Checksum Verification

When downloading a package, you should verify the checksum:

**Python:**
```python
import hashlib

with open('package.zip', 'rb') as f:
    sha256 = hashlib.sha256(f.read()).hexdigest()
    
if sha256 != expected_checksum:
    raise ValueError("Checksum mismatch!")
```

**PowerShell:**
```powershell
$hash = (Get-FileHash -Path "package.zip" -Algorithm SHA256).Hash.ToLower()
if ($hash -ne $expectedChecksum) {
    throw "Checksum mismatch!"
}
```

## Package Signing (Optional)

While not currently required, package signing is recommended for sensitive packages:

- **GPG Signatures**: Packages can be signed with GPG keys
- **Certificate Signing**: Packages can be signed with code signing certificates
- **Verification**: End users can verify signatures before installation

### Future Implementation

We plan to add optional package signing support:
- GPG signature verification
- Certificate-based signing
- Signature validation in automation tools

## Dependency Security

### Dependency Verification

Before publishing, verify that your dependencies:
- Come from trusted sources
- Are up-to-date with security patches
- Don't introduce security vulnerabilities
- Are compatible with your package version

### Vulnerability Scanning

We recommend:
- Regularly scanning dependencies for known vulnerabilities
- Using tools like `npm audit` or `pip-audit` (if applicable)
- Keeping dependencies updated
- Reviewing dependency licenses

## Repository Security

### Access Control

- **Read Access**: Public (all packages are publicly readable)
- **Write Access**: Controlled via Pull Requests
- **Maintainer Access**: Limited to Nexel Games maintainers

### Pull Request Review

All packages are reviewed before merging:
- Structure validation
- Manifest validation
- Checksum verification
- Security review (for sensitive packages)

### Automated Validation

GitHub Actions automatically validate:
- Package structure
- Manifest schema
- Checksum integrity
- Dependency resolution

## Best Practices

### For Package Authors

1. **Don't include sensitive data**: Remove API keys, passwords, and secrets
2. **Review dependencies**: Ensure dependencies are secure and up-to-date
3. **Use checksums**: Always include correct SHA256 checksums
4. **Document changes**: Include security-related changes in changelogs
5. **Report vulnerabilities**: Report security issues to maintainers immediately

### For Package Consumers

1. **Verify checksums**: Always verify package checksums before installation
2. **Review packages**: Review package contents before using in production
3. **Update regularly**: Keep packages updated to latest secure versions
4. **Check dependencies**: Review package dependencies for vulnerabilities
5. **Report issues**: Report security vulnerabilities to package authors and maintainers

## Security Reporting

### Reporting Vulnerabilities

If you discover a security vulnerability:

1. **Don't open a public issue**: Security vulnerabilities should be reported privately
2. **Contact maintainers**: Email the maintainers directly
3. **Provide details**: Include:
   - Package name and version
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
4. **Wait for response**: Allow maintainers time to address the issue

### Response Process

1. **Acknowledge**: Maintainers will acknowledge receipt within 48 hours
2. **Investigate**: Security issues are prioritized for investigation
3. **Fix**: A fix will be developed and tested
4. **Disclosure**: Vulnerabilities will be disclosed after a fix is available
5. **Update**: Affected packages will be updated or deprecated

## Package Validation

### Structure Validation

Packages are validated for:
- Required directory structure
- Required files (package.json)
- Valid file types
- No malicious files

### Content Validation

Packages are checked for:
- Valid package.json
- Correct version format
- Valid dependencies
- Engine version compatibility

### Integrity Validation

Packages are verified for:
- SHA256 checksum match
- File size consistency
- Archive integrity
- No corruption

## Security Checklist

Before publishing a package:

- [ ] No hardcoded secrets or API keys
- [ ] Dependencies are up-to-date and secure
- [ ] SHA256 checksum is correct
- [ ] Package structure is valid
- [ ] No malicious code or files
- [ ] Documentation is accurate
- [ ] License is appropriate
- [ ] Dependencies are documented

## Future Security Enhancements

Planned security improvements:

1. **Package Signing**: GPG and certificate-based signing
2. **Vulnerability Scanning**: Automated dependency scanning
3. **Security Advisories**: Public security advisory system
4. **Access Logs**: Audit logging for package access
5. **Rate Limiting**: Protection against abuse
6. **Content Scanning**: Automated malware scanning

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [SemVer Security](https://semver.org/#spec-item-11)
- [Package Security Best Practices](https://snyk.io/blog/10-npm-security-best-practices/)


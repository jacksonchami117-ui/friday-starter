# Security Policy

## Reporting Security Vulnerabilities

We take the security of the friday-starter project seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### How to Report a Security Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please send an email to [SECURITY_CONTACT_EMAIL_PLACEHOLDER] with the following information:

- A description of the vulnerability
- Steps to reproduce the issue
- Possible impact of the vulnerability
- Any suggested remediation
- Your contact information (optional, but helps us follow up)

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

### Security Response Process

1. **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
2. **Investigation**: We will investigate and validate the reported vulnerability
3. **Resolution**: We will work to resolve the issue and coordinate disclosure
4. **Publication**: After the issue is resolved, we may publish a security advisory

### Supported Versions

Please ensure you are using a supported version when reporting vulnerabilities:

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

### Security Best Practices

When deploying friday-starter, please follow these security best practices:

#### Environment Variables
- Never commit sensitive data like API keys, passwords, or tokens to the repository
- Use strong, unique values for `SECRET_KEY` and `ADMIN_PASSWORD`
- Regularly rotate secrets and API keys

#### Database Security
- Use strong database passwords
- Enable SSL/TLS for database connections in production
- Regularly backup your database
- Limit database access to necessary services only

#### File Upload Security
- Validate all file uploads
- Implement file size limits
- Scan uploaded files for malware when possible
- Store uploads in a secure location with appropriate permissions

#### Network Security
- Use HTTPS in production
- Implement proper CORS policies
- Use secure headers (HSTS, CSP, etc.)
- Regularly update dependencies

#### Infrastructure Security
- Keep your operating system and software up to date
- Use firewalls to limit access to necessary ports
- Implement proper logging and monitoring
- Regular security audits and vulnerability scans

### Vulnerability Disclosure Policy

We believe in responsible disclosure and will work with security researchers to:

- Acknowledge your contribution to improving our security
- Provide reasonable time to fix issues before public disclosure
- Keep you informed of our progress
- Credit you in our security advisories (if desired)

### Contact Information

For security-related inquiries, please contact:
- **Email**: [SECURITY_CONTACT_EMAIL_PLACEHOLDER]
- **Response Time**: Within 48 hours
- **GPG Key**: [Optional - GPG_KEY_ID_PLACEHOLDER]

### Thank You

We appreciate your efforts to responsibly disclose security vulnerabilities and help us keep friday-starter secure for everyone.

---

**Last Updated**: December 2024
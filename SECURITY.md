# Security Policy

**ClearGlass Inc.** takes the security of our projects seriously. This policy outlines how to report vulnerabilities in the **Opal-Koboi** repository and our commitment to responsible disclosure.

## Supported Versions

We actively maintain the following versions:

| Version | Supported          |
|---------|--------------------|
| main    | :white_check_mark: |
| v1.x    | :white_check_mark: |
| < v1.0  | :x:                |

## Reporting a Vulnerability

**Please do not open public issues for security vulnerabilities.**

### Preferred Method (Recommended)
Use GitHub’s **private vulnerability reporting**:
1. Go to the repository **Security** tab → **Report a vulnerability**
2. Or email: **security@clearglassinc.com** (PGP key available on request)

### What to Include
- Clear description of the vulnerability
- Steps to reproduce (including environment details)
- Potential impact and severity
- Any proof-of-concept or exploit code (if safe)
- Your contact information for follow-up

### Our Commitment
- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 7 business days
- **Resolution timeline**: Critical issues targeted within 14 days; others within 30 days
- **Coordinated disclosure**: We will work with you on a mutually agreed publication date
- **Credit**: We will acknowledge reporters (unless you prefer to remain anonymous)

## Scope

**In scope**:
- Code in this repository
- Build / dependency issues that lead to exploitable conditions
- Misconfigurations in documented deployment paths

**Out of scope**:
- Social engineering or physical attacks
- Attacks against ClearGlass infrastructure or employees
- Issues in third-party services we do not control
- Denial of service without clear security impact
- Self-XSS or low-impact findings

## Safe Harbor

We support good-faith security research. If you follow this policy:
- We will not pursue legal action
- We will not suspend or terminate your account
- We will work with you to understand and resolve the issue

## Contact

- Security reports: security@clearglassinc.com
- General inquiries: info@clearglassinc.com
- Company: ClearGlass Inc., Burlington, Ontario, Canada

Thank you for helping keep Canadian public-sector infrastructure and our open-source tools secure.

— ClearGlass Security Team

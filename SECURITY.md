# Security Policy

## Reporting Vulnerabilities
Report security issues to accubotai@gmail.com.

## Security Requirements
- All SQL queries use parameterized statements
- No credentials in source code — use environment variables
- API input validation on all endpoints
- CORS restricted to known origins
- Dependencies pinned and audited

## Sensitive Data
- BC Assessment data may contain personal information — check licence terms
- MLS/IDX data has strict display rules — see PROJECT.md Section 5.2
- Never log PII (owner names, addresses) at DEBUG level in production

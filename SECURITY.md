# Security Policy

## Supported Versions

This is a learning and portfolio project. The `main` branch is the only maintained version.

| Version | Supported |
| --- | --- |
| main | Yes |
| older commits | No |

## Reporting a Vulnerability

If you find a security issue, open a GitHub issue with `[Security]` in the title and describe the problem clearly. Do not include live credentials, API keys, tokens, or private account information in the issue body.

Helpful details include:

- What file or behavior is affected.
- Steps to reproduce the issue.
- Expected behavior versus actual behavior.
- Any safe example data needed to understand the problem.

## Secrets and API Keys

This project uses external movie APIs. Real API keys should be provided through local environment variables such as `TMDB_API_KEY` and `OMDB_API_KEY`.

Do not commit `.env` files, tokens, or API keys to the repository. If a key is accidentally committed, rotate it in the provider dashboard and update your local environment with the new value.

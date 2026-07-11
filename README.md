# Python Security & Automation Scripts

Example Python scripts demonstrating API-based automation and tooling for Azure, Microsoft Graph, and general IT operations.

## Scripts

| File | Purpose |
|---|---|
| [`defender_vulnerability_report.py`](./defender_vulnerability_report.py) | Fetches high-severity vulnerabilities from the Microsoft Defender for Endpoint API, filters by exploit availability, and exports a prioritized CSV report |
| [`entra_stale_accounts_report.py`](./entra_stale_accounts_report.py) | Queries Microsoft Graph for user accounts with no recent sign-in activity and exports a CSV report for access review purposes |
| [`log_file_analyzer.py`](./log_file_analyzer.py) | Parses a text-based log file and summarizes log levels, time range, and the most frequent error messages |
| [`api_health_checker.py`](./api_health_checker.py) | Checks a list of HTTP endpoints for availability and response time, flagging down or slow-responding services |

## Requirements

```
pip install requests msal
```

## Setup

Scripts that use Microsoft Graph or Defender APIs authenticate via `msal` using Entra ID app registration credentials. Set these as environment variables - never hardcode credentials in scripts:

```bash
export TENANT_ID="<your-tenant-id>"
export CLIENT_ID="<your-client-id>"
export CLIENT_SECRET="<your-client-secret>"
```

`log_file_analyzer.py` and `api_health_checker.py` have no authentication requirements and can be run directly.

## Note

These are simplified examples for demonstration purposes. Production usage should include additional error handling, pagination for large result sets (where not already included), and rate-limit handling per the relevant API's guidelines.

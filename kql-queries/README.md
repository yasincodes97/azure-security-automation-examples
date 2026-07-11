# KQL Queries — Microsoft Sentinel & Defender XDR

Example KQL (Kusto Query Language) queries for threat hunting, advanced hunting, and security alert triage in Microsoft Sentinel and Microsoft Defender XDR.

## Queries

| File | Purpose |
|---|---|
| [`suspicious-signins.kql`](./suspicious-signins.kql) | Detects sign-ins from unusual locations or impossible travel patterns |
| [`high-severity-vulnerabilities.kql`](./high-severity-vulnerabilities.kql) | Surfaces high/critical CVSS-scored vulnerabilities from Defender for Endpoint with exploit availability |
| [`failed-logic-app-runs.kql`](./failed-logic-app-runs.kql) | Monitors Log Analytics for failed automation workflow runs |

## Notes on Style

- Time filters are always applied first to reduce scan volume
- `has` / `has_any` preferred over `contains` for indexed performance where applicable
- `project` used early to reduce returned fields
- Queries are written to be adapted to your own tenant's table schema — table and column names may vary slightly depending on your Microsoft 365 Defender / Sentinel configuration

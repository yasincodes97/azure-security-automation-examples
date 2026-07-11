"""
Defender Vulnerability Report Generator

Fetches high-severity, exploitable vulnerabilities from the Microsoft Defender
for Endpoint API and exports a prioritized CSV report for security triage.

Authentication is handled via MSAL (Microsoft Authentication Library) using
an app registration with the "Vulnerability.Read.All" application permission.
"""

import os
import csv
import sys
from datetime import datetime

import requests
import msal

TENANT_ID = os.environ.get("TENANT_ID")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://api.securitycenter.microsoft.com/.default"]
API_BASE_URL = "https://api.securitycenter.microsoft.com/api"

MIN_SEVERITY = {"High", "Critical"}


def get_access_token() -> str:
    """Authenticate against Microsoft Entra ID and return an access token."""
    app = msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=AUTHORITY,
    )
    result = app.acquire_token_for_client(scopes=SCOPE)

    if "access_token" not in result:
        raise RuntimeError(
            f"Authentication failed: {result.get('error_description', 'unknown error')}"
        )
    return result["access_token"]


def fetch_vulnerabilities(token: str) -> list[dict]:
    """Fetch vulnerability findings from Defender for Endpoint API."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_BASE_URL}/vulnerabilities",
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("value", [])


def filter_and_prioritize(vulnerabilities: list[dict]) -> list[dict]:
    """Filter for high/critical severity with known exploits, sorted by CVSS score."""
    filtered = [
        v for v in vulnerabilities
        if v.get("severity") in MIN_SEVERITY and v.get("exploitVerified", False)
    ]
    return sorted(filtered, key=lambda v: v.get("cvssV3", 0), reverse=True)


def export_to_csv(vulnerabilities: list[dict], output_path: str) -> None:
    """Write prioritized vulnerability list to a CSV file."""
    fieldnames = ["id", "name", "severity", "cvssV3", "exposedMachines", "publishedOn"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for vuln in vulnerabilities:
            writer.writerow(vuln)

    print(f"Exported {len(vulnerabilities)} vulnerabilities to {output_path}")


def main() -> None:
    if not all([TENANT_ID, CLIENT_ID, CLIENT_SECRET]):
        print("Error: TENANT_ID, CLIENT_ID, and CLIENT_SECRET environment variables must be set.")
        sys.exit(1)

    token = get_access_token()
    vulnerabilities = fetch_vulnerabilities(token)
    prioritized = filter_and_prioritize(vulnerabilities)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_path = f"vulnerability_report_{timestamp}.csv"
    export_to_csv(prioritized, output_path)


if __name__ == "__main__":
    main()

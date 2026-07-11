"""
Entra ID Stale Account Report

Identifies user accounts in Microsoft Entra ID that haven't signed in for a
configurable number of days, and exports them to a CSV report for access
review and account hygiene purposes.

Authentication is handled via MSAL using an app registration with the
"User.Read.All" and "AuditLog.Read.All" application permissions (required
to read the signInActivity property via Microsoft Graph).
"""

import os
import csv
import sys
from datetime import datetime, timezone

import requests
import msal

TENANT_ID = os.environ.get("TENANT_ID")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]
GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

STALE_THRESHOLD_DAYS = int(os.environ.get("STALE_THRESHOLD_DAYS", "90"))


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


def fetch_users_with_signin_activity(token: str) -> list[dict]:
    """Fetch all users with their last sign-in timestamp, following pagination."""
    headers = {"Authorization": f"Bearer {token}"}
    url = (
        f"{GRAPH_BASE_URL}/users"
        "?$select=id,displayName,userPrincipalName,accountEnabled,signInActivity"
        "&$top=999"
    )

    users = []
    while url:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        users.extend(data.get("value", []))
        url = data.get("@odata.nextLink")

    return users


def filter_stale_accounts(users: list[dict], threshold_days: int) -> list[dict]:
    """Filter for enabled accounts with no sign-in, or sign-in older than the threshold."""
    stale = []
    now = datetime.now(timezone.utc)

    for user in users:
        if not user.get("accountEnabled", False):
            continue

        signin_activity = user.get("signInActivity") or {}
        last_signin_raw = signin_activity.get("lastSignInDateTime")

        if not last_signin_raw:
            days_inactive = None
        else:
            last_signin = datetime.fromisoformat(last_signin_raw.replace("Z", "+00:00"))
            days_inactive = (now - last_signin).days

        if days_inactive is None or days_inactive >= threshold_days:
            stale.append({
                "id": user.get("id"),
                "displayName": user.get("displayName"),
                "userPrincipalName": user.get("userPrincipalName"),
                "lastSignIn": last_signin_raw or "Never",
                "daysInactive": days_inactive if days_inactive is not None else "N/A",
            })

    return sorted(stale, key=lambda u: (u["daysInactive"] == "N/A", u["daysInactive"]), reverse=True)


def export_to_csv(accounts: list[dict], output_path: str) -> None:
    """Write the stale account list to a CSV file."""
    fieldnames = ["id", "displayName", "userPrincipalName", "lastSignIn", "daysInactive"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(accounts)

    print(f"Exported {len(accounts)} stale accounts to {output_path}")


def main() -> None:
    if not all([TENANT_ID, CLIENT_ID, CLIENT_SECRET]):
        print("Error: TENANT_ID, CLIENT_ID, and CLIENT_SECRET environment variables must be set.")
        sys.exit(1)

    token = get_access_token()
    users = fetch_users_with_signin_activity(token)
    stale_accounts = filter_stale_accounts(users, STALE_THRESHOLD_DAYS)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_path = f"stale_accounts_report_{timestamp}.csv"
    export_to_csv(stale_accounts, output_path)


if __name__ == "__main__":
    main()

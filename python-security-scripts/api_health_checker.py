"""
API / Endpoint Health Checker

Checks a list of HTTP endpoints for availability and response time, and
reports which ones are down or responding slowly. Useful for monitoring
internal APIs, websites, or third-party service dependencies.

Endpoints are configured in ENDPOINTS below, or can be loaded from a JSON
file passed as a command-line argument.
"""

import sys
import json
import argparse
import time
from datetime import datetime

import requests

ENDPOINTS = [
    {"name": "Example API", "url": "https://example.com/health", "timeout": 5},
    {"name": "Example Website", "url": "https://example.com", "timeout": 5},
]

SLOW_RESPONSE_THRESHOLD_MS = 1000


def check_endpoint(endpoint: dict) -> dict:
    """Perform a single health check against one endpoint."""
    name = endpoint["name"]
    url = endpoint["url"]
    timeout = endpoint.get("timeout", 5)

    result = {
        "name": name,
        "url": url,
        "status": "UNKNOWN",
        "status_code": None,
        "response_time_ms": None,
        "error": None,
        "checked_at": datetime.utcnow().isoformat(),
    }

    try:
        start = time.perf_counter()
        response = requests.get(url, timeout=timeout)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        result["status_code"] = response.status_code
        result["response_time_ms"] = elapsed_ms

        if response.status_code >= 500:
            result["status"] = "DOWN"
        elif response.status_code >= 400:
            result["status"] = "ERROR"
        elif elapsed_ms > SLOW_RESPONSE_THRESHOLD_MS:
            result["status"] = "SLOW"
        else:
            result["status"] = "UP"

    except requests.exceptions.Timeout:
        result["status"] = "DOWN"
        result["error"] = f"Request timed out after {timeout}s"
    except requests.exceptions.ConnectionError as e:
        result["status"] = "DOWN"
        result["error"] = f"Connection error: {e}"
    except requests.exceptions.RequestException as e:
        result["status"] = "DOWN"
        result["error"] = str(e)

    return result


def check_all_endpoints(endpoints: list[dict]) -> list[dict]:
    """Run health checks against all configured endpoints."""
    return [check_endpoint(ep) for ep in endpoints]


def print_summary(results: list[dict]) -> None:
    """Print a readable summary of all health check results."""
    status_icons = {"UP": "OK", "SLOW": "SLOW", "ERROR": "ERROR", "DOWN": "DOWN"}

    print("=" * 60)
    print("ENDPOINT HEALTH CHECK SUMMARY")
    print("=" * 60)

    for result in results:
        icon = status_icons.get(result["status"], "?")
        line = f"[{icon:<5}] {result['name']:<25} {result['url']}"
        if result["response_time_ms"] is not None:
            line += f" ({result['response_time_ms']}ms)"
        if result["error"]:
            line += f" - {result['error']}"
        print(line)

    down_count = sum(1 for r in results if r["status"] in ("DOWN", "ERROR"))
    print("=" * 60)
    print(f"{len(results)} endpoints checked, {down_count} unhealthy")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the health of configured HTTP endpoints.")
    parser.add_argument(
        "--config",
        help="Path to a JSON file containing a list of endpoints (overrides built-in list)",
    )
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Print results as JSON instead of a human-readable summary",
    )
    args = parser.parse_args()

    endpoints = ENDPOINTS
    if args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            endpoints = json.load(f)

    results = check_all_endpoints(endpoints)

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        print_summary(results)

    if any(r["status"] in ("DOWN", "ERROR") for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()

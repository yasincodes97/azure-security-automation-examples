"""
Log File Analyzer

Parses a text-based log file and produces a summary report: counts by log
level, the most frequent error messages, and the time range covered.

Designed to be generic enough to work with most line-based application or
system logs that follow a "TIMESTAMP LEVEL message" style format. Adjust
LOG_LINE_PATTERN below to match your specific log format.
"""

import re
import sys
import argparse
from collections import Counter
from datetime import datetime

LOG_LINE_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL)\s+"
    r"(?P<message>.*)$"
)

TIMESTAMP_FORMATS = ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]


def parse_timestamp(raw: str) -> datetime | None:
    """Try parsing a timestamp string against known formats."""
    for fmt in TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def analyze_log_file(file_path: str) -> dict:
    """Read and analyze a log file, returning summary statistics."""
    level_counts = Counter()
    message_counts = Counter()
    timestamps = []
    unparsed_lines = 0
    total_lines = 0

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            total_lines += 1
            line = line.strip()
            if not line:
                continue

            match = LOG_LINE_PATTERN.match(line)
            if not match:
                unparsed_lines += 1
                continue

            level = match.group("level").upper()
            message = match.group("message")
            timestamp = parse_timestamp(match.group("timestamp"))

            level_counts[level] += 1
            if level in ("ERROR", "CRITICAL"):
                message_counts[message] += 1
            if timestamp:
                timestamps.append(timestamp)

    return {
        "total_lines": total_lines,
        "parsed_lines": total_lines - unparsed_lines,
        "unparsed_lines": unparsed_lines,
        "level_counts": level_counts,
        "top_error_messages": message_counts.most_common(10),
        "time_range": (min(timestamps), max(timestamps)) if timestamps else None,
    }


def print_report(stats: dict) -> None:
    """Print a human-readable summary of the analysis."""
    print("=" * 60)
    print("LOG FILE ANALYSIS REPORT")
    print("=" * 60)
    print(f"Total lines read:      {stats['total_lines']}")
    print(f"Successfully parsed:   {stats['parsed_lines']}")
    print(f"Unparsed lines:        {stats['unparsed_lines']}")

    if stats["time_range"]:
        start, end = stats["time_range"]
        print(f"Time range:            {start} to {end}")

    print("\nLog level breakdown:")
    for level, count in stats["level_counts"].most_common():
        print(f"  {level:<10} {count}")

    if stats["top_error_messages"]:
        print("\nTop error/critical messages:")
        for message, count in stats["top_error_messages"]:
            truncated = message if len(message) <= 80 else message[:77] + "..."
            print(f"  [{count}x] {truncated}")

    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a text-based log file.")
    parser.add_argument("log_file", help="Path to the log file to analyze")
    args = parser.parse_args()

    try:
        stats = analyze_log_file(args.log_file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.log_file}")
        sys.exit(1)

    print_report(stats)


if __name__ == "__main__":
    main()

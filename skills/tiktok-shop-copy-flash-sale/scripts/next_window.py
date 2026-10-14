#!/usr/bin/env python3
"""Calculate site-local three-day continuations without accessing a website."""

import argparse
import json
import re
from datetime import date, datetime, time, timedelta, timezone


def utc_offset(value):
    match = re.fullmatch(r"([+-])(\d{2}):(\d{2})", value)
    if not match:
        raise argparse.ArgumentTypeError("UTC offset must have format +07:00")
    hours, minutes = int(match[2]), int(match[3])
    if minutes > 59 or hours > 14 or (hours == 14 and minutes):
        raise argparse.ArgumentTypeError("UTC offset must be between -14:00 and +14:00")
    sign = 1 if match[1] == "+" else -1
    return timezone(sign * timedelta(hours=hours, minutes=minutes))


def local_date(value):
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Source end date must be YYYY-MM-DD") from exc


def positive_count(value):
    try:
        count = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Count must be a positive integer") from exc
    if count < 1:
        raise argparse.ArgumentTypeError("Count must be a positive integer")
    return count


def next_windows(source_end, site_timezone, count=1):
    beijing = timezone(timedelta(hours=8))
    windows = []
    previous_end = source_end
    for number in range(1, count + 1):
        start_date = previous_end + timedelta(days=1)
        end_date = start_date + timedelta(days=2)
        start = datetime.combine(start_date, time(0, 0), tzinfo=site_timezone)
        end = datetime.combine(end_date, time(23, 59), tzinfo=site_timezone)
        windows.append({
            "round": number,
            "source_end_date_local": previous_end.isoformat(),
            "start_local": start.isoformat(timespec="minutes"),
            "end_local": end.isoformat(timespec="minutes"),
            "start_beijing": start.astimezone(beijing).isoformat(timespec="minutes"),
            "end_beijing": end.astimezone(beijing).isoformat(timespec="minutes"),
        })
        previous_end = end_date
    return windows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-end-date", required=True, type=local_date,
                        help="Previous campaign end date in the site's local time")
    parser.add_argument("--utc-offset", required=True, type=utc_offset,
                        help="Offset shown by the site, e.g. +07:00 or +08:00")
    parser.add_argument("--count", type=positive_count, default=1,
                        help="Number of successive three-day windows to calculate")
    args = parser.parse_args()
    print(json.dumps(next_windows(args.source_end_date, args.utc_offset, args.count),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

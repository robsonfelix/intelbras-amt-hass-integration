#!/usr/bin/env python3
"""CLI tool for Intelbras AMT integration testing.

This tool communicates with the AMT control server (HTTP REST API)
to send commands to the alarm panel for protocol testing.

Usage:
    amt_cli status              # Get panel status
    amt_cli connected           # Check if panel is connected
    amt_cli raw "5B"            # Send raw command (status)
    amt_cli raw "41 35" -p 1234 # Send raw command with password
    amt_cli arm                 # Arm panel
    amt_cli arm -P A            # Arm partition A
    amt_cli arm --stay          # Arm in stay mode
    amt_cli arm -P A --stay     # Arm partition A in stay mode
    amt_cli disarm -p 1234      # Disarm panel
    amt_cli siren on            # Turn siren on
    amt_cli pgm 1 on            # Turn PGM 1 on

Requirements:
    pip install httpx  (or use requests/urllib)
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

try:
    import httpx
    USE_HTTPX = True
except ImportError:
    import urllib.request
    import urllib.error
    USE_HTTPX = False

DEFAULT_URL = "http://localhost:9019"


def print_json(data: dict[str, Any], indent: int = 2) -> None:
    """Pretty print JSON data."""
    print(json.dumps(data, indent=indent, ensure_ascii=False))


def http_get(url: str) -> dict[str, Any]:
    """Make HTTP GET request."""
    if USE_HTTPX:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(url)
            return r.json()
    else:
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            return json.loads(e.read().decode())


def http_post(url: str, data: dict[str, Any]) -> dict[str, Any]:
    """Make HTTP POST request with JSON body."""
    if USE_HTTPX:
        with httpx.Client(timeout=10.0) as client:
            r = client.post(url, json=data)
            return r.json()
    else:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            return json.loads(e.read().decode())


def cmd_status(args: argparse.Namespace) -> int:
    """Get panel status."""
    result = http_get(f"{args.url}/status")
    print_json(result)
    return 0 if result.get("connected") else 1


def cmd_connected(args: argparse.Namespace) -> int:
    """Check if panel is connected."""
    result = http_get(f"{args.url}/connected")
    print_json(result)
    return 0 if result.get("connected") else 1


def cmd_raw(args: argparse.Namespace) -> int:
    """Send raw command."""
    data = {"command": args.hex}
    if args.password:
        data["password"] = args.password

    result = http_post(f"{args.url}/command/raw", data)
    print_json(result)
    return 0 if result.get("success") else 1


def cmd_arm(args: argparse.Namespace) -> int:
    """Arm panel or partition."""
    data: dict[str, Any] = {}
    if args.partition:
        data["partition"] = args.partition
    if args.stay:
        data["stay"] = True
    if args.password:
        data["password"] = args.password

    result = http_post(f"{args.url}/command/arm", data)
    print_json(result)
    return 0 if result.get("success") else 1


def cmd_disarm(args: argparse.Namespace) -> int:
    """Disarm panel or partition."""
    data: dict[str, Any] = {}
    if args.partition:
        data["partition"] = args.partition
    if args.password:
        data["password"] = args.password

    result = http_post(f"{args.url}/command/disarm", data)
    print_json(result)
    return 0 if result.get("success") else 1


def cmd_stay(args: argparse.Namespace) -> int:
    """Arm in stay mode."""
    data: dict[str, Any] = {}
    if args.password:
        data["password"] = args.password

    result = http_post(f"{args.url}/command/stay", data)
    print_json(result)
    return 0 if result.get("success") else 1


def cmd_siren(args: argparse.Namespace) -> int:
    """Control siren."""
    result = http_post(f"{args.url}/command/siren", {"action": args.action})
    print_json(result)
    return 0 if result.get("success") else 1


def cmd_pgm(args: argparse.Namespace) -> int:
    """Control PGM output."""
    result = http_post(f"{args.url}/command/pgm", {
        "number": args.number,
        "action": args.action,
    })
    print_json(result)
    return 0 if result.get("success") else 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CLI tool for Intelbras AMT integration testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status              Get panel status
  %(prog)s raw "5B"            Send status command (0x5B)
  %(prog)s raw "41 35" -p 1234 Test partition A stay mode
  %(prog)s arm --stay          Arm in stay mode
  %(prog)s arm -P A --stay     Arm partition A in stay mode
  %(prog)s disarm -p 1234      Disarm with password
        """,
    )
    parser.add_argument(
        "--url", "-u",
        default=DEFAULT_URL,
        help=f"Control server URL (default: {DEFAULT_URL})",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # status command
    status_parser = subparsers.add_parser("status", help="Get panel status")
    status_parser.set_defaults(func=cmd_status)

    # connected command
    connected_parser = subparsers.add_parser("connected", help="Check if panel is connected")
    connected_parser.set_defaults(func=cmd_connected)

    # raw command
    raw_parser = subparsers.add_parser("raw", help="Send raw hex command")
    raw_parser.add_argument("hex", help="Command as hex string (e.g., '41 35' or 'A5')")
    raw_parser.add_argument("--password", "-p", help="Password override")
    raw_parser.set_defaults(func=cmd_raw)

    # arm command
    arm_parser = subparsers.add_parser("arm", help="Arm panel or partition")
    arm_parser.add_argument("--partition", "-P", choices=["A", "B", "C", "D"],
                           help="Partition to arm (A/B/C/D)")
    arm_parser.add_argument("--stay", "-s", action="store_true",
                           help="Arm in stay mode")
    arm_parser.add_argument("--password", "-p", help="Password")
    arm_parser.set_defaults(func=cmd_arm)

    # disarm command
    disarm_parser = subparsers.add_parser("disarm", help="Disarm panel or partition")
    disarm_parser.add_argument("--partition", "-P", choices=["A", "B", "C", "D"],
                              help="Partition to disarm (A/B/C/D)")
    disarm_parser.add_argument("--password", "-p", help="Password")
    disarm_parser.set_defaults(func=cmd_disarm)

    # stay command
    stay_parser = subparsers.add_parser("stay", help="Arm in stay mode")
    stay_parser.add_argument("--password", "-p", help="Password")
    stay_parser.set_defaults(func=cmd_stay)

    # siren command
    siren_parser = subparsers.add_parser("siren", help="Control siren")
    siren_parser.add_argument("action", choices=["on", "off"],
                             help="Siren action (on/off)")
    siren_parser.set_defaults(func=cmd_siren)

    # pgm command
    pgm_parser = subparsers.add_parser("pgm", help="Control PGM output")
    pgm_parser.add_argument("number", type=int, choices=range(1, 20),
                           metavar="N", help="PGM number (1-19)")
    pgm_parser.add_argument("action", choices=["on", "off"],
                           help="PGM action (on/off)")
    pgm_parser.set_defaults(func=cmd_pgm)

    args = parser.parse_args()

    try:
        return args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Command-line client for sending a complete motion sequence by TCP."""

import argparse

from behavior_manager_client import BehaviorManager


def parse_args():
    parser = argparse.ArgumentParser(
        description="Send a predefined UR5e motion sequence to the classroom server."
    )
    parser.add_argument(
        "motion",
        nargs="?",
        help="motion name, for example: init, handshake or give5",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="list the available motion names and exit",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    behavior = BehaviorManager()

    if args.list:
        print("Available motions:")
        for motion in behavior.available_motions():
            print(f"  {motion}")
        return 0

    if args.motion is None:
        print("No motion specified. Use --list to see the available motions.")
        return 2

    if args.motion not in behavior.available_motions():
        print(f"Unknown motion: {args.motion}")
        print("Available motions: " + ", ".join(behavior.available_motions()))
        return 2

    print(f"[CLIENT] Requesting motion: {args.motion}")
    return 0 if behavior.execute_command(args.motion) else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json

from . import (
    analyze_email,
    canon_email,
    rules_info,
    rules_version,
    update_rules,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="emailvet",
        description="Provider-aware email address canonicalization.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    canon_parser = subparsers.add_parser(
        "canon",
        help="Canonicalize one email address.",
    )
    canon_parser.add_argument("email")

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze one email address.",
    )
    analyze_parser.add_argument("email")

    subparsers.add_parser(
        "rules-version",
        help="Show the active rules version.",
    )

    subparsers.add_parser(
        "rules-info",
        help="Show active rules metadata.",
    )

    update_parser = subparsers.add_parser(
        "update-rules",
        help="Download and install a rules file.",
    )
    update_parser.add_argument(
        "url",
        nargs="?",
        default=None,
        help=(
            "Rules JSON URL. If omitted, EMAILVET_RULES_URL is used."
        ),
    )

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "canon":
        print(canon_email(args.email))
        return

    if args.command == "analyze":
        result = analyze_email(args.email)

        print(
            json.dumps(
                {
                    "original": result.original,
                    "canonical": result.canonical,
                    "provider": result.provider,
                    "rules_applied": list(result.rules_applied),
                },
                indent=2,
            )
        )
        return

    if args.command == "rules-version":
        print(rules_version())
        return

    if args.command == "rules-info":
        print(json.dumps(rules_info(), indent=2))
        return

    if args.command == "update-rules":
        print(json.dumps(update_rules(args.url), indent=2))
        return

    parser.error("Unknown command")


if __name__ == "__main__":
    main()

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .rules import find_provider


@dataclass(frozen=True)
class EmailAnalysis:
    original: str
    canonical: str
    provider: str | None
    rules_applied: Tuple[str, ...]


def _split_email(email: str) -> tuple[str, str]:
    if not isinstance(email, str):
        raise TypeError("email must be a string")

    email = email.strip()

    if not email:
        raise ValueError("email cannot be empty")

    if email.count("@") != 1:
        raise ValueError("email must contain exactly one @ character")

    local_part, domain = email.rsplit("@", 1)

    if not local_part:
        raise ValueError("email local part cannot be empty")

    if not domain:
        raise ValueError("email domain cannot be empty")

    return local_part, domain


def analyze_email(email: str) -> EmailAnalysis:
    original = email
    local_part, domain = _split_email(email)

    normalized_domain = domain.lower()
    rules_applied: list[str] = []

    if normalized_domain != domain:
        rules_applied.append("lowercase_domain")

    provider_id, provider = find_provider(normalized_domain)

    if provider is None:
        canonical = f"{local_part}@{normalized_domain}"

        return EmailAnalysis(
            original=original,
            canonical=canonical,
            provider=None,
            rules_applied=tuple(rules_applied),
        )

    rules = provider["rules"]

    if rules.get("lowercase_local_part", False):
        lowered = local_part.lower()

        if lowered != local_part:
            rules_applied.append("lowercase_local_part")

        local_part = lowered

    subaddressing = rules.get("subaddressing", {})
    separator = subaddressing.get("separator")
    strip_subaddress = subaddressing.get("strip", False)

    if strip_subaddress and separator and separator in local_part:
        local_part = local_part.split(separator, 1)[0]
        rules_applied.append("strip_subaddress")

    dot_behavior = rules.get("dots", {}).get("behavior", "significant")

    if dot_behavior == "ignore":
        if "." in local_part:
            local_part = local_part.replace(".", "")
            rules_applied.append("ignore_dots")

    elif dot_behavior == "equivalent_to_hyphen":
        if "." in local_part:
            local_part = local_part.replace(".", "-")
            rules_applied.append("canonicalize_dots_to_hyphens")

    elif dot_behavior != "significant":
        raise ValueError(
            f"Unsupported dot behavior in rules: {dot_behavior!r}"
        )

    canonical_domain = provider.get("canonical_domain")

    if canonical_domain:
        canonical_domain = canonical_domain.lower()

        if canonical_domain != normalized_domain:
            rules_applied.append("canonicalize_domain")

        normalized_domain = canonical_domain

    canonical = f"{local_part}@{normalized_domain}"

    return EmailAnalysis(
        original=original,
        canonical=canonical,
        provider=provider_id,
        rules_applied=tuple(rules_applied),
    )


def canon_email(email: str) -> str:
    return analyze_email(email).canonical

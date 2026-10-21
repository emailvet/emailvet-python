from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from pathlib import Path
import os


SUPPORTED_SCHEMA_VERSION = 1
ALLOWED_CONFIDENCE = {"guaranteed", "conditional", "observed"}
ALLOWED_DOT_BEHAVIORS = {
    "significant",
    "ignore",
    "equivalent_to_hyphen",
}


def _downloaded_rules_path() -> Path:
    custom_path = os.environ.get("EMAILVET_RULES_PATH")

    if custom_path:
        return Path(custom_path).expanduser()

    return Path.home() / ".emailvet" / "providers.json"


def _bundled_rules_path():
    return files("emailvet").joinpath("data/providers.json")


def _read_json(path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _validate_confidence(
    provider_id: str,
    rule_name: str,
    value: str | None,
) -> None:
    if value is None:
        return

    if value not in ALLOWED_CONFIDENCE:
        raise ValueError(
            f"Provider {provider_id!r} rule {rule_name!r} has invalid "
            f"confidence {value!r}"
        )


def validate_rules(data: dict) -> None:
    if not isinstance(data, dict):
        raise ValueError("Rules file must contain a JSON object")

    schema_version = data.get("schema_version")

    if schema_version != SUPPORTED_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported rules schema version: {schema_version!r}"
        )

    rules_version = data.get("rules_version")

    if not isinstance(rules_version, str) or not rules_version.strip():
        raise ValueError("rules_version must be a non-empty string")

    providers = data.get("providers")

    if not isinstance(providers, dict):
        raise ValueError("providers must be an object")

    for provider_id, provider in providers.items():
        if not isinstance(provider_id, str) or not provider_id:
            raise ValueError("Provider IDs must be non-empty strings")

        if not isinstance(provider, dict):
            raise ValueError(f"Provider {provider_id!r} must be an object")

        domains = provider.get("domains")

        if not isinstance(domains, list) or not domains:
            raise ValueError(
                f"Provider {provider_id!r} must have at least one domain"
            )

        for domain in domains:
            if not isinstance(domain, str) or not domain.strip():
                raise ValueError(
                    f"Provider {provider_id!r} contains an invalid domain"
                )

        canonical_domain = provider.get("canonical_domain")

        if canonical_domain is not None and not isinstance(
            canonical_domain, str
        ):
            raise ValueError(
                f"Provider {provider_id!r} canonical_domain must be a string"
            )

        rules = provider.get("rules")

        if not isinstance(rules, dict):
            raise ValueError(
                f"Provider {provider_id!r} must contain a rules object"
            )

        lowercase_local_part = rules.get("lowercase_local_part", False)

        if not isinstance(lowercase_local_part, bool):
            raise ValueError(
                f"Provider {provider_id!r} lowercase_local_part must be boolean"
            )

        _validate_confidence(
            provider_id,
            "lowercase_local_part",
            rules.get("lowercase_local_part_confidence"),
        )

        subaddressing = rules.get("subaddressing", {})

        if not isinstance(subaddressing, dict):
            raise ValueError(
                f"Provider {provider_id!r} subaddressing must be an object"
            )

        separator = subaddressing.get("separator")

        if separator is not None:
            if not isinstance(separator, str) or len(separator) != 1:
                raise ValueError(
                    f"Provider {provider_id!r} subaddress separator "
                    "must be one character"
                )

        strip = subaddressing.get("strip", False)

        if not isinstance(strip, bool):
            raise ValueError(
                f"Provider {provider_id!r} subaddress strip must be boolean"
            )

        _validate_confidence(
            provider_id,
            "subaddressing",
            subaddressing.get("confidence"),
        )

        dots = rules.get("dots", {})

        if not isinstance(dots, dict):
            raise ValueError(
                f"Provider {provider_id!r} dots must be an object"
            )

        dot_behavior = dots.get("behavior", "significant")

        if dot_behavior not in ALLOWED_DOT_BEHAVIORS:
            raise ValueError(
                f"Provider {provider_id!r} has unsupported dot behavior "
                f"{dot_behavior!r}"
            )

        _validate_confidence(
            provider_id,
            "dots",
            dots.get("confidence"),
        )

        canonical_domain_rule = rules.get("canonical_domain")

        if canonical_domain_rule is not None:
            if not isinstance(canonical_domain_rule, dict):
                raise ValueError(
                    f"Provider {provider_id!r} canonical_domain rule "
                    "must be an object"
                )

            _validate_confidence(
                provider_id,
                "canonical_domain",
                canonical_domain_rule.get("confidence"),
            )

        conditional_equivalents = provider.get(
            "conditional_equivalent_domains",
            [],
        )

        if not isinstance(conditional_equivalents, list):
            raise ValueError(
                f"Provider {provider_id!r} conditional_equivalent_domains "
                "must be a list"
            )

        for domain in conditional_equivalents:
            if not isinstance(domain, str) or not domain.strip():
                raise ValueError(
                    f"Provider {provider_id!r} contains an invalid "
                    "conditional equivalent domain"
                )

        sources = provider.get("sources", [])

        if not isinstance(sources, list):
            raise ValueError(
                f"Provider {provider_id!r} sources must be a list"
            )

        for source in sources:
            if not isinstance(source, dict):
                raise ValueError(
                    f"Provider {provider_id!r} source must be an object"
                )

            for required in ("title", "url", "last_verified"):
                value = source.get(required)

                if not isinstance(value, str) or not value.strip():
                    raise ValueError(
                        f"Provider {provider_id!r} source missing "
                        f"{required!r}"
                    )


@lru_cache(maxsize=1)
def load_rules() -> tuple[dict, str]:
    downloaded_path = _downloaded_rules_path()

    if downloaded_path.is_file():
        try:
            data = _read_json(downloaded_path)
            validate_rules(data)
            return data, "downloaded"
        except (OSError, json.JSONDecodeError, ValueError):
            pass

    bundled_path = _bundled_rules_path()
    data = _read_json(bundled_path)
    validate_rules(data)

    return data, "bundled"


def clear_rules_cache() -> None:
    load_rules.cache_clear()


def rules_version() -> str:
    data, _source = load_rules()
    return data["rules_version"]


def rules_info() -> dict:
    data, source = load_rules()

    return {
        "version": data["rules_version"],
        "schema_version": data["schema_version"],
        "source": source,
    }


def find_provider(domain: str) -> tuple[str | None, dict | None]:
    data, _source = load_rules()

    for provider_id, provider in data["providers"].items():
        domains = {item.lower() for item in provider["domains"]}

        if domain.lower() in domains:
            return provider_id, provider

    return None, None

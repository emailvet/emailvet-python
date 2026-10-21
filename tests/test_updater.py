import json

import pytest

from emailvet.rules import validate_rules


def test_invalid_schema_version_is_rejected():
    data = {
        "schema_version": 999,
        "rules_version": "test",
        "providers": {},
    }

    with pytest.raises(ValueError):
        validate_rules(data)


def test_minimal_valid_rules_file():
    data = {
        "schema_version": 1,
        "rules_version": "2026.10.21-test",
        "providers": {
            "example": {
                "name": "Example",
                "domains": ["example.com"],
                "canonical_domain": "example.com",
                "rules": {
                    "lowercase_local_part": False,
                    "subaddressing": {
                        "separator": "+",
                        "strip": False,
                    },
                    "dots": {
                        "behavior": "significant",
                    },
                },
                "sources": [
                    {
                        "title": "Example documentation",
                        "url": "https://example.com",
                        "last_verified": "2026-10-21",
                    }
                ],
            }
        },
    }

    validate_rules(data)

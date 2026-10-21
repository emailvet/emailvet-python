from emailvet import rules_info, rules_version


def test_rules_version():
    assert rules_version() == "2026.10.21.3"


def test_rules_info():
    info = rules_info()

    assert info["version"] == "2026.10.21.3"
    assert info["schema_version"] == 1
    assert info["source"] in {"bundled", "downloaded"}

from emailvet import analyze_email, canon_email


def test_outlook_plus_subaddress_is_removed():
    assert canon_email("Fred+shop@outlook.com") == "fred@outlook.com"


def test_outlook_dots_are_preserved():
    assert canon_email("Fred.Smith@outlook.com") == "fred.smith@outlook.com"


def test_hotmail_is_still_generic():
    assert (
        canon_email("Fred.Smith+shop@HOTMAIL.COM")
        == "Fred.Smith+shop@hotmail.com"
    )


def test_proton_plus_subaddress_is_removed():
    assert canon_email("Alice+shop@proton.me") == "alice@proton.me"


def test_proton_domains_are_not_collapsed():
    assert canon_email("Alice@protonmail.ch") == "alice@protonmail.ch"
    assert canon_email("Alice@proton.me") == "alice@proton.me"
    assert canon_email("Alice@pm.me") == "alice@pm.me"


def test_proton_dots_are_preserved():
    assert canon_email("Alice.Smith@proton.me") == "alice.smith@proton.me"


def test_yandex_dots_canonicalize_to_hyphens():
    assert canon_email("My.Address@yandex.com") == "my-address@yandex.com"


def test_yandex_hyphens_are_preserved():
    assert canon_email("My-Address@yandex.com") == "my-address@yandex.com"


def test_yandex_analysis_reports_dot_rule():
    result = analyze_email("My.Address@yandex.com")

    assert result.provider == "yandex"
    assert result.canonical == "my-address@yandex.com"
    assert result.rules_applied == (
        "lowercase_local_part",
        "canonicalize_dots_to_hyphens",
    )


def test_ya_ru_is_still_generic():
    assert canon_email("My.Address@YA.RU") == "My.Address@ya.ru"

def test_fastmail_plus_subaddress_is_removed():
    assert canon_email("alice+shop@fastmail.com") == "alice@fastmail.com"


def test_fastmail_official_legacy_domain_plus_subaddress_is_removed():
    assert canon_email("alice+shop@fastmail.fm") == "alice@fastmail.fm"


def test_fastmail_official_regional_domain_plus_subaddress_is_removed():
    assert canon_email("alice+shop@fastmail.co.uk") == "alice@fastmail.co.uk"


def test_fastmail_less_obvious_official_domain_is_recognized():
    assert canon_email("alice+shop@sent.com") == "alice@sent.com"


def test_fastmail_dots_are_preserved():
    assert canon_email("alice.smith@fastmail.com") == "alice.smith@fastmail.com"


def test_fastmail_local_part_case_is_preserved():
    assert canon_email("Alice+shop@fastmail.com") == "Alice@fastmail.com"


def test_fastmail_custom_domain_is_not_assumed():
    assert (
        canon_email("Alice+shop@example.com")
        == "Alice+shop@example.com"
    )


def test_fastmail_analysis_reports_provider_and_plus_rule():
    result = analyze_email("Alice+shop@fastmail.com")

    assert result.provider == "fastmail"
    assert result.canonical == "Alice@fastmail.com"
    assert result.rules_applied == (
        "strip_subaddress",
    )


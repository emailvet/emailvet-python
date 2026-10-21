from emailvet import analyze_email, canon_email


def test_gmail_dots_are_removed():
    assert canon_email("a.b.c.d@gmail.com") == "abcd@gmail.com"


def test_gmail_plus_subaddress_is_removed():
    assert canon_email("abcd+123@gmail.com") == "abcd@gmail.com"


def test_gmail_dots_and_plus_are_removed():
    assert canon_email("a.b.c.d+123@gmail.com") == "abcd@gmail.com"


def test_gmail_local_part_is_lowercased():
    assert canon_email("A.B.C.D@gmail.com") == "abcd@gmail.com"


def test_googlemail_domain_canonicalizes_to_gmail():
    assert canon_email("A.B+shop@googlemail.com") == "ab@gmail.com"


def test_gmail_analysis_reports_rules():
    result = analyze_email("A.B+shop@googlemail.com")

    assert result.original == "A.B+shop@googlemail.com"
    assert result.canonical == "ab@gmail.com"
    assert result.provider == "gmail"

    assert result.rules_applied == (
        "lowercase_local_part",
        "strip_subaddress",
        "ignore_dots",
        "canonicalize_domain",
    )

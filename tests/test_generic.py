import pytest

from emailvet import analyze_email, canon_email


def test_unknown_provider_only_lowercases_domain():
    assert (
        canon_email("John.Smith+promo@EXAMPLE.COM")
        == "John.Smith+promo@example.com"
    )


def test_unknown_provider_preserves_local_part():
    assert (
        canon_email("John.Smith+promo@example.com")
        == "John.Smith+promo@example.com"
    )


def test_unknown_provider_has_no_provider():
    result = analyze_email("John.Smith@example.com")

    assert result.provider is None
    assert result.canonical == "John.Smith@example.com"


def test_leading_and_trailing_whitespace_is_ignored():
    assert canon_email("  a.b+123@gmail.com  ") == "ab@gmail.com"


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "not-an-email",
        "@example.com",
        "name@",
        "a@b@example.com",
    ],
)
def test_invalid_email_shape_raises_value_error(value):
    with pytest.raises(ValueError):
        canon_email(value)


def test_non_string_raises_type_error():
    with pytest.raises(TypeError):
        canon_email(None)

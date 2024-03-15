from inzetbooster.inzetrooster import get_csrf
import pytest


@pytest.mark.parametrize(
    ["html", "csrf_token"],
    [
        (
            '<html><input type="hidden" name="authenticity_token" value="SECRET"></html>',
            "SECRET",
        ),
        (
            """
            <html>
              <meta name="csrf-token" content="VERY SECRET">
              <input type="hidden" name="authenticity_token" value="SECRET">
            </html>
            """,
            "VERY SECRET",
        ),
    ],
)
def test_get_csrf(html: str, csrf_token: str) -> None:
    assert get_csrf(html=html) == csrf_token


def test_get_csrf_no_token() -> None:
    with pytest.raises(ValueError, match="no CSRF token found"):
        get_csrf(html="<html>Hello</html>")

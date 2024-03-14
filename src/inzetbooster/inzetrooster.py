import httpx
from bs4 import BeautifulSoup, Tag

from . import shifts

CSRF_TOKEN_NAME = "authenticity_token"


def to_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html5lib")


class Inzetrooster:
    client: httpx.Client
    organisation: str
    is_logged_in: bool

    def __init__(self, client: httpx.Client, organisation: str):
        self.client = client
        self.organisation = organisation
        self.is_logged_in = False

    def _get_csrf(
        self, *, html: str | None = None, soup: BeautifulSoup | None = None
    ) -> str:
        assert (html is None) != (soup is None)
        if soup is None:
            soup = to_soup(html)

        tag = soup.find("meta", {"name": "csrf-token"})
        if isinstance(tag, Tag):
            return tag.attrs["content"]

        tag = soup.find("input", {"type": "hidden", "name": CSRF_TOKEN_NAME})
        if isinstance(tag, Tag):
            return tag.attrs["value"]

        raise ValueError("no CSRF token found")

    def login(self, username: str, password: str) -> None:
        r = self.client.get(f"https://inzetrooster.nl/{self.organisation}/login")
        csrf_token = self._get_csrf(html=r.text)

        r = self.client.post(
            f"https://inzetrooster.nl/{self.organisation}/login",
            data={
                CSRF_TOKEN_NAME: csrf_token,
                "username": username,
                "password": password,
            },
        )
        self.is_logged_in = "Geen geldige gebruikersnaam" not in r.text
        if not self.is_logged_in:
            raise ValueError("invalid credentials")

    def export_shifts(self) -> str:
        assert self.is_logged_in, "You must be logged in to export shifts"
        r = self.client.get(
            f"https://inzetrooster.nl/{self.organisation}/admin/shifts/export",
            follow_redirects=False,
        )
        assert r.status_code == 200

        export_soup = to_soup(r.text)
        data = {
            CSRF_TOKEN_NAME: self._get_csrf(soup=export_soup),
            "from_date": "2024-01-01",
            "to_date": "2024-12-31",
            "days[]": [str(d + 1) for d in range(7)],
            "group_ids[]": [
                tag.attrs["value"]
                for tag in export_soup.find("select", {"name": "group_ids[]"}).find_all(
                    "option"
                )
            ],
            "button": "",
        }
        r = self.client.post(
            f"https://inzetrooster.nl/{self.organisation}/admin/shifts/export.csv",
            data=data,
            follow_redirects=False,
        )
        assert r.status_code == 200, "Export must return a 200 response"
        assert r.headers["content-type"] == "text/csv", "Response must be CSV"
        return r.text

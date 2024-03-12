import httpx
from bs4 import BeautifulSoup, Tag
import os


CSRF_TOKEN_NAME = "authenticity_token"


def log(event_name, info):
    if event_name == "http11.send_request_headers.started":
        request = info["request"]
        print(
            event_name,
            {
                "url": request.method + b" " + request.url.target,
                "headers": request.headers,
            },
        )
    elif event_name in (""):
        print(event_name, info)


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
        tag = soup.find("input", {"type": "hidden", "name": CSRF_TOKEN_NAME})
        if not isinstance(tag, Tag):
            raise ValueError("no CSRF token found")
        return tag.attrs["value"]

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

    def export_shifts(self) -> None:
        assert self.is_logged_in, "You must be logged in to export shifts"
        # r = self.client.get(
        #     f"https://inzetrooster.nl/{self.organisation}/admin", follow_redirects=False
        # )
        # assert r.status_code == 200
        # r = self.client.get(
        #     f"https://inzetrooster.nl/{self.organisation}/admin/shifts/modify",
        #     follow_redirects=False,
        # )
        # assert r.status_code == 200
        # r = self.client.get(
        #     f"https://inzetrooster.nl/{self.organisation}/admin/shifts/modify",
        #     follow_redirects=False,
        # )
        # assert r.status_code == 200
        r = self.client.get(
            f"https://inzetrooster.nl/{self.organisation}/admin/shifts/export",
            follow_redirects=False,
            extensions={"trace": log},
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
            headers={
                "accept": "*/*",
                "origin": "https://inzetrooster.nl",
                "referer": f"https://inzetrooster.nl/{self.organisation}/admin/shifts/export",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            },
            follow_redirects=False,
            extensions={"trace": log},
        )
        assert r.status_code == 200


with httpx.Client(follow_redirects=True) as client:
    ir = Inzetrooster(client, os.environ.get("ORGANIZATSION", "rvliethorp"))
    ir.login(os.environ["USERNAME"], os.environ["PASSWORD"])
    ir.export_shifts()

import datetime

import httpx
import structlog.stdlib
from bs4 import BeautifulSoup, Tag

CSRF_TOKEN_NAME = "authenticity_token"

logger = structlog.stdlib.get_logger(__name__)


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

    def login(self, username: str, password: str) -> None:
        logger.debug("Fetching login page")
        r = self.client.get(f"https://inzetrooster.nl/{self.organisation}/login")
        csrf_token = get_csrf(html=r.text)
        logger.debug("got CSRF token for login page", token=csrf_token)

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
            logger.error("login failed", username=username)
            raise ValueError("invalid credentials")
        logger.info("login succeeded", username=username)

    def export_shifts(self) -> str:
        assert self.is_logged_in, "You must be logged in to export shifts"
        logger.debug("loading export page to get CSRF and group ids")
        r = self.client.get(
            f"https://inzetrooster.nl/{self.organisation}/admin/shifts/export",
            follow_redirects=False,
        )
        assert r.status_code == 200

        export_soup = to_soup(r.text)
        from_date = datetime.date.today()
        to_date = from_date + datetime.timedelta(weeks=52)
        data = {
            CSRF_TOKEN_NAME: get_csrf(soup=export_soup),
            "from_date": from_date.strftime("%Y-%m-%d"),
            "to_date": to_date.strftime("%Y-%m-%d"),
            "days[]": [str(d + 1) for d in range(7)],
            "group_ids[]": [
                tag.attrs["value"]
                for tag in export_soup.find("select", {"name": "group_ids[]"}).find_all(
                    "option"
                )
            ],
            "button": "",
        }
        logger.info("requesting CSV export", data=data)
        r = self.client.post(
            f"https://inzetrooster.nl/{self.organisation}/admin/shifts/export.csv",
            data=data,
            follow_redirects=False,
        )
        assert r.status_code == 200, "Export must return a 200 response"
        assert r.headers["content-type"] == "text/csv", "Response must be CSV"
        return r.text

    def import_users(self, csv_data: str) -> None:
        assert self.is_logged_in, "You must be logged in to manage inactive users"
        r = self.client.get(
            f"https://inzetrooster.nl/{self.organisation}/admin/person_imports/new"
        )
        data = {
            CSRF_TOKEN_NAME: get_csrf(html=r.text),
        }
        files = {"person_import[file]": ("users.csv", csv_data, "text/csv")}
        r = self.client.post(
            f"https://inzetrooster.nl/{self.organisation}/admin/person_imports",
            data=data,
            files=files,
            follow_redirects=False,
        )
        assert r.status_code == 302, "Export must return a 302 response"
        assert (
            r.headers["location"]
            == f"https://inzetrooster.nl/{self.organisation}/admin"
        )

    def export_users(self, include_inactive: bool = False) -> str:
        assert self.is_logged_in, "You must be logged in to manage inactive users"
        r = self.client.get(
            f"https://inzetrooster.nl/{self.organisation}/admin/people/export"
        )
        data = {
            CSRF_TOKEN_NAME: get_csrf(html=r.text),
            "group_ids[]": "0",
            "field[]": [
                "identity",
                "first_name",
                "infix",
                "last_name",
                "email",
                "username",
                "exempt",
                "active_date",
                "inactive_date",
                "role",
                "remarks",
                "last_activity",
            ],
        }
        if include_inactive:
            data["inactive_people"] = "true"
        r = self.client.post(
            f"https://inzetrooster.nl/{self.organisation}/admin/people/export.csv",
            data=data,
            follow_redirects=False,
        )
        assert r.status_code == 200, "Export must return a 200 response"
        assert r.headers["content-type"] == "text/csv", "Response must be CSV"
        return r.text

    def make_all_users_inactive(self) -> None:
        assert self.is_logged_in, "You must be logged in to manage inactive users"
        r = self.client.get(
            f"https://inzetrooster.nl/{self.organisation}/admin/people/destroy/all"
        )
        data = {
            CSRF_TOKEN_NAME: get_csrf(html=r.text),
            "people_set_all": "inactive",
        }
        r = self.client.post(
            f"https://inzetrooster.nl/{self.organisation}/admin/people/destroy/all",
            data=data,
            follow_redirects=False,
        )
        assert r.status_code == 302, "Export must return a 302 response"


def get_csrf(*, html: str | None = None, soup: BeautifulSoup | None = None) -> str:
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

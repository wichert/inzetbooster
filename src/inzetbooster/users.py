import csv
import datetime
import io
from dataclasses import dataclass
from typing import BinaryIO, Iterable

import structlog
from openpyxl import load_workbook

logger = structlog.stdlib.get_logger(__name__)


@dataclass
class Person:
    id: str
    firstname: str
    preposition: str
    surname: str
    email: str
    username: str | None = None
    exempt: bool | None = None
    activated_date: datetime.date | None = None
    deactived_date: datetime.date | None = None
    role: str | None = None
    last_login: datetime.datetime | None = None

    def is_valid(self) -> bool:
        return bool(self.firstname and self.surname and self.email)

    def is_manegeplan_user(self) -> bool:
        return self.id.startswith("PRS")

    @classmethod
    def from_record(cls, record: dict[str, str]):
        logger.debug("parsing CSV record", data=record)
        return Person(
            id=record["Gebruiker_id"],
            firstname=record["Voornaam"],
            preposition=record["Tussen"],
            surname=record["Achternaam"],
            email=record["Email"],
            username=record["Gebruikersnaam"] or None,
            exempt=record["Vrijgesteld"] == "true",
            activated_date=_parse_date(record["Actief_datum"]),
            deactived_date=_parse_date(record["Inactief_datum"]),
            role=record["Rol_en_rechten"],
            last_login=datetime.datetime.strptime(
                record["Laatste_login"], "%Y-%m-%d %H:%M"
            )
            if record["Laatste_login"]
            else None,
        )


def _parse_date(value: str) -> datetime.date | None:
    return datetime.datetime.strptime(value, "%d-%m-%Y").date() if value else None


def parse_csv(f: str) -> Iterable[Person]:
    reader = csv.DictReader(io.StringIO(f, newline=""), dialect=csv.unix_dialect)
    return [Person.from_record(row) for row in reader]


def create_csv(people: Iterable[Person]) -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output, dialect=csv.unix_dialect)
    writer.writerow(
        ["Gebruiker_id", "Voornaam", "Tussen", "Achternaam", "Email", "Inactief_datum"]
    )
    for person in people:
        writer.writerow(
            [
                person.id,
                person.firstname,
                person.preposition,
                person.surname,
                person.email,
                person.deactived_date.strftime("%Y-%m-%d")
                if person.deactived_date
                else "",
            ]
        )
    return output.getvalue()


def read_manegeplan_export(fn: str | BinaryIO) -> Iterable[Person]:
    wb = load_workbook(fn)
    if (sheet := wb.active) is None:
        raise ValueError("workbook has no active sheet")

    rows = sheet.rows
    column_names = [h.value for h in next(rows)]
    while not column_names[-1]:
        column_names = column_names[:-1]

    for row_cells in rows:
        if all(c.value is None for c in row_cells):
            continue
        data = {column: cell.value for column, cell in zip(column_names, row_cells)}

        yield Person(
            id=data["Gebruiker_id"],
            firstname=data["Voornaam"] or "",
            preposition=data["Tussen"] or "",
            surname=data["Achternaam"] or "",
            email=data["Email"] or "",
        )

import csv
from dataclasses import dataclass
import datetime
from typing import Iterable

(
    "Dienst_id",
    "Groep_id",
    "Groep_naam",
    "Datum",
    "Dag",
    "Starttijd",
    "Eindtijd",
    "Tijdsduur",
    "Gebruiker_id",
    "Naam",
    "Email",
    "Telefoon",
    "Locatie_id",
    "Locatie_naam",
    "Afwezig",
    "Geannuleerd",
    "Starred",
    "Opmerkingen",
)


@dataclass()
class Shift:
    shift_id: int
    group_id: int
    group_name: str
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    user_id: str | None
    user_name: str | None
    user_email: str | None
    comments: str

    @classmethod
    def from_record(self, record: dict[str, str]):
        return Shift(
            shift_id=int(record["Dienst_id"]),
            group_id=int(record["Groep_id"]),
            group_name=record["Groep_naam"],
            date=datetime.datetime.strptime(record["Datum"], "%d-%m-%Y").date(),
            start_time=datetime.datetime.strptime(record["Starttijd"], "%H:%M").time(),
            end_time=datetime.datetime.strptime(record["Eindtijd"], "%H:%M").time(),
            user_id=record["Gebruiker_id"] if record["Gebruiker_id"] else None,
            user_name=record["Naam"] if record["Naam"] else None,
            user_email=record["Email"] if record["Email"] else None,
            comments=record["Opmerkingen"],
        )


def parse_csv(f: Iterable[str]) -> list[Shift]:
    reader = csv.DictReader(f)
    return [Shift.from_record(row) for row in reader]

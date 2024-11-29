import datetime
from pathlib import Path

import pytest
from inzetbooster.users import Person, parse_csv, read_manegeplan_export


@pytest.mark.parametrize(
    ["person", "valid"],
    [
        (
            Person(
                id="PN1",
                firstname="Jane",
                preposition="",
                surname="Doe",
                email="jane@example.com",
            ),
            True,
        ),
        (
            Person(
                id="PN2",
                firstname="",
                preposition="",
                surname="Doe",
                email="jane@example.com",
            ),
            False,
        ),
        (
            Person(
                id="PN3",
                firstname="Jane",
                preposition="",
                surname="",
                email="jane@example.com",
            ),
            False,
        ),
        (
            Person(
                id="PN4",
                firstname="Jane",
                preposition="",
                surname="Doe",
                email="",
            ),
            False,
        ),
    ],
)
def test_person_is_valid(person: Person, valid: bool) -> None:
    assert person.is_valid() == valid


def test_read_manegeplan_export():
    path = Path(__file__).parent / "manegeplan-export.xlsx"
    persons = list(read_manegeplan_export(path))
    assert persons == [
        Person(
            id="PRS100",
            firstname="Alice",
            preposition="in",
            surname="Chains",
            email="alice@rock.me",
        ),
        Person(
            id="PRS103",
            firstname="Madonna",
            preposition="",
            surname="",
            email="madonna",
        ),
    ]


def test_parse_csv():
    input = """\
"Gebruiker_id","Voornaam","Tussen","Achternaam","Email","Gebruikersnaam","Vrijgesteld","Actief_datum","Inactief_datum","Herinneringen","Rol_en_rechten","Opmerkingen","Laatste_login"
"2","Vrijwilligerscoordinator","","Liethorp","vrijwilligers@example.com","vrijwilligers","false","12-01-2024","","true","admin","","2024-03-25 11:59"
"PRS100","","","Acme Ltd","info@acme.example.com","acme","false","20-04-2023","","true","user","","2024-02-01 17:31"
"PRS103","Bianca","","Smith","bianca@example.com","BiancaPRS103","false","20-04-2023","","true","user","",""
"""
    assert parse_csv(input) == [
        Person(
            id="2",
            firstname="Vrijwilligerscoordinator",
            preposition="",
            surname="Liethorp",
            email="vrijwilligers@example.com",
            username="vrijwilligers",
            exempt=False,
            activated_date=datetime.date(2024, 1, 12),
            deactived_date=None,
            role="admin",
            last_login=datetime.datetime(2024, 3, 25, 11, 59),
        ),
        Person(
            id="PRS100",
            firstname="",
            preposition="",
            surname="Acme Ltd",
            email="info@acme.example.com",
            username="acme",
            exempt=False,
            activated_date=datetime.date(2023, 4, 20),
            deactived_date=None,
            role="user",
            last_login=datetime.datetime(2024, 2, 1, 17, 31),
        ),
        Person(
            id="PRS103",
            firstname="Bianca",
            preposition="",
            surname="Smith",
            email="bianca@example.com",
            username="BiancaPRS103",
            exempt=False,
            activated_date=datetime.date(2023, 4, 20),
            deactived_date=None,
            role="user",
            last_login=None,
        ),
    ]

from inzetbooster.shifts import Shift, parse_csv
import pytest
import datetime
import io


@pytest.mark.parametrize(
    ["record", "shift"],
    [
        # Uncovered shift
        (
            {
                "Dienst_id": "2926209",
                "Groep_id": "10736",
                "Groep_naam": "Bar",
                "Datum": "13-01-2024",
                "Dag": " Zaterdag",
                "Starttijd": "16:00",
                "Eindtijd": "18:00",
                "Tijdsduur": "02:00",
                "Gebruiker_id": "",
                "Naam": "",
                "Email": "",
                "Telefoon": "",
                "Locatie_id": "",
                "Locatie_naam": "",
                "Afwezig": "",
                "Geannuleerd": "",
                "Starred": "",
                "Opmerkingen": "",
            },
            Shift(
                shift_id=2926209,
                group_id=10736,
                group_name="Bar",
                date=datetime.date(2024, 1, 13),
                start_time=datetime.time(16, 0),
                end_time=datetime.time(18, 0),
                user_id=None,
                user_name=None,
                user_email=None,
                comments="",
            ),
        ),
        # Covered shift
        (
            {
                "Dienst_id": "2891448",
                "Groep_id": "12079",
                "Groep_naam": "Bar met ervaring",
                "Datum": "13-01-2024",
                "Dag": " Zaterdag",
                "Starttijd": "15:30",
                "Eindtijd": "18:30",
                "Tijdsduur": "03:00",
                "Gebruiker_id": "PRS2921",
                "Naam": "Alice Alice",
                "Email": "alice@example.com",
                "Telefoon": "",
                "Locatie_id": "",
                "Locatie_naam": "",
                "Afwezig": "",
                "Geannuleerd": "",
                "Starred": "",
                "Opmerkingen": "Nieuwjaarsborrel",
            },
            Shift(
                shift_id=2891448,
                group_id=12079,
                group_name="Bar met ervaring",
                date=datetime.date(2024, 1, 13),
                start_time=datetime.time(15, 30),
                end_time=datetime.time(18, 30),
                user_id="PRS2921",
                user_name="Alice Alice",
                user_email="alice@example.com",
                comments="Nieuwjaarsborrel",
            ),
        ),
    ],
)
def test_from_record(record: dict[str, str], shift: Shift):
    assert Shift.from_record(record) == shift


def test_parse_csv():
    input = io.StringIO("""\
"Dienst_id","Groep_id","Groep_naam","Datum","Dag","Starttijd","Eindtijd","Tijdsduur","Gebruiker_id","Naam","Email","Telefoon","Locatie_id","Locatie_naam","Afwezig","Geannuleerd","Starred","Opmerkingen"
"2891448","12079","Bar met ervaring","13-01-2024"," Zaterdag","15:30","18:30","03:00","PRS2921","Alice Alice","alice@example.com","","","","","","","Nieuwjaarsborrel"
"2926209","10736","Bar","13-01-2024"," Zaterdag","16:00","18:00","02:00","","","","","","","","","",""
""")
    assert parse_csv(input) == [
        Shift(
            shift_id=2891448,
            group_id=12079,
            group_name="Bar met ervaring",
            date=datetime.date(2024, 1, 13),
            start_time=datetime.time(15, 30),
            end_time=datetime.time(18, 30),
            user_id="PRS2921",
            user_name="Alice Alice",
            user_email="alice@example.com",
            comments="Nieuwjaarsborrel",
        ),
        Shift(
            shift_id=2926209,
            group_id=10736,
            group_name="Bar",
            date=datetime.date(2024, 1, 13),
            start_time=datetime.time(16, 0),
            end_time=datetime.time(18, 0),
            user_id=None,
            user_name=None,
            user_email=None,
            comments="",
        ),
    ]

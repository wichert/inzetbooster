from pathlib import Path
import pytest
from inzetbooster.users import Person, read_manegeplan_export


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

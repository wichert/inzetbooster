from openpyxl import load_workbook
from dataclasses import dataclass
from typing import Iterable


@dataclass
class Person:
    id: str
    firstname: str
    preposition: str
    surname: str
    email: str

    def is_valid(self) -> bool:
        return bool(self.firstname and self.surname and self.email)


def read_manegeplan_export(fn: str) -> Iterable[Person]:
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

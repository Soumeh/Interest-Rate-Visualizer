from dataclasses import dataclass
from enum import Enum

from dash import dcc

@dataclass
class FiscalSelection:
    range: range
    translation: str

class FiscalSelections(Enum):
    Q1 = FiscalSelection(range(1, 4), "Prvi kvartal")
    Q2 = FiscalSelection(range(4, 7), "Drugi kvartal")
    Q3 = FiscalSelection(range(7, 10), "Treći kvartal")
    Q4 = FiscalSelection(range(10, 13), "Četvrti kvartal")
    YEAR = FiscalSelection(range(1, 13), "Godišnji nivo")

    @classmethod
    def get_dropdown(cls):
        return dcc.Dropdown(
            {selection.name: selection.value.translation for selection in cls},
            None,
            id="fiscal-selection-dropdown",
        )

from dataclasses import dataclass
from enum import Enum

from dash import dcc

from src.db import SerializableTable, SerializableType
from src.db.household import (
    HouseholdLoans,
    HouseholdLoanPurposes,
    HouseholdTermDeposits,
    HouseholdTermDepositPurposes,
)
from src.db.non_financial import (
    NonFinancialLoans,
    NonFinancialLoanPurposes,
    NonFinancialTermDeposits,
    NonFinancialTermDepositPurposes,
    NonFinancialTermDepositsBySize,
    NonFinancialTermDepositPurposesBySize,
)
from src.db.total import (
    TotalLoans,
    TotalLoanPurposes,
    TotalLoansByCurrency,
    TotalLoanPurposesByCurrency,
)


@dataclass
class TableType:
    table: type[SerializableTable]
    purpose: type[SerializableType]
    translation: str

    def get_purpose_dropdown(self):
        return dcc.Dropdown(
            {selection.name: selection.value for selection in self.purpose},
            None,
            id="table-purpose-dropdown",
        )


class TableTypes(Enum):
    HOUSEHOLD_LOANS = TableType(
        HouseholdLoans,
        HouseholdLoanPurposes,
        "Kamatne stope na kredite odobrene stanovništvu",
    )
    HOUSEHOLD_TERM_DEPOSITS = TableType(
        HouseholdTermDeposits,
        HouseholdTermDepositPurposes,
        "Kamatne stope na primljene oročene depozite stanovništva",
    )
    NON_FINANCIAL_LOANS = TableType(
        NonFinancialLoans,
        NonFinancialLoanPurposes,
        "Kamatne stope na kredite odobrene nefinancijskom sektoru",
    )
    NON_FINANCIAL_TERM_DEPOSITS = TableType(
        NonFinancialTermDeposits,
        NonFinancialTermDepositPurposes,
        "Kamatne stope na primljene oročene depozite nefinancijskog sektora",
    )
    NON_FINANCIAL_TERM_DEPOSITS_BY_SIZE = TableType(
        NonFinancialTermDepositsBySize,
        NonFinancialTermDepositPurposesBySize,
        "Kamatne stope na primljene oročene depozite nefinancijskog sektora, po veličini preduzeća",
    )
    TOTAL_LOANS = TableType(
        TotalLoans,
        TotalLoanPurposes,
        "Kamatne stope odobrene stanovništvu i nefinancijskom sektoru",
    )
    TOTAL_LOANS_BY_CURRENCY = TableType(
        TotalLoansByCurrency,
        TotalLoanPurposesByCurrency,
        "Kamatne stope odobrene stanovništvu i nefinancijskom sektoru, po valutama",
    )

    @classmethod
    def get_dropdown(cls):
        return dcc.Dropdown(
            {selection.name: selection.value.translation for selection in cls},
            None,
            id="table-type-dropdown",
        )

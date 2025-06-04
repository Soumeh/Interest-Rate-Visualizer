import enum

from pandas import DataFrame, Series
from sqlalchemy import (
    Column,
    Integer,
    Enum,
    Float,
    UniqueConstraint,
    Insert,
)
from sqlalchemy.dialects.postgresql import insert

from src.db import or_none, Base, SerializableData


class NonFinancialDataType(enum.Enum):
    TOTAL = "TOTAL"
    CURRENT_ASSETS = "CURRENT_ASSETS"
    INVESTMENT = "INVESTMENT"
    OTHER = "OTHER"

class NonFinancialData(SerializableData):
    id = Column(Integer, primary_key=True)
    data_type = Column(Enum(NonFinancialDataType), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    non_indexed = Column(Float)
    reference_rate = Column(Float)
    belibor_1m = Column(Float)
    belibor_3m = Column(Float)
    belibor_6m = Column(Float)
    other_indexations = Column(Float)
    total_rsd = Column(Float)

    eur = Column(Float)
    chf = Column(Float)
    usd = Column(Float)
    other_currencies = Column(Float)
    total_foreign_currency = Column(Float)

    final_total = Column(Float)
    _previous_year = None

    __table_args__ = (UniqueConstraint('data_type', 'year', 'month'),)

    @classmethod
    def query_insert(cls, year: int, month: int, row: DataFrame | Series, **extra_data) -> Insert:
        return insert(cls).values(
            data_type=extra_data["data_type"],
            year=year,
            month=month,
            non_indexed=or_none(row.iloc[0]),
            reference_rate=or_none(row.iloc[1]),
            belibor_1m=or_none(row.iloc[2]),
            belibor_3m=or_none(row.iloc[3]),
            belibor_6m=or_none(row.iloc[4]),
            other_indexations=or_none(row.iloc[5]),
            total_rsd=or_none(row.iloc[6]),
            eur=or_none(row.iloc[7]),
            chf=or_none(row.iloc[8]),
            usd=or_none(row.iloc[9]),
            other_currencies=or_none(row.iloc[10]),
            total_foreign_currency=or_none(row.iloc[11]),
            final_total=or_none(row.iloc[12]),
        ).on_conflict_do_nothing()

class NonFinancialImportsDataType(enum.Enum):
    TOTAL = "TOTAL"
    OTHER = "OTHER"

class NonFinancialImportsData(SerializableData):
    id = Column(Integer, primary_key=True)
    data_type = Column(Enum(NonFinancialImportsDataType))
    year = Column(Integer)
    month = Column(Integer)

    eur = Column(Float)
    chf = Column(Float)
    usd = Column(Float)
    other = Column(Float)
    total = Column(Float)

    __table_args__ = (UniqueConstraint('data_type', 'year', 'month'),)

    @classmethod
    def query_insert(cls, year: int, month: int, row: DataFrame | Series, **extra_data) -> Insert:
        return insert(cls).values(
            data_type=extra_data["data_type"],
            year=year,
            month=month,
            eur=or_none(row.iloc[0]),
            chf=or_none(row.iloc[1]),
            usd=or_none(row.iloc[2]),
            other=or_none(row.iloc[3]),
            total=or_none(row.iloc[4]),
        ).on_conflict_do_nothing()

class NonFinancialInterestRates(Base, NonFinancialData):
    __tablename__ = "non_financial_interest_rates"

class NonFinancialLoans(Base, NonFinancialData):
    __tablename__ = "non_financial_loans"

class NonFinancialImportsInterestRates(Base, NonFinancialImportsData):
    __tablename__ = "non_financial_imports_interest_rates"

class NonFinancialImportsLoans(Base, NonFinancialImportsData):
    __tablename__ = "non_financial_imports_loans"


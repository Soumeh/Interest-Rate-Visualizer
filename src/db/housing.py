from pandas import DataFrame, Series
from sqlalchemy import (
    Column,
    Float,
    Enum,
    UniqueConstraint,
    Integer, Insert,
)
from sqlalchemy.dialects.postgresql import insert

from src.db import or_none, Base, SerializableData, SerializableType

class HouseholdDataType(SerializableType):
    TOTAL = "TOTAL"
    HOUSING = "HOUSING"
    CONSUMER = "CONSUMER"
    CASH = "CASH"
    OTHER = "OTHER"

class HouseholdData(SerializableData):
    id = Column(Integer, primary_key=True)
    data_type = Column(Enum(HouseholdDataType), nullable=False)
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

class HouseholdInterestRates(Base, HouseholdData):
    __tablename__ = "household_interest_rates"

class HouseholdLoans(Base, HouseholdData):
    __tablename__ = "household_loans"

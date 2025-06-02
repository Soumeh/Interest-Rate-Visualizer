import enum

import pandas
import sqlalchemy
from pandas import DataFrame, isnull, Series
from sqlalchemy import Column, Integer, Float, Enum, Engine, MetaData, Table
from sqlalchemy.orm import declarative_base

Base = declarative_base()

def or_none(element):
    return None if isnull(element) else element

class BankingDataType(enum.Enum):
    TOTAL = "total"
    HOUSING = "housing"
    CONSUMER = "consumer"
    CASH = "cash"
    OTHER = "other"

class BankingData:
    id = Column(Integer, primary_key=True)
    data_type = Column(Enum(BankingDataType))
    year = Column(Integer)
    month = Column(Integer)

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

    @classmethod
    def from_row(cls, data_type: BankingDataType, year: int, month: int, row: DataFrame | Series) -> "BankingData":
        return cls(
            data_type=data_type,
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
        )

    @classmethod
    def frame_by_type(cls, engine: Engine, data_type: BankingDataType) -> DataFrame:
        table = Table(cls.__tablename__, MetaData(), autoload_with=engine)
        query = sqlalchemy.select("*").where(table.c.data_type == data_type.value)
        return pandas.read_sql_query(query, engine)

class HouseholdInterestRates(Base, BankingData):
    __tablename__ = "household_interest_rates"

class HouseholdLoans(Base, BankingData):
    __tablename__ = "household_loans"

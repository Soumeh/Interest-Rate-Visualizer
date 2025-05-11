import numpy
import pandas
from pandas import DataFrame
from sqlalchemy import Column, Integer, Float

from src.db import Base


class InterestRates:
    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    month = Column(Integer)

    non_indexed = Column(Float)
    reference_rate = Column(Float)
    belibor_1m = Column(Float)
    belibor_3m = Column(Float)
    belibor_6m = Column(Float)
    other_indexations = Column(Float)
    total = Column(Float)

    eur = Column(Float)
    chf = Column(Float)
    usd = Column(Float)
    other_currencies = Column(Float)
    total_foreign_currency = Column(Float)

    _previous_year = None

def or_none(element):
    return None if pandas.isnull(element) else element

class ConsumerInterestRates(Base, InterestRates):
    __tablename__ = "consumer_interest_rates"

    months = {
        "jan": 1,
        "january": 1,
        "januar": 1,

        "feb": 2,
        "february": 2,
        "februar": 2,

        "mar": 3,
        "march": 3,
        "mart": 3,

        "apr": 4,
        "april": 4,

        "may": 5,
        "maj": 5,

        "jun": 6,
        "june": 6,

        "jul": 7,
        "july": 7,

        "aug": 8,
        "august": 8,
        "avgust": 8,

        "sep": 9,
        "september": 9,
        "septamber": 9,

        "oct": 10,
        "october": 10,
        "oktobar": 10,

        "nov": 11,
        "november": 11,
        "novembar": 11,

        "dec": 12,
        "december": 12,
        "decembar": 12
    }

    @classmethod
    def from_row(cls, row: DataFrame) -> "ConsumerInterestRates":
        year = row.iloc[0]
        if numpy.isnan(year):
            year = cls._previous_year
        else:
            cls._previous_year = year

        month_str = row.iloc[1].lower()
        month = cls.months.get(month_str)

        return ConsumerInterestRates(
            year=year,
            month=month,
            non_indexed=or_none(row.iloc[2]),
            reference_rate=or_none(row.iloc[3]),
            belibor_1m=or_none(row.iloc[4]),
            belibor_3m=or_none(row.iloc[5]),
            belibor_6m=or_none(row.iloc[6]),
            other_indexations=or_none(row.iloc[7]),
            total=or_none(row.iloc[8]),
            eur=or_none(row.iloc[9]),
            chf=or_none(row.iloc[10]),
            usd=or_none(row.iloc[11]),
            other_currencies=or_none(row.iloc[12]),
            total_foreign_currency=or_none(row.iloc[13]),
        )

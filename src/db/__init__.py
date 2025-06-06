from enum import Enum
from typing import Tuple

import pandas
import sqlalchemy
from numpy import isnan
from pandas import isnull, DataFrame, Series
from sqlalchemy import Engine, Float, ResultProxy
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

from src.common.month_matcher import month_to_integer

Base = declarative_base()

def or_none(element):
    return None if isnull(element) else element

class SerializableType(Enum):
    pass

class SerializableData:
    __tablename__ = ""

    @classmethod
    def _frame_by_type(cls, engine: Engine, data_type: SerializableType) -> DataFrame:
        query = sqlalchemy.select("*").where(cls.__table__.c.purpose == data_type.value)
        return pandas.read_sql_query(query, engine)

    @classmethod
    def _get_start_end_points(cls, frame: DataFrame) -> Tuple[int, int]:
        start = 0
        while month_to_integer(str(frame.iloc[start, 1])) is None:
            start += 1
        end = 0
        while month_to_integer(str(frame.iloc[end, 1])) is None:
            end -= 1
        end += 1
        return start, end

    @classmethod
    async def _process_rows(
        cls,
        session: AsyncSession,
        date_frame: DataFrame,
        table_frame: DataFrame,
        purpose: type[SerializableType],
        **extra_data,
    ):
        previous_year = None
        index: int = 0
        try:
            for i, row in table_frame.iterrows():
                date = date_frame.iloc[index]
                index += 1
                year = date.iloc[0]
                if isnan(year):
                    year = previous_year
                else:
                    year = int(year)
                    previous_year = year
                month = month_to_integer(date.iloc[1])

                await cls.insert(session, purpose, year, month, row, **extra_data)

        except Exception as exception:
            print(f"Error processing row {i}: {exception}")

    @classmethod
    async def process_frame(cls, session: AsyncSession, frame: DataFrame):
        pass

    @classmethod
    async def insert(cls, session: AsyncSession, purpose: type[SerializableType], year: int, month: int, row: DataFrame, **extra_data):
        pass

class LocalInterestRates(Base, SerializableData):
    __tablename__ = "local_interest_rates"

    id: Mapped[int] = mapped_column(primary_key=True)
    non_indexed: Mapped[float] = mapped_column(Float, nullable=True)
    reference_rate: Mapped[float] = mapped_column(Float, nullable=True)
    belibor_1m: Mapped[float] = mapped_column(Float, nullable=True)
    belibor_3m: Mapped[float] = mapped_column(Float, nullable=True)
    belibor_6m: Mapped[float] = mapped_column(Float, nullable=True)
    other: Mapped[float] = mapped_column(Float, nullable=True)
    total: Mapped[float] = mapped_column(Float, nullable=True)

    @classmethod
    async def insert(cls, session: AsyncSession, row: DataFrame | Series) -> ResultProxy:
        query = insert(cls).values(
            non_indexed = or_none(row.iloc[0]),
            reference_rate = or_none(row.iloc[1]),
            belibor_1m = or_none(row.iloc[2]),
            belibor_3m = or_none(row.iloc[3]),
            belibor_6m = or_none(row.iloc[4]),
            other = or_none(row.iloc[5]),
            total = or_none(row.iloc[6]),
        ).on_conflict_do_nothing()
        return await session.execute(query)

class ForeignInterestRates(Base, SerializableData):
    __tablename__ = "foreign_interest_rates"

    id: Mapped[int] = mapped_column(primary_key=True)
    eur: Mapped[float] = mapped_column(Float, nullable=True)
    chf: Mapped[float] = mapped_column(Float, nullable=True)
    usd: Mapped[float] = mapped_column(Float, nullable=True)
    other: Mapped[float] = mapped_column(Float, nullable=True)
    total: Mapped[float] = mapped_column(Float, nullable=True)

    @classmethod
    async def insert(cls, session: AsyncSession, row: DataFrame | Series) -> ResultProxy:
        query = insert(cls).values(
            eur = or_none(row.iloc[0]),
            chf = or_none(row.iloc[1]),
            usd = or_none(row.iloc[2]),
            other = or_none(row.iloc[3]),
            total = or_none(row.iloc[4]),
        ).on_conflict_do_nothing()
        return await session.execute(query)

class EnterpriseInterestRates(Base, SerializableData):
    __tablename__ = 'enterprise_interest_rates'

    id: Mapped[int] = mapped_column(primary_key=True)
    up_to_one: Mapped[float] = mapped_column(Float, nullable=True)
    one_up_to_two: Mapped[float] = mapped_column(Float, nullable=True)
    over_two: Mapped[float] = mapped_column(Float, nullable=True)
    total: Mapped[float] = mapped_column(Float, nullable=True)

    @classmethod
    async def insert(cls, session: AsyncSession, row: DataFrame | Series) -> ResultProxy:
        query = insert(cls).values(
            up_to_one = or_none(row.iloc[0]),
            one_up_to_two = or_none(row.iloc[1]),
            over_two = or_none(row.iloc[2]),
            total = or_none(row.iloc[3]),
        ).on_conflict_do_nothing()
        return await session.execute(query)

class TotalInterestRates(Base, SerializableData):
    __tablename__ = 'total_interest_rates'

    id: Mapped[int] = mapped_column(primary_key=True)
    household: Mapped[float] = mapped_column(Float, nullable=True)
    non_financial: Mapped[float] = mapped_column(Float, nullable=True)
    total: Mapped[float] = mapped_column(Float, nullable=True)

    @classmethod
    async def insert(cls, session: AsyncSession, row: DataFrame | Series) -> ResultProxy:
        query = insert(cls).values(
            household = or_none(row.iloc[0]),
            non_financial = or_none(row.iloc[1]),
            total = or_none(row.iloc[2]),
        ).on_conflict_do_nothing()
        return await session.execute(query)

from enum import Enum

import pandas
import sqlalchemy
from pandas import isnull, DataFrame, Series
from sqlalchemy import Engine, Float, ResultProxy
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()

def or_none(element):
    return None if isnull(element) else element

class SerializableType(Enum):
    pass

class SerializableData:
    __tablename__ = ""

    @classmethod
    def frame_by_type(cls, engine: Engine, data_type: SerializableType) -> DataFrame:
        query = sqlalchemy.select("*").where(cls.__table__.c.purpose == data_type.value)
        return pandas.read_sql_query(query, engine)

    @classmethod
    def from_row(cls, year: int, month: int, row: DataFrame | Series, **extra_data) -> "SerializableData":
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
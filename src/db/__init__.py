from enum import Enum
from typing import Tuple

import pandas
import sqlalchemy
from numpy import isnan
from pandas import isnull, DataFrame, Series
from plotly import express
from plotly.graph_objs import Figure
from sqlalchemy import Float, ResultProxy, inspect, Row
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    Session,
    DeclarativeBase,
    scoped_session,
    InstanceState,
)

from src.common.month_matcher import month_to_integer


def or_none(element):
    return None if isnull(element) else element

class SerializableType(Enum):
    pass

class Base(DeclarativeBase):
    pass

class SerializableTable:
    __tablename__ = ""

    @classmethod
    def get_years(cls, session):
        table = cls.__table__.c
        query = sqlalchemy.select(table.year).distinct().order_by(table.year)
        result = session.execute(query)
        years = [row[0] for row in result.fetchall() if row[0] is not None]
        return years

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
            session: Session,
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
    async def insert(
            cls,
            session: Session,
            purpose: type[SerializableType],
            year: int,
            month: int,
            row: DataFrame,
            **extra_data,
    ):
        pass

    @classmethod
    def get_data(
            cls,
            session: scoped_session,
            purpose: str,
            year: int,
            month_range: range,
    ) -> DataFrame:
        table = cls.__table__

        rows = (
            cls.query(session)
            .where(table.c.purpose == purpose)
            .where(table.c.year == year)
            .where(table.c.month.between(month_range[0], month_range[-1]))
            .all()
        )

        frames = []
        for row in rows:
            if isinstance(row, Row):
                row = row[0]
            df = row.to_frame()
            frames.append(df)

        return pandas.concat(frames, ignore_index=True)

    @classmethod
    def query(cls, session: scoped_session):
        return session.query(cls)

    def to_frame(self) -> DataFrame:
        return pandas.DataFrame(self.to_dict())

    def to_dict(self) -> dict:
        data = {}

        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue
            if key.endswith("_id") or key == "id":
                continue
            if isinstance(value, SerializableType):
                continue
            if not isinstance(value, (bool, str, int, float, type(None))):
                continue
            data[key] = [value]

        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue
            if not key.endswith("_id") and f"{key}_id" in self.__dict__:
                if value is not None and isinstance(value, SerializableTable):
                    relation = value.to_frame()
                    relation_dict = { f"{key}.{k}": v for k, v in relation.to_dict("list").items() }
                    data.update(relation_dict)

        return data

    def to_express(self, data: DataFrame, theme: str) -> Figure:
        return express.bar(
            data,
            x="month_name",
            y="total",
            labels={"month_name": "Mesec", "total": "Ukupno"},
            template=theme,
        )

class LocalInterestRates(Base, SerializableTable):
    __tablename__ = "local_interest_rates"

    id: Mapped[int] = mapped_column(primary_key=True)
    non_indexed: Mapped[float] = mapped_column(Float, nullable=True)
    reference_rate: Mapped[float] = mapped_column(Float, nullable=True)
    belibor_1m: Mapped[float] = mapped_column(Float, nullable=True)
    belibor_3m: Mapped[float] = mapped_column(Float, nullable=True)
    belibor_6m: Mapped[float] = mapped_column(Float, nullable=True)
    other_local: Mapped[float] = mapped_column(Float, nullable=True)
    total_local: Mapped[float] = mapped_column(Float, nullable=True)

    @classmethod
    async def insert(
            cls, session: Session, row: DataFrame | Series
    ) -> ResultProxy:
        query = (
            insert(cls)
            .values(
                non_indexed=or_none(row.iloc[0]),
                reference_rate=or_none(row.iloc[1]),
                belibor_1m=or_none(row.iloc[2]),
                belibor_3m=or_none(row.iloc[3]),
                belibor_6m=or_none(row.iloc[4]),
                other_local=or_none(row.iloc[5]),
                total_local=or_none(row.iloc[6]),
            )
            .on_conflict_do_nothing()
        )
        return await session.execute(query)

class ForeignInterestRates(Base, SerializableTable):
    __tablename__ = "foreign_interest_rates"

    id: Mapped[int] = mapped_column(primary_key=True)
    eur: Mapped[float] = mapped_column(Float, nullable=True)
    chf: Mapped[float] = mapped_column(Float, nullable=True)
    usd: Mapped[float] = mapped_column(Float, nullable=True)
    other_foreign: Mapped[float] = mapped_column(Float, nullable=True)
    total_foreign: Mapped[float] = mapped_column(Float, nullable=True)

    @classmethod
    async def insert(
            cls, session: AsyncSession, row: DataFrame | Series
    ) -> ResultProxy:
        query = (
            insert(cls)
            .values(
                eur=or_none(row.iloc[0]),
                chf=or_none(row.iloc[1]),
                usd=or_none(row.iloc[2]),
                other_foreign=or_none(row.iloc[3]),
                total_foreign=or_none(row.iloc[4]),
            )
            .on_conflict_do_nothing()
        )
        return await session.execute(query)

class EnterpriseInterestRates(Base, SerializableTable):
    __tablename__ = "enterprise_interest_rates"

    id: Mapped[int] = mapped_column(primary_key=True)
    up_to_one: Mapped[float] = mapped_column(Float, nullable=True)
    one_up_to_two: Mapped[float] = mapped_column(Float, nullable=True)
    over_two: Mapped[float] = mapped_column(Float, nullable=True)
    total_enterprise: Mapped[float] = mapped_column(Float, nullable=True)

    @classmethod
    async def insert(
            cls, session: AsyncSession, row: DataFrame | Series
    ) -> ResultProxy:
        query = (
            insert(cls)
            .values(
                up_to_one=or_none(row.iloc[0]),
                one_up_to_two=or_none(row.iloc[1]),
                over_two=or_none(row.iloc[2]),
                total_enterprise=or_none(row.iloc[3]),
            )
            .on_conflict_do_nothing()
        )
        return await session.execute(query)

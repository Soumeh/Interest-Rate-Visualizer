from enum import Enum
from typing import Tuple

import pandas
import sqlalchemy
from numpy import isnan
from pandas import isnull, DataFrame
from plotly import express
from plotly.graph_objs import Figure
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    Session,
    DeclarativeBase,
    scoped_session,
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
            purpose: SerializableType,
            year: int,
            month_range: range,
    ) -> DataFrame:
        table = cls.__table__

        rows = (
            cls.query(session)
            .where(table.c.purpose == purpose.name)
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

        if not frames:
            return DataFrame()

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

    def get_columns(self):
        return [
            {"id": "year", "name": "Godina"},
            {"id": "month_name", "name": "Mesec"},
        ]

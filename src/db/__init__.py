from enum import Enum

import pandas
import sqlalchemy
from pandas import isnull, DataFrame, Series
from sqlalchemy import Engine, Column, Integer, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()

def or_none(element):
    return None if isnull(element) else element

class SerializableType(Enum):
    pass

class SerializableData:
    # data_type = Column(sqlalchemy.Enum(SerializableType))

    __tablename__ = ""

    @classmethod
    def frame_by_type(cls, engine: Engine, data_type: SerializableType) -> DataFrame:
        # table = Table(cls.__tablename__, MetaData(), autoload_with=engine)
        # query = sqlalchemy.select("*").where(table.c.data_type == data_type.value)
        query = sqlalchemy.select("*").where(cls.__table__.c.data_type == data_type.value)
        return pandas.read_sql_query(query, engine)

    @classmethod
    def from_row(cls, year: int, month: int, row: DataFrame | Series, **extra_data) -> "SerializableData":
        pass

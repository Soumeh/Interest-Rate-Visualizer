from pandas import DataFrame, Series
from sqlalchemy import Float, ResultProxy
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    Session,
)

from src.db import Base, SerializableTable, or_none


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
    async def insert(cls, session: Session, row: DataFrame | Series) -> ResultProxy:
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
    async def insert(cls, session: Session, row: DataFrame | Series) -> ResultProxy:
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

class InterestRateMaturity(SerializableTable):
    id: Mapped[int] = mapped_column(primary_key=True)
    up_to_one: Mapped[float] = mapped_column(Float, nullable=True)
    one_up_to_two: Mapped[float] = mapped_column(Float, nullable=True)
    over_two: Mapped[float] = mapped_column(Float, nullable=True)

    @classmethod
    async def insert(cls, session: Session, row: DataFrame | Series) -> ResultProxy:
        query = (
            insert(cls)
            .values(
                up_to_one=or_none(row.iloc[0]),
                one_up_to_two=or_none(row.iloc[1]),
                over_two=or_none(row.iloc[2]),
            )
            .on_conflict_do_nothing()
        )
        return await session.execute(query)

class LocalInterestRateMaturity(InterestRateMaturity, Base):
    __tablename__ = "local_interest_rate_maturity"

class ForeignInterestRateMaturity(InterestRateMaturity, Base):
    __tablename__ = "foreign_interest_rate_maturity"

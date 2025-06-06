from pandas import DataFrame, Series
from sqlalchemy import (
    Float,
    Enum,
    UniqueConstraint,
    Integer,
    ForeignKey,
    ResultProxy,
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.db import (
    or_none,
    Base,
    SerializableData,
    SerializableType,
    LocalInterestRates,
    ForeignInterestRates,
)


class HouseholdInterestRatePurposes(SerializableType):
    TOTAL = "TOTAL"
    HOUSING = "HOUSING"
    CONSUMER = "CONSUMER"
    CASH = "CASH"
    OTHER = "OTHER"

class HouseholdInterestRates(Base, SerializableData):
    __tablename__ = 'household_interest_rates'
    __table_args__ = (UniqueConstraint('purpose', 'year', 'month'),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    year: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
    purpose: Mapped[HouseholdInterestRatePurposes] = mapped_column(Enum(HouseholdInterestRatePurposes))

    local_rates_id: Mapped[int] = mapped_column(ForeignKey("local_interest_rates.id"), nullable=True)
    local_rates: Mapped[LocalInterestRates] = relationship(LocalInterestRates)
    foreign_rates_id: Mapped[int] = mapped_column(ForeignKey("foreign_interest_rates.id"), nullable=True)
    foreign_rates: Mapped[ForeignInterestRates] = relationship(ForeignInterestRates)
    total: Mapped[float] = mapped_column(Float, nullable=True)

    @classmethod
    async def insert(cls, session: AsyncSession, purpose: HouseholdInterestRatePurposes, year: int, month: int, row: DataFrame | Series, **extra_data) -> ResultProxy:
        local_rates: ResultProxy = await LocalInterestRates.insert(session, row.iloc[0:7])
        local_rates_id = local_rates.inserted_primary_key[0]

        foreign_rates: ResultProxy = await ForeignInterestRates.insert(session, row.iloc[7:12])
        foreign_rates_id = foreign_rates.inserted_primary_key[0]

        query = insert(cls).values(
            purpose=purpose,
            year=year,
            month=month,
            local_rates_id=local_rates_id,
            foreign_rates_id=foreign_rates_id,
            total=or_none(row.iloc[12]),
        ).on_conflict_do_nothing()
        return await session.execute(query)

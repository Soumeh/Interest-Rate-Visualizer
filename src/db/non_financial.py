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


class NonFinancialInterestRatePurposes(SerializableType):
    TOTAL = "TOTAL"
    CURRENT_ASSETS = "CURRENT_ASSETS"
    INVESTMENT = "INVESTMENT"
    OTHER = "OTHER"
    IMPORT = "IMPORT"
    FOREIGN = "FOREIGN"

class NonFinancialInterestRates(Base, SerializableData):
    __tablename__ = 'non_financial_interest_rates'
    __table_args__ = (UniqueConstraint('purpose', 'year', 'month'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
    purpose: Mapped[NonFinancialInterestRatePurposes] = mapped_column(Enum(NonFinancialInterestRatePurposes))

    local_rates_id: Mapped[int] = mapped_column(ForeignKey("local_interest_rates.id"), nullable=True)
    local_rates: Mapped[LocalInterestRates] = relationship(LocalInterestRates)
    foreign_rates_id: Mapped[int] = mapped_column(ForeignKey("foreign_interest_rates.id"), nullable=True)
    foreign_rates: Mapped[ForeignInterestRates] = relationship(ForeignInterestRates)
    total: Mapped[float] = mapped_column(Float, nullable=True)

    @classmethod
    async def insert(cls, session: AsyncSession, purpose: NonFinancialInterestRatePurposes, year: int, month: int, row: DataFrame | Series, **extra_data) -> ResultProxy:
        if not 'only_foreign_rates' in extra_data:
            local_rates: ResultProxy = await LocalInterestRates.insert(session, row.iloc[0:7])
            local_rates_id = local_rates.inserted_primary_key[0]
            foreign_rates: ResultProxy = await ForeignInterestRates.insert(session, row.iloc[7:12])
            foreign_rates_id = foreign_rates.inserted_primary_key[0]
            total = or_none(row.iloc[12])
        else:
            local_rates_id = None
            foreign_rates: ResultProxy = await ForeignInterestRates.insert(session, row.iloc[0:6])
            foreign_rates_id = foreign_rates.inserted_primary_key[0]
            total = None

        query = insert(cls).values(
            purpose=purpose,
            year=year,
            month=month,
            local_rates_id=local_rates_id,
            foreign_rates_id=foreign_rates_id,
            total=total,
        ).on_conflict_do_nothing()
        return await session.execute(query)

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
    SerializableTable,
    SerializableType,
    LocalInterestRates,
    ForeignInterestRates,
)


class HouseholdLoanPurposes(SerializableType):
    TOTAL = "Ukupno"
    HOUSING_LOANS = "Stambeni krediti"
    CONSUMER_LOANS = "Potrošački krediti"
    CASH_LOANS = "Gotovinski krediti"
    OTHER_LOANS = "Ostali krediti"

class HouseholdLoans(Base, SerializableTable):
    __tablename__ = 'household_loans'
    __table_args__ = (UniqueConstraint('purpose', 'year', 'month'),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    year: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
    purpose: Mapped[HouseholdLoanPurposes] = mapped_column(Enum(HouseholdLoanPurposes))

    local_rates_id: Mapped[int] = mapped_column(ForeignKey("local_interest_rates.id"), nullable=True)
    local_rates: Mapped[LocalInterestRates] = relationship(LocalInterestRates)
    foreign_rates_id: Mapped[int] = mapped_column(ForeignKey("foreign_interest_rates.id"), nullable=True)
    foreign_rates: Mapped[ForeignInterestRates] = relationship(ForeignInterestRates)
    total: Mapped[float] = mapped_column(Float, nullable=True)

    @classmethod
    async def insert(cls, session: AsyncSession, purpose: HouseholdLoanPurposes, year: int, month: int, row: DataFrame | Series, **extra_data) -> ResultProxy:
        local_rates: ResultProxy = await LocalInterestRates.insert(session, row.iloc[0:7])
        local_rates_id = local_rates.inserted_primary_key[0]

        foreign_rates: ResultProxy = await ForeignInterestRates.insert(session, row.iloc[7:12])
        foreign_rates_id = foreign_rates.inserted_primary_key[0]

        query = insert(cls).values(
            purpose=purpose.name,
            year=year,
            month=month,
            local_rates_id=local_rates_id,
            foreign_rates_id=foreign_rates_id,
            total=or_none(row.iloc[12]),
        ).on_conflict_do_nothing()
        return await session.execute(query)

    @classmethod
    async def process_frame(cls, session: AsyncSession, frame: DataFrame):
        from_top, to_bottom = cls._get_start_end_points(frame)
        date_frame: DataFrame = frame.iloc[from_top:to_bottom, 0:2]

        total_data = frame.iloc[from_top:to_bottom, 2:14]
        total_data[14] = Series()
        await cls._process_rows(session, date_frame, total_data, HouseholdLoanPurposes.TOTAL)

        housing_data = frame.iloc[from_top:to_bottom, 14:27]
        await cls._process_rows(session, date_frame, housing_data, HouseholdLoanPurposes.HOUSING_LOANS)

        consumer_data = frame.iloc[from_top:to_bottom, 27:40]
        await cls._process_rows(session, date_frame, consumer_data, HouseholdLoanPurposes.CONSUMER_LOANS)

        cash_data = frame.iloc[from_top:to_bottom, 40:53]
        await cls._process_rows(session, date_frame, cash_data, HouseholdLoanPurposes.CASH_LOANS)

        other_data = frame.iloc[from_top:to_bottom, 53:66]
        await cls._process_rows(session, date_frame, other_data, HouseholdLoanPurposes.OTHER_LOANS)

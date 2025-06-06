from pandas import DataFrame, Series
from sqlalchemy import UniqueConstraint, Integer, ForeignKey, Float, ResultProxy
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.db import Base, SerializableData, TotalInterestRates

class TotalLoansByCurrency(Base, SerializableData):
    __tablename__ = 'total_loans_by_currency'
    __table_args__ = (UniqueConstraint('year', 'month'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)

    rsd_rates_id: Mapped[int] = mapped_column(ForeignKey("total_interest_rates.id"), nullable=True)
    rsd_rates: Mapped[TotalInterestRates] = relationship(TotalInterestRates)

    eur_rates_id: Mapped[int] = mapped_column(ForeignKey("total_interest_rates.id"), nullable=True)
    eur_rates: Mapped[TotalInterestRates] = relationship(TotalInterestRates)

    chf_rates_id: Mapped[int] = mapped_column(ForeignKey("total_interest_rates.id"), nullable=True)
    chf_rates: Mapped[TotalInterestRates] = relationship(TotalInterestRates)

    other_rates_id: Mapped[int] = mapped_column(ForeignKey("total_interest_rates.id"), nullable=True)
    other_rates: Mapped[TotalInterestRates] = relationship(TotalInterestRates)

    total_rates_id: Mapped[int] = mapped_column(ForeignKey("total_interest_rates.id"), nullable=True)
    total_rates: Mapped[TotalInterestRates] = relationship(TotalInterestRates)

    household_total: Mapped[float] = mapped_column(Float, nullable=True)
    non_financial_total: Mapped[float] = mapped_column(Float, nullable=True)
    total: Mapped[float] = mapped_column(Float, nullable=True)

    @classmethod
    async def insert(cls, session: AsyncSession, purpose, year: int, month: int, row: DataFrame | Series, **extra_data) -> ResultProxy:
        rsd_rates: ResultProxy = await TotalInterestRates.insert(session, row.iloc[0:3])
        rsd_rates_id = rsd_rates.inserted_primary_key[0]

        eur_rates: ResultProxy = await TotalInterestRates.insert(session, row.iloc[3:6])
        eur_rates_id = eur_rates.inserted_primary_key[0]

        chf_rates: ResultProxy = await TotalInterestRates.insert(session, row.iloc[6:9])
        chf_rates_id = chf_rates.inserted_primary_key[0]

        other_rates: ResultProxy = await TotalInterestRates.insert(session, row.iloc[9:12])
        other_rates_id = other_rates.inserted_primary_key[0]

        total_rates: ResultProxy = await TotalInterestRates.insert(session, row.iloc[12:15])
        total_rates_id = total_rates.inserted_primary_key[0]

        household_total = row.iloc[15]
        non_financial_total = row.iloc[16]
        total = row.iloc[17]

        query = insert(cls).values(
            year=year,
            month=month,
            rsd_rates_id=rsd_rates_id,
            eur_rates_id=eur_rates_id,
            chf_rates_id=chf_rates_id,
            other_rates_id=other_rates_id,
            total_rates_id=total_rates_id,
            household_total=household_total,
            non_financial_total=non_financial_total,
            total=total,
        ).on_conflict_do_nothing()
        return await session.execute(query)

    @classmethod
    async def process_frame(cls, session: AsyncSession, frame: DataFrame):
        from_top, to_bottom = cls._get_start_end_points(frame)
        date_frame: DataFrame = frame.iloc[from_top:to_bottom, 0:2]

        total_data = frame.iloc[from_top:to_bottom, 2:-2]
        await cls._process_rows(session, date_frame, total_data, None)

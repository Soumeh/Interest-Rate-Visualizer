from pandas import DataFrame, Series
from sqlalchemy import UniqueConstraint, Integer, Float, ResultProxy, Enum
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped

from src.db import Base, SerializableTable, SerializableType


class TotalLoanPurposesByCurrency(SerializableType):
    TOTAL = "Ukupno"
    RSD = "Dinarski"
    EUR = "Krediti u EUR"
    CHF = "Krediti u CHF"
    OTHER = "Krediti u ostalim valutama"
    TOTAL_FOREIGN = "Krediti u stranim valutama"


class TotalLoansByCurrency(Base, SerializableTable):
    __tablename__ = "total_loans_by_currency"
    __table_args__ = (UniqueConstraint("year", "month", "purpose"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
    purpose: Mapped[TotalLoanPurposesByCurrency] = mapped_column(
        Enum(TotalLoanPurposesByCurrency)
    )

    household_total: Mapped[float] = mapped_column(Float, nullable=True)
    non_financial_total: Mapped[float] = mapped_column(Float, nullable=True)
    total: Mapped[float] = mapped_column(Float, nullable=True)

    @classmethod
    async def insert(
        cls,
        session: AsyncSession,
        purpose: TotalLoanPurposesByCurrency,
        year: int,
        month: int,
        row: DataFrame | Series,
        **extra_data,
    ) -> ResultProxy:
        household_total = row.iloc[0]
        non_financial_total = row.iloc[1]
        total = row.iloc[2]

        query = (
            insert(cls)
            .values(
                purpose=purpose.name,
                year=year,
                month=month,
                household_total=household_total,
                non_financial_total=non_financial_total,
                total=total,
            )
            .on_conflict_do_nothing()
        )
        return await session.execute(query)

    @classmethod
    async def process_frame(cls, session: AsyncSession, frame: DataFrame):
        from_top, to_bottom = cls._get_start_end_points(frame)
        date_frame: DataFrame = frame.iloc[from_top:to_bottom, 0:2]

        rsd_data = frame.iloc[from_top:to_bottom, 2:5]
        await cls._process_rows(
            session, date_frame, rsd_data, TotalLoanPurposesByCurrency.RSD
        )

        eur_data = frame.iloc[from_top:to_bottom, 5:8]
        await cls._process_rows(
            session, date_frame, eur_data, TotalLoanPurposesByCurrency.EUR
        )

        chf_data = frame.iloc[from_top:to_bottom, 8:11]
        await cls._process_rows(
            session, date_frame, chf_data, TotalLoanPurposesByCurrency.CHF
        )

        total_foreign_data = frame.iloc[from_top:to_bottom, 11:14]
        await cls._process_rows(
            session,
            date_frame,
            total_foreign_data,
            TotalLoanPurposesByCurrency.TOTAL_FOREIGN,
        )

        total_data = frame.iloc[from_top:to_bottom, 14:17]
        await cls._process_rows(
            session, date_frame, total_data, TotalLoanPurposesByCurrency.TOTAL
        )

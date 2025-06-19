from dash.html import Figure
from pandas import DataFrame, Series, concat, melt
from plotly import express
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
from sqlalchemy.orm import mapped_column, Mapped, relationship, scoped_session

from src.db import (
    or_none,
    Base,
    SerializableTable,
    SerializableType,
    EnterpriseInterestRates,
)


class NonFinancialTermDepositPurposesBySize(SerializableType):
    MICRO = "Mirko Preduzeće"
    SMALL = "Malo Preduzeće"
    MEDIUM = "Srednje Preduzeće"
    LARGE = "Veliko Preduzeće"
    TOTAL = "Ukupno"

class NonFinancialTermDepositsBySize(Base, SerializableTable):
    __tablename__ = "non_financial_term_deposits_by_size"
    __table_args__ = (UniqueConstraint("purpose", "year", "month"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
    purpose: Mapped[NonFinancialTermDepositPurposesBySize] = mapped_column(
        Enum(NonFinancialTermDepositPurposesBySize)
    )

    local_enterprise_interest_rates_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("enterprise_interest_rates.id"), nullable=True
    )
    foreign_enterprise_interest_rates_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("enterprise_interest_rates.id"), nullable=True
    )

    local_enterprise_interest_rates: Mapped[EnterpriseInterestRates] = relationship(
        EnterpriseInterestRates, foreign_keys=[local_enterprise_interest_rates_id]
    )
    foreign_enterprise_interest_rates: Mapped[EnterpriseInterestRates] = relationship(
        EnterpriseInterestRates, foreign_keys=[foreign_enterprise_interest_rates_id]
    )

    local_total: Mapped[float] = mapped_column(Float, nullable=True)
    foreign_total: Mapped[float] = mapped_column(Float, nullable=True)

    @classmethod
    async def insert(
        cls,
        session: AsyncSession,
        purpose: NonFinancialTermDepositPurposesBySize,
        year: int,
        month: int,
        row: DataFrame | Series,
        **extra_data,
    ) -> ResultProxy:
        if purpose == NonFinancialTermDepositPurposesBySize.TOTAL:
            query = (
                insert(cls)
                .values(
                    purpose=purpose.name,
                    year=year,
                    month=month,
                    local_enterprise_interest_rates_id=None,
                    foreign_enterprise_interest_rates_id=None,
                    local_total=or_none(row.iloc[0]),
                    foreign_total=or_none(row.iloc[1]),
                )
                .on_conflict_do_nothing()
            )
            return await session.execute(query)

        local_enterprise_interest_rates: ResultProxy = (
            await EnterpriseInterestRates.insert(session, row.iloc[0:3])
        )
        local_enterprise_interest_rates_id = (
            local_enterprise_interest_rates.inserted_primary_key[0]
        )
        local_total = or_none(row.iloc[3])

        foreign_enterprise_interest_rates: ResultProxy = (
            await EnterpriseInterestRates.insert(session, row.iloc[4:7])
        )
        foreign_enterprise_interest_rates_id = (
            foreign_enterprise_interest_rates.inserted_primary_key[0]
        )
        foreign_total = or_none(row.iloc[7])

        query = (
            insert(cls)
            .values(
                purpose=purpose.name,
                year=year,
                month=month,
                local_enterprise_interest_rates_id=local_enterprise_interest_rates_id,
                foreign_enterprise_interest_rates_id=foreign_enterprise_interest_rates_id,
                local_total=local_total,
                foreign_total=foreign_total,
            )
            .on_conflict_do_nothing()
        )
        return await session.execute(query)

    @classmethod
    async def process_frame(cls, session: AsyncSession, frame: DataFrame):
        from_top, from_bottom = cls._get_start_end_points(frame)
        date_frame: DataFrame = frame.iloc[from_top:from_bottom, 0:2]

        local_micro_data = frame.iloc[from_top:from_bottom, 2:6]
        foreign_micro_data = frame.iloc[from_top:from_bottom, 19:23]
        micro_data = concat([local_micro_data, foreign_micro_data], axis=1)
        await cls._process_rows(
            session, date_frame, micro_data, NonFinancialTermDepositPurposesBySize.MICRO
        )

        local_small_data = frame.iloc[from_top:from_bottom, 6:10]
        foreign_small_data = frame.iloc[from_top:from_bottom, 23:27]
        small_data = concat([local_small_data, foreign_small_data], axis=1)
        await cls._process_rows(
            session, date_frame, small_data, NonFinancialTermDepositPurposesBySize.SMALL
        )

        local_medium_data = frame.iloc[from_top:from_bottom, 10:14]
        foreign_medium_data = frame.iloc[from_top:from_bottom, 27:31]
        medium_data = concat([local_medium_data, foreign_medium_data], axis=1)
        await cls._process_rows(
            session, date_frame, medium_data, NonFinancialTermDepositPurposesBySize.MEDIUM
        )

        local_large_data = frame.iloc[from_top:from_bottom, 14:18]
        foreign_large_data = frame.iloc[from_top:from_bottom, 31:35]
        large_data = concat([local_large_data, foreign_large_data], axis=1)
        await cls._process_rows(
            session, date_frame, large_data, NonFinancialTermDepositPurposesBySize.LARGE
        )

        local_total = frame.iloc[from_top:from_bottom, 18:19]
        foreign_total = frame.iloc[from_top:from_bottom, 35:36]
        total_data = concat([local_total, foreign_total], axis=1)
        await cls._process_rows(
            session, date_frame, total_data, NonFinancialTermDepositPurposesBySize.TOTAL
        )

    @classmethod
    def query(cls, session: scoped_session):
        return session.query(cls, EnterpriseInterestRates).join(EnterpriseInterestRates)

    def to_express(self, data: DataFrame, theme: str) -> Figure:
        columns = [
            "local_total",
            "foreign_total",
        ]
        labels = {
            "local_total": "Ukupno lokalno",
            "foreign_total": "Ukupno strano",
        }
        melted_df = melt(
            data,
            id_vars=["month_name"],
            value_vars=columns,
            var_name="key",
            value_name="rate",
        )
        melted_df["key"] = melted_df["key"].map(labels)
        return express.line(
            melted_df,
            x="month_name",
            y="rate",
            color="key",
            labels={"month_name": "Mesec", "rate": "Kamatna stopa"},
            template=theme,
        )

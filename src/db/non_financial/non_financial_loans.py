from dash.html import Figure
from pandas import DataFrame, Series, melt
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

from src.db import or_none, Base, SerializableTable, SerializableType
from src.db.generic import LocalInterestRates, ForeignInterestRates


class NonFinancialLoanPurposes(SerializableType):
    TOTAL = "Ukupno"
    CURRENT_ASSETS = "Krediti za obrtna sredstva"
    INVESTMENT = "Investicioni krediti"
    OTHER_LOCAL_LOANS = "Ostali dinarski krediti"
    IMPORTS = "Krediti za uvoz"
    OTHER_FOREIGN_LOANS = "Ostali devizni krediti"


class NonFinancialLoans(Base, SerializableTable):
    __tablename__ = "non_financial_loans"
    __table_args__ = (UniqueConstraint("purpose", "year", "month"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
    purpose: Mapped[NonFinancialLoanPurposes] = mapped_column(
        Enum(NonFinancialLoanPurposes)
    )

    local_rates_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("local_interest_rates.id"), nullable=True
    )
    foreign_rates_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("foreign_interest_rates.id"), nullable=True
    )
    local_rates: Mapped[LocalInterestRates] = relationship(
        "LocalInterestRates", foreign_keys=[local_rates_id], lazy="joined"
    )
    foreign_rates: Mapped[ForeignInterestRates] = relationship(
        "ForeignInterestRates", foreign_keys=[foreign_rates_id], lazy="joined"
    )

    total: Mapped[float] = mapped_column(Float, nullable=True)

    @classmethod
    async def insert(
        cls,
        session: AsyncSession,
        purpose: NonFinancialLoanPurposes,
        year: int,
        month: int,
        row: DataFrame | Series,
        **extra_data,
    ) -> ResultProxy:
        if "only_foreign_rates" not in extra_data:
            local_rates: ResultProxy = await LocalInterestRates.insert(
                session, row.iloc[0:7]
            )
            local_rates_id = local_rates.inserted_primary_key[0]
            foreign_rates: ResultProxy = await ForeignInterestRates.insert(
                session, row.iloc[7:12]
            )
            foreign_rates_id = foreign_rates.inserted_primary_key[0]
            total = or_none(row.iloc[12])
        else:
            local_rates_id = None
            foreign_rates: ResultProxy = await ForeignInterestRates.insert(
                session, row.iloc[0:6]
            )
            foreign_rates_id = foreign_rates.inserted_primary_key[0]
            total = None

        query = (
            insert(cls)
            .values(
                purpose=purpose.name,
                year=year,
                month=month,
                local_rates_id=local_rates_id,
                foreign_rates_id=foreign_rates_id,
                total=total,
            )
            .on_conflict_do_nothing()
        )
        return await session.execute(query)

    @classmethod
    async def process_frame(cls, session: AsyncSession, frame: DataFrame):
        from_top, from_bottom = cls._get_start_end_points(frame)
        date_frame: DataFrame = frame.iloc[from_top:from_bottom, 0:2]

        total_data = frame.iloc[from_top:from_bottom, 2:14]
        total_data[14] = Series()
        await cls._process_rows(
            session, date_frame, total_data, NonFinancialLoanPurposes.TOTAL
        )

        current_data = frame.iloc[from_top:from_bottom, 14:27]
        await cls._process_rows(
            session, date_frame, current_data, NonFinancialLoanPurposes.CURRENT_ASSETS
        )

        investment_data = frame.iloc[from_top:from_bottom, 27:40]
        await cls._process_rows(
            session, date_frame, investment_data, NonFinancialLoanPurposes.INVESTMENT
        )

        other_data = frame.iloc[from_top:from_bottom, 40:53]
        await cls._process_rows(
            session, date_frame, other_data, NonFinancialLoanPurposes.OTHER_LOCAL_LOANS
        )

        total_data = frame.iloc[from_top:from_bottom, 53:58]
        await cls._process_rows(
            session,
            date_frame,
            total_data,
            NonFinancialLoanPurposes.IMPORTS,
            only_foreign_rates=True,
        )

        other_imports_data = frame.iloc[from_top:from_bottom, 58:63]
        await cls._process_rows(
            session,
            date_frame,
            other_imports_data,
            NonFinancialLoanPurposes.OTHER_LOCAL_LOANS,
            only_foreign_rates=True,
        )

    @classmethod
    def query(cls, session: scoped_session):
        return (
            session.query(cls, LocalInterestRates, ForeignInterestRates)
            .join(LocalInterestRates)
            .join(ForeignInterestRates)
        )

    def to_express(self, data: DataFrame, theme: str) -> Figure:
        columns = ["local_rates.total_local", "foreign_rates.total_foreign", "total"]
        labels = {
            "local_rates.total_local": "Ukupno lokalno",
            "foreign_rates.total_foreign": "Ukupno strano",
            "total": "Ukupno",
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

    def get_columns(self):
        return [
            {"id": "year", "name": "Godina"},
            {"id": "month_name", "name": "Mesec"},
            {"id": "local_rates.total_local", "name": "Ukupno lokalno"},
            {"id": "foreign_rates.total_foreign", "name": "Ukupno strano"},
            {"id": "total", "name": "Ukupno"},
        ]

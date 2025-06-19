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


class HouseholdTermDepositPurposes(SerializableType):
	TOTAL = "Ukupno"
	UP_TO_ONE = "Oročeni depoziti do 1 godine"
	ONE_UP_TO_TWO = "Oročeni depoziti preko 1 do 2 godine"
	OVER_TWO = "Oročeni depoziti preko 2 godine"

class HouseholdTermDeposits(Base, SerializableTable):
	__tablename__ = "household_term_deposits"
	__table_args__ = (UniqueConstraint("purpose", "year", "month"),)

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	year: Mapped[int] = mapped_column(Integer)
	month: Mapped[int] = mapped_column(Integer)
	purpose: Mapped[HouseholdTermDepositPurposes] = mapped_column(
		Enum(HouseholdTermDepositPurposes)
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
		purpose: HouseholdTermDepositPurposes,
		year: int,
		month: int,
		row: DataFrame | Series,
		**extra_data,
	) -> ResultProxy:
		local_rates: ResultProxy = await LocalInterestRates.insert(
			session, row.iloc[0:7]
		)
		local_rates_id = local_rates.inserted_primary_key[0]

		foreign_rates: ResultProxy = await ForeignInterestRates.insert(
			session, row.iloc[7:12]
		)
		foreign_rates_id = foreign_rates.inserted_primary_key[0]

		query = (
			insert(cls)
			.values(
				purpose=purpose.name,
				year=year,
				month=month,
				local_rates_id=local_rates_id,
				foreign_rates_id=foreign_rates_id,
				total=or_none(row.iloc[12]),
			)
			.on_conflict_do_nothing()
		)
		return await session.execute(query)

	@classmethod
	async def process_frame(cls, session: AsyncSession, frame: DataFrame):
		from_top, to_bottom = cls._get_start_end_points(frame)
		date_frame: DataFrame = frame.iloc[from_top:to_bottom, 0:2]

		total_data = frame.iloc[from_top:to_bottom, 2:14]
		total_data[14] = Series()
		await cls._process_rows(
			session, date_frame, total_data, HouseholdTermDepositPurposes.TOTAL
		)

		housing_data = frame.iloc[from_top:to_bottom, 14:27]
		await cls._process_rows(
			session, date_frame, housing_data, HouseholdTermDepositPurposes.UP_TO_ONE
		)

		consumer_data = frame.iloc[from_top:to_bottom, 27:40]
		await cls._process_rows(
			session,
			date_frame,
			consumer_data,
			HouseholdTermDepositPurposes.ONE_UP_TO_TWO,
		)

		cash_data = frame.iloc[from_top:to_bottom, 40:53]
		await cls._process_rows(
			session, date_frame, cash_data, HouseholdTermDepositPurposes.OVER_TWO
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
			{"id": "godina", "name": "Godina"},
			{"id": "month_name", "name": "Mesec"},
			{"id": "local_rates.total_local", "name": "Ukupno lokalno"},
			{"id": "foreign_rates.total_foreign", "name": "Ukupno strano"},
			{"id": "total", "name": "Ukupno"},
		]

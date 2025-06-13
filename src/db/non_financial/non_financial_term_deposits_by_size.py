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
from sqlalchemy.orm import mapped_column, Mapped, relationship, scoped_session

from src.db import (
	or_none,
	Base,
	SerializableTable,
	SerializableType,
	EnterpriseInterestRates,
)


class NonFinancialTermDepositPurposesBySize(SerializableType):
	LOCAL = "LOCAL"
	FOREIGN = "FOREIGN"


class NonFinancialTermDepositsBySize(Base, SerializableTable):
	__tablename__ = "non_financial_term_deposits_by_size"
	__table_args__ = (UniqueConstraint("purpose", "year", "month"),)

	id: Mapped[int] = mapped_column(primary_key=True)
	year: Mapped[int] = mapped_column(Integer)
	month: Mapped[int] = mapped_column(Integer)
	purpose: Mapped[NonFinancialTermDepositPurposesBySize] = mapped_column(Enum(NonFinancialTermDepositPurposesBySize))

	micro_enterprises_id: Mapped[int] = mapped_column(Integer, ForeignKey("enterprise_interest_rates.id"), nullable=True)
	small_enterprises_id: Mapped[int] = mapped_column(Integer, ForeignKey("enterprise_interest_rates.id"), nullable=True)
	medium_enterprises_id: Mapped[int] = mapped_column(Integer, ForeignKey("enterprise_interest_rates.id"), nullable=True)
	large_enterprises_id: Mapped[int] = mapped_column(Integer, ForeignKey("enterprise_interest_rates.id"), nullable=True)

	micro_enterprises: Mapped[EnterpriseInterestRates] = relationship(EnterpriseInterestRates, foreign_keys=[micro_enterprises_id])
	small_enterprises: Mapped[EnterpriseInterestRates] = relationship(EnterpriseInterestRates, foreign_keys=[small_enterprises_id])
	medium_enterprises: Mapped[EnterpriseInterestRates] = relationship(EnterpriseInterestRates, foreign_keys=[medium_enterprises_id])
	large_enterprises: Mapped[EnterpriseInterestRates] = relationship(EnterpriseInterestRates, foreign_keys=[large_enterprises_id])

	total: Mapped[float] = mapped_column(Float, nullable=True)

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
		micro_enterprises: ResultProxy = await EnterpriseInterestRates.insert(
			session, row.iloc[0:4]
		)
		micro_enterprises_id = micro_enterprises.inserted_primary_key[0]
		small_enterprises: ResultProxy = await EnterpriseInterestRates.insert(
			session, row.iloc[4:8]
		)
		small_enterprises_id = small_enterprises.inserted_primary_key[0]
		medium_enterprises: ResultProxy = await EnterpriseInterestRates.insert(
			session, row.iloc[8:12]
		)
		medium_enterprises_id = medium_enterprises.inserted_primary_key[0]
		large_enterprises: ResultProxy = await EnterpriseInterestRates.insert(
			session, row.iloc[12:16]
		)
		large_enterprises_id = large_enterprises.inserted_primary_key[0]

		total = or_none(row.iloc[16])

		query = (
			insert(cls)
			.values(
				purpose=purpose.name,
				year=year,
				month=month,
				micro_enterprises_id=micro_enterprises_id,
				small_enterprises_id=small_enterprises_id,
				medium_enterprises_id=medium_enterprises_id,
				large_enterprises_id=large_enterprises_id,
				total=total,
			)
			.on_conflict_do_nothing()
		)
		return await session.execute(query)

	@classmethod
	async def process_frame(cls, session: AsyncSession, frame: DataFrame):
		from_top, from_bottom = cls._get_start_end_points(frame)
		date_frame: DataFrame = frame.iloc[from_top:from_bottom, 0:2]

		total_data = frame.iloc[from_top:from_bottom, 2:19]
		await cls._process_rows(
			session, date_frame, total_data, NonFinancialTermDepositPurposesBySize.LOCAL
		)

		current_data = frame.iloc[from_top:from_bottom, 19:36]
		await cls._process_rows(
			session,
			date_frame,
			current_data,
			NonFinancialTermDepositPurposesBySize.FOREIGN,
		)

	@classmethod
	def query(cls, session: scoped_session):
		return session.query(cls, EnterpriseInterestRates).join(EnterpriseInterestRates)

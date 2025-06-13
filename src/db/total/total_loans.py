from sqlalchemy import UniqueConstraint, Integer, Enum
from sqlalchemy.orm import mapped_column, Mapped, scoped_session

from src.db import Base, SerializableTable, SerializableType


class TotalLoanPurposes(SerializableType):
	TEST = "test"


class TotalLoans(Base, SerializableTable):
	__tablename__ = "total_loans"
	__table_args__ = (UniqueConstraint("year", "month"),)

	id: Mapped[int] = mapped_column(primary_key=True)
	year: Mapped[int] = mapped_column(Integer)
	month: Mapped[int] = mapped_column(Integer)
	purpose: Mapped[TotalLoanPurposes] = mapped_column(Enum(TotalLoanPurposes))

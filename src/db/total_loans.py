from sqlalchemy import UniqueConstraint, Integer
from sqlalchemy.orm import mapped_column, Mapped

from src.db import Base, SerializableData


class TotalLoans(Base, SerializableData):
    __tablename__ = 'total_loans'
    __table_args__ = (UniqueConstraint('year', 'month'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
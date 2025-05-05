from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class InterestRate(Base):
    __tablename__ = "test"

    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    month = Column(Integer)

    non_indexed = Column(Float)
    reference_rate = Column(Float)
    belibor_1m = Column(Float)
    belibor_3m = Column(Float)
    belibor_6m = Column(Float)
    other_indexations = Column(Float)
    total = Column(Float)

    eur = Column(Float)
    chf = Column(Float)
    usd = Column(Float)
    other_currencies = Column(Float)
    total_foreign_currency = Column(Float)

    # name = Column(String(50), nullable=False)
    # location = Column(String(100))

    # employees = relationship("Employee", back_populates="department")

    # def __repr__(self):
    #     return f"<Department(id={self.id}, name='{self.name}', location='{self.location}')>"

class ConsumerInterestRate(InterestRate):
    pass
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Test(Base):
    __tablename__ = "test"

    # id = Column(Integer, primary_key=True)
    # name = Column(String(50), nullable=False)
    # location = Column(String(100))

    # employees = relationship("Employee", back_populates="department")

    # def __repr__(self):
    #     return f"<Department(id={self.id}, name='{self.name}', location='{self.location}')>"

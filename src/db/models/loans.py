from src.db.models import Base, GenericData

class TotalLoans(Base, GenericData):
    __tablename__ = "total_loans"

class HousingLoans(Base, GenericData):
    __tablename__ = "housing_loans"

class ConsumerLoans(Base, GenericData):
    __tablename__ = "consumer_loans"

class CashLoans(Base, GenericData):
    __tablename__ = "cash_loans"

class OtherLoans(Base, GenericData):
    __tablename__ = "other_loans"

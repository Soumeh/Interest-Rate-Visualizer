from src.db.models import Base, GenericData

class TotalInterestRates(Base, GenericData):
    __tablename__ = "total_interest_rates"

class HousingInterestRates(Base, GenericData):
    __tablename__ = "housing_interest_rates"

class ConsumerInterestRates(Base, GenericData):
    __tablename__ = "consumer_interest_rates"

class CashInterestRates(Base, GenericData):
    __tablename__ = "cash_interest_rates"

class OtherInterestRates(Base, GenericData):
    __tablename__ = "other_interest_rates"

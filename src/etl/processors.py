from numpy import isnan
from pandas import DataFrame, Series
from sqlalchemy.orm import Session

from src.common.test import month_to_integer
from src.db import Base, SerializableData
from src.db.housing import HouseholdInterestRates, HouseholdLoans, HouseholdDataType
from src.db.non_financial import (
    NonFinancialDataType,
    NonFinancialInterestRates,
    NonFinancialImportsInterestRates,
    NonFinancialImportsDataType,
)


def process_table(session: Session, date_frame: DataFrame, table_frame: DataFrame, table: type[Base, SerializableData], **extra_data):
    previous_year = None
    index: int = 0
    for i, row in table_frame.iterrows():
        try:
            date = date_frame.iloc[index]
            index += 1
            year = date.iloc[0]
            if isnan(year):
                year = previous_year
            else:
                year = int(year)
                previous_year = year
            month = month_to_integer(date.iloc[1])

            query = table.query_insert(year, month, row, **extra_data)
            session.execute(query)
        except Exception as exception:
            print(f"Error processing row {i}: {exception}")

def process_population_interest_rates(session: Session, frame: DataFrame):
    date_frame: DataFrame = frame.iloc[11:-5, 0:2]

    total_interest_rates_data = frame.iloc[11:-5, 2:14]
    total_interest_rates_data[14] = Series()
    process_table(session, date_frame, total_interest_rates_data, HouseholdInterestRates, data_type = HouseholdDataType.TOTAL)

    housing_interest_rates_data = frame.iloc[11:-5, 14:27]
    process_table(session, date_frame, housing_interest_rates_data, HouseholdInterestRates, data_type = HouseholdDataType.HOUSING)

    consumer_interest_rates_data = frame.iloc[11:-5, 27:40]
    process_table(session, date_frame, consumer_interest_rates_data, HouseholdInterestRates, data_type = HouseholdDataType.CONSUMER)

    cash_interest_rates_data = frame.iloc[11:-5, 40:53]
    process_table(session, date_frame, cash_interest_rates_data, HouseholdInterestRates, data_type = HouseholdDataType.CASH)

    other_interest_rates_data = frame.iloc[11:-5, 53:66]
    process_table(session, date_frame, other_interest_rates_data, HouseholdInterestRates, data_type = HouseholdDataType.OTHER)

def process_population_loans(session: Session, frame: DataFrame):
    date_frame: DataFrame = frame.iloc[11:-5, 0:2]

    total_loans_data = frame.iloc[11:-5, 2:14]
    total_loans_data[14] = Series()
    process_table(session, date_frame, total_loans_data, HouseholdLoans, data_type = HouseholdDataType.TOTAL)

    housing_loans_data = frame.iloc[11:-5, 14:27]
    process_table(session, date_frame, housing_loans_data, HouseholdLoans, data_type = HouseholdDataType.HOUSING)

    consumer_loans_data = frame.iloc[11:-5, 27:40]
    process_table(session, date_frame, consumer_loans_data, HouseholdLoans, data_type = HouseholdDataType.CONSUMER)

    cash_loans_data = frame.iloc[11:-5, 40:53]
    process_table(session, date_frame, cash_loans_data, HouseholdLoans, data_type = HouseholdDataType.CASH)

    other_loans_data = frame.iloc[11:-5, 53:66]
    process_table(session, date_frame, other_loans_data, HouseholdLoans, data_type = HouseholdDataType.OTHER)

def process_non_financial_interest_rates(session: Session, frame: DataFrame):
    date_frame: DataFrame = frame.iloc[11:-5, 0:2]

    total_imports_data = frame.iloc[11:-5, 2:14]
    total_imports_data[14] = Series()
    process_table(session, date_frame, total_imports_data, NonFinancialInterestRates, data_type = NonFinancialDataType.TOTAL)

    current_assets_data = frame.iloc[11:-5, 14:27]
    process_table(session, date_frame, current_assets_data, NonFinancialInterestRates, data_type = NonFinancialDataType.CURRENT_ASSETS)

    investment_data = frame.iloc[11:-5, 27:40]
    process_table(session, date_frame, investment_data, NonFinancialInterestRates, data_type = NonFinancialDataType.INVESTMENT)

    other_data = frame.iloc[11:-5, 40:53]
    process_table(session, date_frame, other_data, NonFinancialInterestRates, data_type = NonFinancialDataType.OTHER)


    total_imports_data = frame.iloc[11:-5, 53:58]
    process_table(session, date_frame, total_imports_data, NonFinancialImportsInterestRates, data_type = NonFinancialImportsDataType.TOTAL)

    other_imports_data = frame.iloc[11:-5, 58:63]
    process_table(session, date_frame, other_imports_data, NonFinancialImportsInterestRates, data_type = NonFinancialImportsDataType.OTHER)

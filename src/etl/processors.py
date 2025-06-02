from numpy import isnan
from pandas import DataFrame, Series
from sqlalchemy.orm import Session
from sqlalchemy import insert, inspect

from src.common.test import month_to_integer
from src.db.models import BankingData, BankingDataType, HouseholdInterestRates, HouseholdLoans, Base


def process_table(session: Session, date_frame: DataFrame, table_frame: DataFrame, table_type: type[BankingData], data_type: BankingDataType):
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

            rate = table_type.from_row(data_type.value, year, month, row)
            session.add(rate)
        except Exception as exception:
            print(f"Error processing row {i}: {exception}")

def process_population_interest_rates(session: Session, frame: DataFrame):
    date_frame: DataFrame = frame.iloc[11:-5, 0:2]

    total_interest_rates_data = frame.iloc[11:-5, 2:14]
    total_interest_rates_data[14] = Series()
    process_table(session, date_frame, total_interest_rates_data, HouseholdInterestRates, BankingDataType.TOTAL)

    housing_interest_rates_data = frame.iloc[11:-5, 14:27]
    process_table(session, date_frame, housing_interest_rates_data, HouseholdInterestRates, BankingDataType.HOUSING)

    consumer_interest_rates_data = frame.iloc[11:-5, 27:40]
    process_table(session, date_frame, consumer_interest_rates_data, HouseholdInterestRates, BankingDataType.CONSUMER)

    cash_interest_rates_data = frame.iloc[11:-5, 40:53]
    process_table(session, date_frame, cash_interest_rates_data, HouseholdInterestRates, BankingDataType.CASH)

    other_interest_rates_data = frame.iloc[11:-5, 53:66]
    process_table(session, date_frame, other_interest_rates_data, HouseholdInterestRates, BankingDataType.OTHER)

def process_population_loans(session: Session, frame: DataFrame):
    date_frame: DataFrame = frame.iloc[11:-5, 0:2]

    total_loans_data = frame.iloc[11:-5, 2:14]
    total_loans_data[14] = Series()
    process_table(session, date_frame, total_loans_data, HouseholdLoans, BankingDataType.TOTAL)

    housing_loans_data = frame.iloc[11:-5, 14:27]
    process_table(session, date_frame, housing_loans_data, HouseholdLoans, BankingDataType.HOUSING)

    consumer_loans_data = frame.iloc[11:-5, 27:40]
    process_table(session, date_frame, consumer_loans_data, HouseholdLoans, BankingDataType.CONSUMER)

    cash_loans_data = frame.iloc[11:-5, 40:53]
    process_table(session, date_frame, cash_loans_data, HouseholdLoans, BankingDataType.CASH)

    other_loans_data = frame.iloc[11:-5, 53:66]
    process_table(session, date_frame, other_loans_data, HouseholdLoans, BankingDataType.OTHER)

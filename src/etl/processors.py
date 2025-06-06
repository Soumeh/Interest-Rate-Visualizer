from typing import Tuple

from numpy import isnan
from pandas import DataFrame, Series
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.month_matcher import month_to_integer
from src.db import Base, SerializableData, SerializableType
from src.db.housing import HouseholdInterestRates, HouseholdInterestRatePurposes
from src.db.non_financial import (
    NonFinancialInterestRates,
    NonFinancialInterestRatePurposes,
)

def get_start_end_points(frame: DataFrame) -> Tuple[int, int]:
    start = 0
    while month_to_integer(str(frame.iloc[start, 1])) is None:
        start += 1
    end = 0
    while month_to_integer(str(frame.iloc[end, 1])) is None:
        end -= 1
    end += 1
    return start, end

async def process_table(session: AsyncSession, date_frame: DataFrame, table_frame: DataFrame, table: type[Base, SerializableData], purpose: type[SerializableType], **extra_data):
    previous_year = None
    index: int = 0
    try:
        for i, row in table_frame.iterrows():
            date = date_frame.iloc[index]
            index += 1
            year = date.iloc[0]
            if isnan(year):
                year = previous_year
            else:
                year = int(year)
                previous_year = year
            month = month_to_integer(date.iloc[1])

            await table.insert(session, purpose, year, month, row, **extra_data)

    except Exception as exception:
        print(f"Error processing row {i}: {exception}")

async def process_population_interest_rates(session: AsyncSession, frame: DataFrame):
    from_top, to_bottom = get_start_end_points(frame)
    date_frame: DataFrame = frame.iloc[from_top:to_bottom, 0:2]

    total_data = frame.iloc[from_top:to_bottom, 2:14]
    total_data[14] = Series()
    await process_table(session, date_frame, total_data, HouseholdInterestRates, HouseholdInterestRatePurposes.TOTAL)

    housing_data = frame.iloc[from_top:to_bottom, 14:27]
    await process_table(session, date_frame, housing_data, HouseholdInterestRates, HouseholdInterestRatePurposes.HOUSING)

    consumer_data = frame.iloc[from_top:to_bottom, 27:40]
    await process_table(session, date_frame, consumer_data, HouseholdInterestRates, HouseholdInterestRatePurposes.CONSUMER)

    cash_data = frame.iloc[from_top:to_bottom, 40:53]
    await process_table(session, date_frame, cash_data, HouseholdInterestRates, HouseholdInterestRatePurposes.CASH)

    other_data = frame.iloc[from_top:to_bottom, 53:66]
    await process_table(session, date_frame, other_data, HouseholdInterestRates, HouseholdInterestRatePurposes.OTHER)

async def process_non_financial_interest_rates(session: AsyncSession, frame: DataFrame):
    from_top, from_bottom = get_start_end_points(frame)
    date_frame: DataFrame = frame.iloc[from_top:from_bottom, 0:2]

    total_data = frame.iloc[from_top:from_bottom, 2:14]
    total_data[14] = Series()
    await process_table(session, date_frame, total_data, NonFinancialInterestRates, NonFinancialInterestRatePurposes.TOTAL)

    current_data = frame.iloc[from_top:from_bottom, 14:27]
    await process_table(session, date_frame, current_data, NonFinancialInterestRates, NonFinancialInterestRatePurposes.CURRENT_ASSETS)

    investment_data = frame.iloc[from_top:from_bottom, 27:40]
    await process_table(session, date_frame, investment_data, NonFinancialInterestRates, NonFinancialInterestRatePurposes.INVESTMENT)

    other_data = frame.iloc[from_top:from_bottom, 40:53]
    await process_table(session, date_frame, other_data, NonFinancialInterestRates, NonFinancialInterestRatePurposes.OTHER)

    total_data = frame.iloc[from_top:from_bottom, 53:58]
    await process_table(session, date_frame, total_data, NonFinancialInterestRates, NonFinancialInterestRatePurposes.IMPORT, only_foreign_rates = True)

    other_imports_data = frame.iloc[from_top:from_bottom, 58:63]
    await process_table(session, date_frame, other_imports_data, NonFinancialInterestRates, NonFinancialInterestRatePurposes.OTHER, only_foreign_rates = True)

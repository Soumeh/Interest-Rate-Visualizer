import os

import pandas as pd
import plotly.express as px
import sqlalchemy
from django.template import Engine
from dotenv import load_dotenv
from pandas.core.interchange.dataframe_protocol import DataFrame

from src.db.models import BankingDataType, HouseholdInterestRates

load_dotenv()
engine: Engine = sqlalchemy.create_engine(os.getenv("DATABASE_URL"))
total_household_interest_rates: DataFrame = HouseholdInterestRates.frame_by_type(engine, BankingDataType.TOTAL)

def create_total_by_month_graph(frame_year, template):
    """Create a line chart showing totals by month."""
    return px.line(
        frame_year,
        x="month_name",
        y="total",
        labels={"month_name": "Mesec", "total": "Ukupno"},
        template=template
    )


def create_currency_comparison_graph(frame_year, template):
    """Create a bar chart comparing different currencies."""
    # Melt the dataframe to get currency columns in a format suitable for a bar chart
    currency_cols = ['eur', 'chf', 'usd', 'other_currencies']
    currency_labels = {
        'eur': 'EUR',
        'chf': 'CHF',
        'usd': 'USD',
        'other_currencies': 'Ostale valute'
    }

    melted_df = pd.melt(
        frame_year,
        id_vars=['month_name'],
        value_vars=currency_cols,
        var_name='currency',
        value_name='rate'
    )

    # Map currency codes to readable names
    melted_df['currency'] = melted_df['currency'].map(currency_labels)

    return px.bar(
        melted_df,
        x='month_name',
        y='rate',
        color='currency',
        labels={"month_name": "Mesec", "rate": "Kamatna stopa", "currency": "Valuta"},
        template=template
    )


GRAPH_TYPE_TRANSLATIONS = {
    'total_by_month': 'Ukupne kamatne stope po mesecu',
    'currency_comparison': 'Poređenje kamatnih stopa po valutama'
}

GRAPH_TYPE_FUNCTIONS = {
    'total_by_month': create_total_by_month_graph,
    'currency_comparison': create_currency_comparison_graph
}



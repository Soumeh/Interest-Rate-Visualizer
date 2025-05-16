import os

import pandas as pd
import plotly.express as px
import sqlalchemy
from dash import Dash, html, dcc, callback, Output, Input
from dotenv import load_dotenv

load_dotenv()
app = Dash(__name__, assets_folder='assets')
engine = sqlalchemy.create_engine(os.getenv("DATABASE_URL"))

month_names = {
    1: "Januar",
    2: "Februar",
    3: "Mart",
    4: "April",
    5: "Maj",
    6: "Jun",
    7: "Jul",
    8: "Avgust",
    9: "Septembar",
    10: "Oktobar",
    11: "Novembar",
    12: "Decembar",
}

frame = pd.read_sql_table('consumer_interest_rates', engine)

app.layout = [
    html.H1(children='Kamatne Stope Kredita Stanovništva'),
    html.Div([
        dcc.Dropdown(frame.year.unique(), frame.year.max(), id='dropdown-selection')
    ], className='year-dropdown'),
    html.Div([
        dcc.Graph(id='graph-content')
    ], className='graph-container')
]

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    frame_year = frame[frame.year==value].copy()
    frame_year["month_name"] = frame_year["month"].map(month_names)
    return px.line(
        frame_year,
        x="month_name",
        y="total",
        labels={"month_name": "Mesec", "total": "Total"},
    )

if __name__ == '__main__':
    app.run(debug=True)

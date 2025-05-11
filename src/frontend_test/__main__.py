import os

import pandas as pd
import plotly.express as px
import sqlalchemy
from dash import Dash, html, dcc, callback, Output, Input
from dotenv import load_dotenv

load_dotenv()
app = Dash()
engine = sqlalchemy.create_engine(os.getenv("DATABASE_URL"))

frame = pd.read_sql_table('consumer_interest_rates', engine)

app.layout = [
    html.H1(children='Title of Dash App', style={'textAlign': 'center'}),
    dcc.Dropdown(frame.year.unique(), frame.year.max(), id='dropdown-selection'),
    dcc.Graph(id='graph-content')
]

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    frame_year = frame[frame.year==value]
    return px.line(frame_year, x='month', y='total')

if __name__ == '__main__':
    app.run(debug=True)

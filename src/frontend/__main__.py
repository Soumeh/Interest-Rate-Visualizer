import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from django_plotly_dash import DjangoDash

# Create a DjangoDash application
app = DjangoDash('ExampleDashApp')

# Sample data - in a real app you'd query your PostgreSQL database
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "NY", "NY", "NY"]
})

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),
    html.Div(children='''
        Dash: A web application framework for your Django app.
    '''),
    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])
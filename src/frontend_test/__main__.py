import os
import json

import pandas as pd
import plotly.express as px
import sqlalchemy
from dash import Dash, html, dcc, callback, Output, Input, State
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

# Graph types
graph_types = {
    'total_by_month': 'Ukupne kamatne stope po mesecu',
    'currency_comparison': 'Poređenje kamatnih stopa po valutama'
}

frame = pd.read_sql_table('consumer_interest_rates', engine)

# Initialize the app with clientside callbacks for theme handling
app.clientside_callback(
    """
    function(theme, toggle_clicks) {
        // Get stored theme from localStorage if available
        let storedTheme = localStorage.getItem('theme');

        // Initialize theme based on system preference if not set
        if (!storedTheme) {
            storedTheme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }

        // Use the stored theme as the current theme
        let currentTheme = storedTheme;

        // Toggle theme if the button was clicked
        if (toggle_clicks && toggle_clicks > 0) {
            currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
        }

        // Apply theme to document
        document.documentElement.setAttribute('data-theme', currentTheme);

        // Store theme in localStorage for persistence
        localStorage.setItem('theme', currentTheme);

        return currentTheme;
    }
    """,
    Output('theme-store', 'data'),
    Input('theme-store', 'data'),
    Input('theme-toggle', 'n_clicks')
)

app.layout = html.Div([
    html.H1(children='Kamatne Stope Kredita Stanovništva'),

    # Controls container
    html.Div([
        # Year dropdown
        html.Div([
            html.Label('Izaberite godinu:'),
            dcc.Dropdown(frame.year.unique(), frame.year.max(), id='year-dropdown')
        ], className='dropdown-container'),

        # Graph type dropdown
        html.Div([
            html.Label('Izaberite tip grafa:'),
            dcc.Dropdown(
                options=[{'label': label, 'value': value} for value, label in graph_types.items()],
                value='total_by_month',
                id='graph-type-dropdown'
            )
        ], className='dropdown-container'),

        # Theme toggle button
        html.Div([
            html.Button('Promeni temu', id='theme-toggle', n_clicks=0)
        ], className='theme-toggle-container')
    ], className='controls-container'),

    # Graph container
    html.Div([
        dcc.Graph(id='graph-content')
    ], className='graph-container'),

    # Store the current theme
    dcc.Store(id='theme-store', storage_type='local')
], id='main-container')

@callback(
    Output('graph-content', 'figure'),
    Input('year-dropdown', 'value'),
    Input('graph-type-dropdown', 'value'),
    Input('theme-store', 'data')
)
def update_graph(year, graph_type, theme):
    if not year or not graph_type:
        return {}

    frame_year = frame[frame.year==year].copy()
    frame_year["month_name"] = frame_year["month"].map(month_names)

    # Set template based on theme
    template = 'plotly_dark' if theme == 'dark' else 'plotly_white'

    if graph_type == 'total_by_month':
        return px.line(
            frame_year,
            x="month_name",
            y="total",
            labels={"month_name": "Mesec", "total": "Ukupno"},
            template=template
        )
    elif graph_type == 'currency_comparison':
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


if __name__ == '__main__':
    app.run(debug=True)

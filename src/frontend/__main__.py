from dash import Dash, html, dcc, Output, Input

from src.common import month_names
from src.frontend import GRAPH_TYPE_TRANSLATIONS, total_household_interest_rates, GRAPH_TYPE_FUNCTIONS

app = Dash(__name__, assets_folder='assets')


app.clientside_callback(
    "window.dash_clientside.theme.toggleTheme",
    Output('theme-store', 'data'),
    Input('theme-store', 'data'),
    Input('theme-toggle', 'n_clicks')
)


app.layout = html.Div([
    html.H1(children='Banka aplikacija'),
    # html.Div([
    #     html.Label('Izaberite tip grafa:'),
    #     dcc.Dropdown(
    #         options=[{'label': label, 'value': value} for value, label in graph_types.items()],
    #         value=None,
    #         id='test-dropdown'
    #     )
    # ], className='dropdown-container'),

    # Controls container
    html.Div([
        # Year dropdown
        html.Div([
            html.Label('Izaberite godinu:'),
            dcc.Dropdown(total_household_interest_rates.year.unique(), value=None, id='year-dropdown')
        ], className='dropdown-container'),

        # Graph type dropdown
        html.Div([
            html.Label('Izaberite opcije grafa:'),
            dcc.Dropdown(
                options=[{'label': label, 'value': value} for value, label in GRAPH_TYPE_TRANSLATIONS.items()],
                value=None,
                id='graph-type-dropdown'
            )
        ], className='dropdown-container'),

        # Theme toggle button
        html.Div([
            html.Button('Promeni temu', id='theme-toggle', n_clicks=0)
        ], className='theme-toggle-container')
    ], className='controls-container'),

    html.Hr(className='separator'),

    html.H2(children='privremeno', className='plot-title'),
    # Graph container
    html.Div([
        dcc.Graph(id='graph-content')
    ], className='graph-container'),

    # Store the current theme
    dcc.Store(id='theme-store', storage_type='local')
], id='main-container')



@app.callback(
    Output('graph-content', 'figure'),
    Input('year-dropdown', 'value'),
    Input('graph-type-dropdown', 'value'),
    Input('theme-store', 'data')
)
def update_graph(year, graph_type, theme):
    if not year or not graph_type:
        return {}

    frame_year = total_household_interest_rates[total_household_interest_rates.year == year].copy()
    frame_year["month_name"] = frame_year["month"].map(month_names)

    # Set template based on theme
    template = 'plotly_dark' if theme == 'dark' else 'plotly_white'

    # Use the mapping to call the appropriate function
    if graph_type in GRAPH_TYPE_FUNCTIONS:
        return GRAPH_TYPE_FUNCTIONS[graph_type](frame_year, template)

    # Return empty figure if graph_type is not recognized
    return {}

if __name__ == '__main__':
    app.run(debug=True)

import pandas as pd
from dash import Dash, html, dcc, Output, Input, dash_table

from src.frontend.type.quarter import FiscalSelections
from src.frontend.type.table_type import TableTypes

# TODO remove later only for testing
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

layout = html.Div(
    id="main-container",
    children=[
        html.H1(children="Banka aplikacija"),

        html.Div(
            className="theme-toggle-container",
            children=[
                html.Button(
                    id="theme-toggle-button",
                    className="button",
                    children="Promeni pozadinu",
                ),
                # html.Button(
                #     id="test-button",
                #     className="button",
                #     children="Test",
                # ),
            ],
        ),

		html.Div(
			className="selection-container",
			children=[
				html.Div(
					id="table-type",
					className="dropdown-containers",
					children=[
						html.Div(
							children=[
								html.Label("Izaberite tip podataka:"),
								TableTypes.get_dropdown(),
							],
						),
					],
				),
				html.Div(
					id="time-period",
					className="dropdown-containers",
					children=[
						html.Div(
							children=[
								html.Label("Izaberite namenu:"),
								dcc.Dropdown(
									{}, None, id="table-purpose-dropdown"
								),
							],
						),
						html.Div(
							children=[
								html.Label("Izaberite godinu:"),
								# TODO proper year selection
								dcc.Dropdown(
									[2010, 2011, 2012, 2013, 2014],
									None,
									id="year-selection-dropdown",
								),
							],
						),
						html.Div(
							children=[
								html.Label("Izaberite vremenski period:"),
								FiscalSelections.get_dropdown(),
							],
						),
					],
				),
			],
		),

        html.Hr(className="separator"),
        html.Div(
            id="graph-container",
            children=[
                dcc.Graph(id="graph-content"),
            ],
        ),
        dash_table.DataTable(
        	id="data-table",
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("records"),
            export_format="csv",
        ),
        dcc.Store(id="theme-store", storage_type="local"),
    ],
)


def create_dash(server):
	app = Dash(__name__, server=server, assets_folder="assets")

	app.clientside_callback(
		"window.dash_clientside.theme.toggleTheme",
		Output("theme-store", "data"),
		Input("theme-store", "data"),
		Input("theme-toggle-button", "n_clicks"),
	)

	app.layout = layout

	@app.callback(
		Output("table-purpose-dropdown", "options"),
		Input("table-type-dropdown", "value"),
	)
	def update_table_purpose(table_type):
		if table_type is None:
			return {}

		return {
			selection.name: selection.value
			for selection in TableTypes[table_type].value.purpose
		}

	@app.callback(
		Output("graph-content", "figure"),
		Input("table-type-dropdown", "value"),
		Input("table-purpose-dropdown", "value"),
		Input("fiscal-selection-dropdown", "value"),
	)
	def update_display(table_type, table_purpose, fiscal_selection):
		if table_type is None or table_purpose is None or fiscal_selection is None:
			return

		table = TableTypes[table_type].value.table
		purpose = TableTypes[table_type].value.purpose

		# TODO do

import plotly.express
from dash import Dash, html, dcc, Output, Input, dash_table
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from src.common import MONTH_NAMES
from src.frontend.type.quarter import FiscalSelections
from src.frontend.type.table_type import TableTypes

def create_dash(server: Flask, db: SQLAlchemy):
    app = Dash(__name__, server=server, assets_folder="assets")

    app.layout = html.Div(
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
                                    dcc.Dropdown([], None, id="table-purpose-dropdown"),
                                ],
                            ),
                            html.Div(
                                children=[
                                    html.Label("Izaberite godinu:"),
                                    # TODO proper year selection
                                    dcc.Dropdown(
                                        [],
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
            html.Div(id="graph-container"),

            dcc.Store(id="theme-store", storage_type="local"),
        ],
    )

    app.clientside_callback(
        "window.dash_clientside.theme.toggleTheme",
        Output("theme-store", "data"),
        Input("theme-store", "data"),
        Input("theme-toggle-button", "n_clicks"),
    )

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
        Output("year-selection-dropdown", "options"),
        Input("table-type-dropdown", "value"),
    )
    def update_years(table_type):
        if table_type is None:
            return {}

        return TableTypes[table_type].value.table.get_years(db.session)

    @app.callback(
        Output("graph-container", "children"),
        Input("table-type-dropdown", "value"),
        Input("table-purpose-dropdown", "value"),
        Input("year-selection-dropdown", "value"),
        Input("fiscal-selection-dropdown", "value"),
        Input("theme-store", "data"),
    )
    def update_display(
		table_type, table_purpose, year_selection, fiscal_selection, theme
    ):
        theme = "plotly_dark" if theme == "dark" else "plotly_white"

        if (
			table_type is None
			or table_purpose is None
			or year_selection is None
			or fiscal_selection is None
        ):
            return [
                dcc.Graph(
                    id="graph-content",
                    figure=plotly.express.bar(None, template=theme)
                ),
                dash_table.DataTable(
                    id="data-table",
                    export_format="csv",
                ),
            ]

        table = TableTypes[table_type].value.table
        purpose_type = TableTypes[table_type].value.purpose
        purpose = purpose_type[table_purpose]
        month_range = FiscalSelections[fiscal_selection].value.range

        data = table.get_data(db.session, purpose, year_selection, month_range)

        columns = [
            {"id": i, "name": i}
            for i in data.columns
            if i not in ["id", "type", "purpose"]
        ]
        table_data = data.to_dict("records")

        data["month_name"] = data["month"].map(MONTH_NAMES)
        figure = plotly.express.bar(
            data,
            x="month_name",
            y="total",
            labels={"month_name": "Mesec", "total": "Ukupno"},
            template=theme,
        )
        figure.add_annotation(
            x=0,
            y=-0.1,
            text="U % na godišnjem nivou",
            showarrow=False,
            xref="paper",
            yref="paper",
        )

        return [
            dcc.Graph(
                id="graph-content",
                figure=figure,
            ),
            dash_table.DataTable(
                id="data-table",
                columns=columns,
                data=table_data,
                export_format="csv",
            ),
        ]

    return app

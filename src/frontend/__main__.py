from dotenv import load_dotenv

from src.backend import create_app

# from src.frontend import GRAPH_TYPE_TRANSLATIONS, total_household_interest_rates, GRAPH_TYPE_FUNCTIONS
# from src.frontend.app import app

load_dotenv()


# @app.callback(
#     Output('graph-content', 'figure'),
#     Input('year-dropdown', 'value'),
#     Input('graph-type-dropdown', 'value'),
#     Input('theme-store', 'data')
# )
# def update_graph(year, graph_type, theme):
#     if not year or not graph_type:
#         return {}
#
#     frame_year = total_household_interest_rates[total_household_interest_rates.year == year].copy()
#     frame_year["month_name"] = frame_year["month"].map(MONTH_NAMES)
#
#     # Set template based on theme
#     template = 'plotly_dark' if theme == 'dark' else 'plotly_white'
#
#     # Use the mapping to call the appropriate function
#     if graph_type in GRAPH_TYPE_FUNCTIONS:
#         return GRAPH_TYPE_FUNCTIONS[graph_type](frame_year, template)
#
#     # Return empty figure if graph_type is not recognized
#     return {}

# async def async_main():
#     engine = create_async_engine(getenv("DATABASE_URL"), future=True)
#     async with AsyncSession(engine) as session:
#         async with session.begin():
#             pass
#
#     app.run(debug=True)
#
# if __name__ == '__main__':
#     asyncio.run(async_main())

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

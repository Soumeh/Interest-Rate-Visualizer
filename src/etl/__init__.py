import os
import asyncio
# import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
# import requests

load_dotenv()

excel_url = 'https://www.nbs.rs/export/sites/NBS_site/documents/statistika/monetarni_sektor/SBMS_ks_3.xls'
sheet_name = '0'

async def main() -> None:

    # Download the file
    # response = requests.get(excel_url)
    # excel_data = BytesIO(response.content)

    # Read the Excel file into a DataFrame
    # df = pd.read_excel(excel_data, sheet_name=sheet_name)
    # df = pd.read_excel(excel_data)

    # Display the first few rows to verify
    # print("Data from Excel URL:")
    # print(df.head())

    engine = create_async_engine(os.getenv("DATABASE_URL"))
    async with engine.connect() as connection:
        result = await connection.execute(text("select 'hello world'"))
        print(result.fetchall())
    await engine.dispose()
    # 3. Export to database
    # table_name = 'excel_data'  # Your table name
    # if_exists = 'replace'  # 'replace', 'append', or 'fail'

    # Write DataFrame to SQL database
    # df.to_sql(
        # name=table_name,
        # con=engine,
        # if_exists=if_exists,
        # index=False  # Set to True if you want to write row indices
    # )

    # print(f"Data successfully exported to {table_name} table in database")

asyncio.run(main())
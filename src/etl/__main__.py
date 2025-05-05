import os
import asyncio
from hashlib import md5
from pathlib import Path

import pandas
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
import requests

load_dotenv()

def get_cached_data(url, sheet_name: str | int = 0, cache_dir: str = ".temp/excel/", force_download: bool = False):
    """Download Excel file with caching"""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(exist_ok=True)

    url_hash = md5(url.encode()).hexdigest()
    cache_path = cache_dir / f"{url_hash}.xls"

    if force_download or not cache_path.exists():
        print(f"Downloading from: {url}")
        response = requests.get(url)
        response.raise_for_status()

        with open(cache_path, 'wb') as f:
            f.write(response.content)

    return pandas.read_excel(cache_path, sheet_name=sheet_name, na_values=['-'])

excel_url = 'https://www.nbs.rs/export/sites/NBS_site/documents/statistika/monetarni_sektor/SBMS_ks_3.xls'
excel = get_cached_data(excel_url, 3)




# async def main() -> None:

    # Download the file
    # response = requests.get(excel_url)
    # excel_data = BytesIO(response.content)

    # Read the Excel file into a DataFrame
    # df = pd.read_excel(excel_data, sheet_name=sheet_name)
    # df = pd.read_excel(excel_data)

    # Display the first few rows to verify
    # print("Data from Excel URL:")
    # print(df.head())

    # engine = create_async_engine(os.getenv("DATABASE_URL"))
    # async with engine.connect() as connection:
    #     result = await connection.execute(text("select 'hello world'"))
    #     print(result.fetchall())
    # await engine.dispose()

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

# asyncio.run(main())

def main():
    print(excel.iat[0, 0])

if __name__ == '__main__':
    main()

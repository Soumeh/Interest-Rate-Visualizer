import asyncio
import hashlib
from os import getenv
from pathlib import Path
from typing import Callable

import pandas
import requests
from dotenv import load_dotenv
from narwhals import DataFrame
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from src.db import Base
from src.etl.processors import process_population_interest_rates, process_non_financial_interest_rates

load_dotenv()

def get_cached_data(url, sheet_name: str | int = 0, cache_dir: str = ".temp/excel/", force_download: bool = False) -> DataFrame:
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(exist_ok=True, parents=True)

    url_hash = hashlib.md5(url.encode()).hexdigest()
    cache_path = cache_dir / f"{url_hash}.xls"

    if force_download or not cache_path.exists():
        print(f"Downloading from: {url}")
        response = requests.get(url)
        response.raise_for_status()

        with open(cache_path, 'wb') as f:
            f.write(response.content)

    return pandas.read_excel(cache_path, sheet_name=sheet_name, na_values=['-', ' ', '', ' -', '- '], header=None)

async def process_file(session: AsyncSession, url: str, sheet_name: str, frame_consumer: Callable):
    frame: DataFrame = get_cached_data(url, sheet_name)
    await frame_consumer(session, frame)

async def async_main():
    engine = create_async_engine(getenv("DATABASE_URL"), future=True)

    async with engine.begin() as connection:
        # await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        async with session.begin():
            await process_file(
                session,
                "https://www.nbs.rs/export/sites/NBS_site/documents/statistika/monetarni_sektor/SBMS_ks_3.xls",
                "Weighted IR on loans-New Bus.",
                process_population_interest_rates,
            )
            await process_file(
                session,
                "https://www.nbs.rs/export/sites/NBS_site/documents/statistika/monetarni_sektor/SBMS_ks_4.xlsx",
                "Weighted IR on loans-New Bus.",
                process_non_financial_interest_rates,
            )
        await session.commit()

if __name__ == '__main__':
    asyncio.run(async_main())

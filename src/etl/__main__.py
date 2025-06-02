import os
from hashlib import md5
from pathlib import Path
from typing import Callable

import pandas
import requests
import sqlalchemy
from dotenv import load_dotenv
from narwhals import DataFrame

from src.db.models import Base
from src.etl.processors import *  # noqa: F403

load_dotenv()

def get_cached_data(url, sheet_name: str | int = 0, cache_dir: str = ".temp/excel/", force_download: bool = False) -> DataFrame:
    """Download an Excel file with caching"""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(exist_ok=True, parents=True)

    url_hash = md5(url.encode()).hexdigest()
    cache_path = cache_dir / f"{url_hash}.xls"

    if force_download or not cache_path.exists():
        print(f"Downloading from: {url}")
        response = requests.get(url)
        response.raise_for_status()

        with open(cache_path, 'wb') as f:
            f.write(response.content)

    return pandas.read_excel(cache_path, sheet_name=sheet_name, na_values=['-', ' ', '', ' -', '- '], header=None)

engine = sqlalchemy.create_engine(os.getenv("DATABASE_URL"))

def process_file(url: str, sheet_name: str, frame_consumer: Callable):
    frame: DataFrame = get_cached_data(url, sheet_name)
    with Session(engine) as session:
        frame_consumer(session, frame)
        session.commit()

def main():
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        process_file(
            "https://www.nbs.rs/export/sites/NBS_site/documents/statistika/monetarni_sektor/SBMS_ks_3.xls",
            "Weighted IR on loans-New Bus.",
            process_population_interest_rates,
        )
        process_file(
            "https://www.nbs.rs/export/sites/NBS_site/documents/statistika/monetarni_sektor/SBMS_ks_3.xls",
            "Volume on loans-New Bus.",
            process_population_loans,
        )
        session.commit()

if __name__ == '__main__':
    main()

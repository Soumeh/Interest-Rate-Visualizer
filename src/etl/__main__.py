import os
from hashlib import md5
from pathlib import Path
from typing import Callable

import pandas
import requests
import sqlalchemy
from dotenv import load_dotenv
from narwhals import DataFrame
from sqlalchemy.orm import Session

from src.db import Base
from src.etl.processors import process_population_interest_rates, process_population_loans, \
    process_non_financial_interest_rates

load_dotenv()
ENGINE = sqlalchemy.create_engine(os.getenv("DATABASE_URL"), implicit_returning=False)

def get_cached_data(url, sheet_name: str | int = 0, cache_dir: str = ".temp/excel/", force_download: bool = False) -> DataFrame:
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

def process_file(url: str, sheet_name: str, frame_consumer: Callable):
    frame: DataFrame = get_cached_data(url, sheet_name)
    # with Session(ENGINE) as session:
    #     frame_consumer(session, frame)
    #     session.commit()
    frame_consumer(frame)

def main():
    Base.metadata.create_all(ENGINE)

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
    process_file(
        "https://www.nbs.rs/export/sites/NBS_site/documents/statistika/monetarni_sektor/SBMS_ks_4.xlsx",
        "Weighted IR on loans-New Bus.",
        process_non_financial_interest_rates,
    )


if __name__ == '__main__':
    main()

import os
from hashlib import md5
from pathlib import Path

import pandas
import requests
import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from src.db import Base
from src.db.models import ConsumerInterestRates

load_dotenv()

def get_cached_data(url, sheet_name: str | int = 0, cache_dir: str = ".temp/excel/", force_download: bool = False):
    """Download an Excel file with caching"""
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

    return pandas.read_excel(cache_path, sheet_name=sheet_name, na_values=['-', ' ', '', ' -', '- '], header=None)

excel_url = 'https://www.nbs.rs/export/sites/NBS_site/documents/statistika/monetarni_sektor/SBMS_ks_3.xls'
excel = get_cached_data(excel_url, "Weighted IR on loans-New Bus.")
engine = sqlalchemy.create_engine(os.getenv("DATABASE_URL"))

def main():
    Base.metadata.create_all(engine)

    test = excel.iloc[11:-5, 0:14]

    with Session(engine) as session:
        for index, row in test.iterrows():
            try:
                rate = ConsumerInterestRates.from_row(row)
                session.add(rate)
            except Exception as e:
                print(f"Error processing row {index}: {e}")
        session.commit()


if __name__ == '__main__':
    main()

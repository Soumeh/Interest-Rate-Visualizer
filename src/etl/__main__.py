import asyncio
import hashlib
from os import getenv
from pathlib import Path

import pandas
import requests
from dotenv import load_dotenv
from narwhals import DataFrame
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from src.db import Base, SerializableTable
from src.db.household import HouseholdLoans, HouseholdTermDeposits
from src.db.non_financial import NonFinancialLoans, NonFinancialTermDepositsBySize
from src.db.total import TotalLoans, TotalLoansByCurrency

load_dotenv()
DATABASE_URL = f"postgresql+asyncpg://{getenv('POSTGRES_USER')}:{getenv('POSTGRES_PASSWORD')}@{getenv('POSTGRES_HOST')}:{getenv('POSTGRES_PORT')}/{getenv('POSTGRES_DB')}"


def get_cached_data(
	url,
	sheet_name: str | int = 0,
	cache_dir: str = ".temp/excel/",
	force_download: bool = False,
) -> DataFrame:
	cache_dir = Path(cache_dir)
	cache_dir.mkdir(exist_ok=True, parents=True)

	# url_hash = hashlib.md5(url.encode()).hexdigest()
	# cache_path = cache_dir / f"{url_hash}.xls"
	cache_path = cache_dir / url.split("/")[-1]

	if force_download or not cache_path.exists():
		print(f"Downloading from: {url}")
		response = requests.get(url)
		response.raise_for_status()

		with open(cache_path, "wb") as f:
			f.write(response.content)

	return pandas.read_excel(
		cache_path,
		sheet_name=sheet_name,
		na_values=["-", " ", "", " -", "- "],
		header=None,
	)


async def process_file(
	session: AsyncSession, url: str, sheet_name: str, table: type[SerializableTable]
):
	frame: DataFrame = get_cached_data(url, sheet_name)
	await table.process_frame(session, frame)


async def async_main():
	engine = create_async_engine(DATABASE_URL, future=True)

	async with engine.begin() as connection:
		await connection.run_sync(Base.metadata.create_all)

	async with AsyncSession(engine) as session:
		async with session.begin():
			await process_file(
				session,
				"https://www.nbs.rs/export/sites/NBS_site/documents/statistika/monetarni_sektor/SBMS_ks_3.xls",
				"Weighted IR on loans-New Bus.",
				HouseholdLoans,
			)
			# await process_file(
			# 	session,
			# 	"https://www.nbs.rs/export/sites/NBS_site/documents/statistika/monetarni_sektor/SBMS_ks_4.xlsx",
			# 	"Weighted IR on loans-New Bus.",
			# 	NonFinancialLoans,
			# )
			# await process_file(
			# 	session,
			# 	"https://www.nbs.rs/export/sites/NBS_site/documents/statistika/monetarni_sektor/SBMS_ks_5.xls",
			# 	"Weighted IR on deposits-New Bus",
			# 	NonFinancialTermDepositsBySize,
			# )
			# await process_file(
			# 	session,
			# 	"https://www.nbs.rs/export/sites/NBS_site/documents/statistika/monetarni_sektor/SBMS_ks_6.xls",
			# 	"Weigted IR on deposits-New Bus.",
			# 	HouseholdTermDeposits,
			# )
			# await process_file(
			# 	session,
			# 	"https://www.nbs.rs/export/sites/NBS_site/documents/statistika/monetarni_sektor/SBMS_ks_7.xlsx",
			# 	"Weghted IR on deposits-New Bus.",
			# 	NonFinancialTermDepositsBySize,
			# )
			# await process_file(
			# 	session,
			# 	"https://www.nbs.rs/export/sites/NBS_site/documents/statistika/monetarni_sektor/SBMS18.xls",
			# 	"Weighted IR on loans-New Bus.",
			# 	TotalLoans,
			# )
			# await process_file(
			# 	session,
			# 	"https://www.nbs.rs/export/sites/NBS_site/documents/statistika/monetarni_sektor/SBMS25.xls",
			# 	"Weighted IR on Loans-New Bus.",
			# 	TotalLoansByCurrency,
			# )
		await session.commit()


if __name__ == "__main__":
	asyncio.run(async_main())

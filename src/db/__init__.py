from sqlalchemy.orm import declarative_base

Base = declarative_base()

def clean_title(title: str) -> str:
    return title.strip().rstrip()

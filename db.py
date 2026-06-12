from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

DATABASE_URL = "sqlite:///pots.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

Base = declarative_base()
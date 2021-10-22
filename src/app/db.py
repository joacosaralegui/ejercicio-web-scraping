import os

from sqlalchemy import Column, DateTime, Integer, MetaData, SmallInteger, Table, Text, create_engine
from sqlalchemy.sql import func

from databases import Database
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Crawl logs
crawl_logs = Table(
    "crawl_logs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("date", DateTime, default=func.now(), nullable=False, index=True),
    Column("url", Text, index=True),
    Column("amount_of_links", Integer),
)

metadata.create_all(engine)

# databases query builder
database = Database(DATABASE_URL)

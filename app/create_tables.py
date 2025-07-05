# create_tables.py

from app.models import Base
from app.database import engine

# This will create any missing tables in the DB
Base.metadata.create_all(bind=engine)

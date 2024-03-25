from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import os

engine = create_engine(os.environ.get("DATABASE_URI"))
Base = declarative_base()
Base.metadata.create_all(engine)
from sqlalchemy import create_engine
from db.models import Base
import os

engine = create_engine(os.getenv("DATABASE_URI"))
Base.metadata.create_all(engine)
engine.dispose()

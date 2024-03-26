from sqlalchemy import create_engine
from models import Base
import os

engine = create_engine(os.getenv("DATABASE_URI"))
Base.metadata.create_all(engine)

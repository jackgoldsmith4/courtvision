from sqlalchemy import create_engine
from dotenv import load_dotenv
from db.models import Base
import os

load_dotenv()
engine = create_engine(os.environ.get("DATABASE_URL"))

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
engine.dispose()

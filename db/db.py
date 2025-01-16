from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy import create_engine
import os

@contextmanager
def get_session():
  db_url = os.environ.get("DATABASE_URL")
  engine = create_engine(db_url, echo=False, pool_size=5, max_overflow=1)
  Session = sessionmaker(bind=engine)
  session = Session()
  try:
    yield session
  finally:
    session.close()
    engine.dispose()

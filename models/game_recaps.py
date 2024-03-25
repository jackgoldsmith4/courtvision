from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Date, Text

Base = declarative_base()

class GameRecaps(Base):
  __tablename__ = 'game_recaps'

  game_id = Column(String, primary_key=True) # hash of game_date, home_team, away_team
  game_date = Column(Date, nullable=False)
  home_team = Column(String(100), nullable=False)
  away_team = Column(String(100), nullable=False)
  author = Column(String(100), nullable=False)
  recap_text = Column(Text)

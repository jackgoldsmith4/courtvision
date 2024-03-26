from sqlalchemy import Column, Integer, String, Date, CheckConstraint, Float, Index, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class GameRecaps(Base):
  __tablename__ = 'game_recaps'

  game_id = Column(String, primary_key=True) # hash of game_date, home_team, away_team
  game_date = Column(Date, nullable=False)
  home_team = Column(String(100), nullable=False)
  away_team = Column(String(100), nullable=False)
  author = Column(String(100))
  recap_text = Column(Text)

class PlayerStats(Base):
  __tablename__ = 'player_stats'
  __table_args__ = (
    CheckConstraint('game_started IN (0, 1)'),
    CheckConstraint('is_home_game IN (0, 1)'),
    Index('idx_game_id', 'game_id'),
  )

  stats_id = Column(Integer, primary_key=True)
  game_id = Column(String, nullable=False) # hash of game_date, home_team, away_team
  game_date = Column(Date, nullable=False)
  home_team = Column(String(100), nullable=False)
  away_team = Column(String(100), nullable=False)
  is_home_game = Column(Integer, nullable=False) # 1 for home, 0 for away

  player_name = Column(String(100), nullable=False)
  player_age = Column(Integer, nullable=False)
  game_outcome = Column(Integer, nullable=False)  # negative values for L, positive for W
  game_started = Column(Integer, nullable=False)  # 1 for started, 0 otherwise
  minutes_played = Column(Float)
  points = Column(Integer)
  field_goals_made = Column(Integer)
  field_goals_attempted = Column(Integer)
  three_pointers_made = Column(Integer)
  three_pointers_attempted = Column(Integer)
  free_throws_made = Column(Integer)
  free_throws_attempted = Column(Integer)
  offensive_rebounds = Column(Integer)
  defensive_rebounds = Column(Integer)
  assists = Column(Integer)
  steals = Column(Integer)
  blocks = Column(Integer)
  turnovers = Column(Integer)
  plus_minus = Column(Integer)

from sqlalchemy import Column, Integer, String, Date, CheckConstraint, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PlayerStats(Base):
    __tablename__ = 'player_stats'
    __table_args__ = (
      CheckConstraint('game_started IN (0, 1)'),
      CheckConstraint('is_home_game IN (0, 1)'),
    )

    stats_id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String, nullable=False)
    game_date = Column(Date, nullable=False)
    player_team = Column(String(100), nullable=False)
    opponent = Column(String(100), nullable=False)
    player_name = Column(String(100), nullable=False)
    is_home_game = Column(Integer, nullable=False) # 1 for home, 0 for away
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

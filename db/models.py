from sqlalchemy import Column, Integer, String, Date, CheckConstraint, Float, Text, asc, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class GameRecap(Base):
  __tablename__ = 'game_recaps'

  author = Column(String(100))
  headline = Column(Text)
  recap_text = Column(Text)

  # 1-to-1 relationship with Game table
  # TODO implement

class PlayerGameLog(Base):
  __tablename__ = 'player_game_logs'
  __table_args__ = (
    CheckConstraint('game_started IN (0, 1)'),
    CheckConstraint('is_home_game IN (0, 1)'),
  )

  player_game_log_id = Column(String(64), primary_key=True) # SHA-256 hash of player_name and game id

  player_age = Column(Integer, nullable=False)
  is_home_game = Column(Integer, nullable=False) # 1 for home, 0 for away
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

  # relationship to Player
  player = relationship("Player", back_populates="player_game_logs")

  # relationship to Game
  game = relationship("Game", back_populates="game_stats")

class Player(Base):
  __tablename__ = 'players'

  id = Column(String(20), primary_key=True) # Basketball-Reference ID
  name = Column(String(100), nullable=False)
  start_year = Column(Integer, nullable=False)
  end_year = Column(Integer, nullable=False)

  # 1-to-many relationship with PlayerGameLog
  player_game_logs = relationship("PlayerGameLog", order_by=asc(PlayerGameLog.game_date), back_populates="player")

  def to_dict(self):
    return {
      'id': self.id,
      'name': self.name,
      'start_year': self.start_year,
      'end_year': self.end_year
    }

class Game(Base):
  __tablename__ = 'games'

  id = Column(String(64), primary_key=True) # SHA-256 hash of game_date, home_team, away_team
  game_date = Column(Date, nullable=False)
  home_team = Column(String(100), nullable=False)
  away_team = Column(String(100), nullable=False)

  # 1-to-many relationship with PlayerGameLog
  game_stats = relationship("PlayerGameLog", order_by=desc(PlayerGameLog.points))

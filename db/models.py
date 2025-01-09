from sqlalchemy import Column, Integer, String, Date, CheckConstraint, Float, Text, asc, desc, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import relationship

Base = declarative_base()

class PlayerGameLog(Base):
  __tablename__ = 'player_game_logs'
  __table_args__ = (
    CheckConstraint('game_started IN (0, 1)'),
    CheckConstraint('is_home_game IN (0, 1)'),
  )

  player_game_log_id = Column(BYTEA, primary_key=True) # SHA-256 hash of player_name and game id

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
  player_id = Column(String(20), ForeignKey('players.id'))
  player = relationship("Player", back_populates="player_game_logs")

  # relationship to Game
  game_id = Column(BYTEA, ForeignKey('games.id'))
  game = relationship("Game", back_populates="game_stats")

  def to_dict(self):
    return {
      'player_game_log_id': self.player_game_log_id,
      'player_id': self.player_id,
      'game_id': self.game_id,
      'player_age': self.player_age,
      'is_home_game': self.is_home_game,
      'game_outcome': self.game_outcome,
      'game_started': self.game_started,
      'minutes_played': self.minutes_played,
      'points': self.points,
      'field_goals_made': self.field_goals_made,
      'field_goals_attempted': self.field_goals_attempted,
      'three_pointers_made': self.three_pointers_made,
      'three_pointers_attempted': self.three_pointers_attempted,
      'free_throws_made': self.free_throws_made,
      'free_throws_attempted': self.free_throws_attempted,
      'offensive_rebounds': self.offensive_rebounds,
      'defensive_rebounds': self.defensive_rebounds,
      'assists': self.assists,
      'steals': self.steals,
      'blocks': self.blocks,
      'turnovers': self.turnovers,
      'plus_minus': self.plus_minus
    }

class Player(Base):
  __tablename__ = 'players'

  id = Column(String(20), primary_key=True) # Basketball-Reference ID
  name = Column(String(100), nullable=False)
  start_year = Column(Integer, nullable=False)
  end_year = Column(Integer, nullable=False)

  # 1-to-many relationship with PlayerGameLog
  player_game_logs = relationship("PlayerGameLog", order_by=asc(PlayerGameLog.player_age), back_populates="player")

  def to_dict(self):
    return {
      'id': self.id,
      'name': self.name,
      'start_year': self.start_year,
      'end_year': self.end_year
    }

class Game(Base):
  __tablename__ = 'games'

  id = Column(BYTEA, primary_key=True) # SHA-256 hash of game_date, home_team, away_team
  game_date = Column(Date, nullable=False)
  home_team = Column(String(100), nullable=False)
  away_team = Column(String(100), nullable=False)

  recap_url = Column(String(100), nullable=True)
  recap_author = Column(String(100), nullable=True)
  recap_headline = Column(Text, nullable=True)
  recap_text = Column(Text, nullable=True)

  # 1-to-many relationship with PlayerGameLog
  game_stats = relationship("PlayerGameLog", order_by=desc(PlayerGameLog.points), back_populates="game")

from sqlalchemy.orm import sessionmaker
from models import PlayerStats
from hashlib import sha256

# add a player stat row to the DB
def insert_player_stat(engine):
  pass

# get all stats for a certain game
def get_player_stats_by_game_id(engine, game_id):
  pass

# get all stats for a certain player
def get_player_stats_by_player_name(engine, player_name):
  # TODO
  pass

from utils import remove_special_characters
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db.games import get_all_games
from db.players import get_players
from openai import OpenAI
import pandas as pd
import numpy as np
import os

url = "https://api.openai.com/v1/chat/completions"
api_key = os.environ.get("OPENAI_API_KEY") # TODO get new key and put it in .env and heroku
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# prompt GPT 3.5 to pick a player from the given context that will appear in the recap headline
# Returns: name of a player from the context
def prompt_model(context_str):
  prompt_text = f"""
    Here is a string that represents the box score for a specific NBA game:

    {context_str}

    Your job is to pick the player in this box score that you think is most likely
    to show up in the headline of the Associated Press game recap article.

    Your response should only consist of a name that is present in the provided box score,
    or just the word None if you think it is most likely that the headline doesn't mention a specific player.

    Some box scores have been anonymized, and each player in that game is represented as Player X, where X is an incrementing integer.
    In these anonymized cases, and only these cases, your response should only consist of the words Player X,
    where X is replaced by the integer corresponding to the player you pick. You can also choose to pick no player and return None.
    In other words, treat anonymized player labels as if they were player names.
    If the names are not anonymized, your response should contain the actual player name instead of an anonymized version.
  """

  # TODO update model
  data = {
    "model": "gpt-3.5-turbo",
    "prompt": prompt_text,
    "max_tokens": 60
  }

  client = OpenAI(api_key=api_key)
  response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {
        "role": "user",
        "content": prompt_text,
      }
    ],
    temperature=0.3,
    max_tokens=60,
    top_p=0.5,
  )

  chosen_player = response.choices[0].message.content
  return chosen_player

# Takes in a box score string and returns an anonymized version, as well as a dictionary
# mapping anonymized names to actual player names {key=anonymized_name, value=player_name}
def anonymize_context(box_score_str):
  player_dict = {}

  player_anonymized_counter = 0
  names = box_score_str.split('player_name: ')[1:]
  for name in names:
    player = name.split(' player_age:')[0]
    anon_player = f"Player {player_anonymized_counter}"
    box_score_str = box_score_str.replace(player, anon_player)
    player_dict[anon_player] = player
    player_anonymized_counter += 1

  return box_score_str, player_dict

# Wrapper function to prompt the model for a box score string and return names chosen before and after anonymization
def predict_name_from_box_score(box_score_str):
  chosen_name = prompt_model(box_score_str)
  box_score_player_replaced, player_dict = anonymize_context(box_score_str)
  chosen_name_replaced = prompt_model(box_score_player_replaced)
  try:
    chosen_name_anonymous = player_dict[chosen_name_replaced]
  except KeyError:
    chosen_name_anonymous = 'None'
  return (chosen_name, chosen_name_anonymous)

# Returns: 2x2 matrix representing changes in model behavior after anonymizing player
# B = model predicts player for the headline BEFORE switching
# A = model predicts player for the headline AFTER switching
# [  (B,A)      (B, no A)  ]
# [(no B, A)  (no B, no A) ]
def build_player_change_matrix(contexts_with_name, name):
  player_matrix = np.zeros((2, 2))
  predictions = []
  for context, chosen_name, chosen_name_anonymous in contexts_with_name:
    # increment corresponding matrix cell
    if chosen_name == name:
      if chosen_name_anonymous == name:
        player_matrix[0][0] += 1
      else:
        player_matrix[0][1] += 1
    else:
      if chosen_name_anonymous == name:
        player_matrix[1][0] += 1
      else:
        player_matrix[1][1] += 1
    predictions.append((context, chosen_name, chosen_name_anonymous))

  return player_matrix, predictions

### SCRIPT ###
engine = create_engine(os.environ.get("DATABASE_URL"))
Session = sessionmaker(bind=engine)
session = Session()

predictions = pd.DataFrame(columns=['box_score_str', 'recap_headline', 'predicted_name', 'predicted_name_anonymous'])
for game in get_all_games():
  box_score_str = '' # TODO pull and flatten all player stats for this game into a box score string (also normalize each name)
  recap_headline = game.recap_headline
  chosen_name, chosen_name_anonymous = predict_name_from_box_score(box_score_str)
  predictions = predictions.append({
    'box_score_str': box_score_str,
    'recap_headline': recap_headline,
    'predicted_name': remove_special_characters(chosen_name),
    'predicted_name_anonymous': remove_special_characters(chosen_name_anonymous)
  }, ignore_index=True)

player_matrices = {}
for player in get_players(session):
  # TODO setup a "matrix" for each player with 8 options, decide how to organize 8 instead of 4
  player_matrix = np.zeros((2, 2))

  # return all games in the dataset that contain that player in the box score
  name = remove_special_characters(player.name)
  games_with_player = predictions[predictions['box_score_str'].str.contains(name)]

  # TODO populate the player "matrix" for each game based on:
  ### A: if the player was picked from the box score
  ### B: if the player was picked from the anonymized box_score
  ### C: if the player actually was in the recap headline (TODO need a function to extract player names from recap headlines)

  player_matrices[name] = player_matrix

# TODO save player_matrices somehow

session.close()
engine.dispose()

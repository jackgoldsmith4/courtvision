from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from tf_keras.callbacks import EarlyStopping
from tf_keras.models import Sequential
from tf_keras.layers import Dense
from utils import thread_func
from sklearn.svm import SVR
import tensorflow as tf
import pandas as pd
import numpy as np
import os

# model 1: Linear Regression
def linear_regression(X_train, X_train_scaled, y_train, X_test_scaled, y_test, n_train, n_test, test_mean):
  model = LinearRegression()
  model.fit(X_train_scaled, y_train)
  return run_model(
    model, 'Linreg',
    X_train_scaled, y_train, X_test_scaled, y_test,
    X_train.columns, n_train, n_test, test_mean
  )

# model 2: Lasso Regression
def lasso_regression(X_train, X_train_scaled, y_train, X_test_scaled, y_test, n_train, n_test, test_mean, l):
  model = Lasso(alpha=l)
  model.fit(X_train_scaled, y_train)
  return run_model(
    model, f"Lasso (lambda={l})",
    X_train_scaled, y_train, X_test_scaled, y_test,
    X_train.columns, n_train, n_test, test_mean
  )

# model 3: Ridge Regression
def ridge_regression(X_train, X_train_scaled, y_train, X_test_scaled, y_test, n_train, n_test, test_mean, l):
  model = Ridge(alpha=l)
  model.fit(X_train_scaled, y_train)
  return run_model(
    model, f"Ridge (lambda={l})",
    X_train_scaled, y_train, X_test_scaled, y_test,
    X_train.columns, n_train, n_test, test_mean
  )

# model 4: Random Forest Regression
def random_forest_regression(X_train, y_train, X_test, y_test, n_train, n_test, test_mean, n_estimators, max_depth):
  model = RandomForestRegressor(
    n_estimators=n_estimators,
    max_depth=max_depth,
  )
  model.fit(X_train, y_train)
  return run_model(
    model, f"Random Forest ({n_estimators} estimators, {max_depth} depth)",
    X_train, y_train, X_test, y_test,
    X_train.columns, n_train, n_test, test_mean
  )

# model 5: Support Vector Machine (SVR)
def svm(X_train, y_train, X_test, y_test, n_train, n_test, test_mean, kernel):
  # scale both X and y
  scaler_X = MinMaxScaler()
  X_train_scaled = scaler_X.fit_transform(X_train)
  X_test_scaled = scaler_X.transform(X_test)
  scaler_y = MinMaxScaler()
  y_train_scaled = scaler_y.fit_transform(y_train.to_numpy().reshape(-1, 1)).flatten()
  y_test_scaled = scaler_y.transform(y_test.to_numpy().reshape(-1, 1)).flatten()

  model = SVR(kernel=kernel)
  model.fit(X_train_scaled, y_train_scaled)
  train_predictions = model.predict(X_train_scaled)
  test_predictions = model.predict(X_test_scaled)

  # Scale back the predictions to the original value range
  y_train_pred = scaler_y.inverse_transform(train_predictions.reshape(-1, 1)).flatten()
  y_test_pred = scaler_y.inverse_transform(test_predictions.reshape(-1, 1)).flatten()

  mse_train = mean_squared_error(y_train, y_train_pred)
  rmse_train = np.sqrt(mse_train)
  r2_train = r2_score(y_train, y_train_pred)

  mse_test = mean_squared_error(y_test, y_test_pred)
  rmse_test = np.sqrt(mse_test)
  r2_test = r2_score(y_test, y_test_pred)

  return pd.DataFrame({
    'model_type': f"SVM ({kernel} kernel)",
    'n_train': n_train,
    'n_test': n_test,
    'mse_train': mse_train,
    'rmse_train': rmse_train,
    'r2_train': r2_train,
    'mse_test': mse_test,
    'rmse_test': rmse_test,
    'r2_test': r2_test,
    'y_test_mean': test_mean,
    'bias': '',
  }, index=[0])

# model 6: Feedforward NN
def feedforward_nn(X_train, y_train, X_test, y_test, n_train, n_test, test_mean, layers, epochs):
  # scale both X and y
  scaler_X = MinMaxScaler()
  X_train_scaled = scaler_X.fit_transform(X_train)
  X_test_scaled = scaler_X.transform(X_test)
  scaler_y = MinMaxScaler()
  y_train_scaled = scaler_y.fit_transform(y_train.to_numpy().reshape(-1, 1)).flatten()
  y_test_scaled = scaler_y.transform(y_test.to_numpy().reshape(-1, 1)).flatten()

  lays = [Dense(layers[0], activation='relu', input_shape=(X_train_scaled.shape[1],))]
  for layer in layers[1:-1]:
    lays.append(Dense(layer, activation='relu'))
  lays.append(Dense(1))
  model = Sequential(lays)

  model.compile(optimizer='adam',
    loss='mean_squared_error',
    metrics=['mean_squared_error']
  )

  # train the model
  early_stopping = EarlyStopping(monitor='loss', patience=10, restore_best_weights=True)
  history = model.fit(X_train_scaled, y_train_scaled,
    epochs=epochs,
    batch_size=32,
    #validation_split=0.2,
    callbacks=[early_stopping]
  )

  train_predictions = model.predict(X_train_scaled)
  test_predictions = model.predict(X_test_scaled)

  # scale back the predictions to the original value range
  y_train_pred = scaler_y.inverse_transform(train_predictions.reshape(-1, 1)).flatten()
  y_test_pred = scaler_y.inverse_transform(test_predictions.reshape(-1, 1)).flatten()

  mse_train = mean_squared_error(y_train, y_train_pred)
  rmse_train = np.sqrt(mse_train)
  r2_train = r2_score(y_train, y_train_pred)

  mse_test = mean_squared_error(y_test, y_test_pred)
  rmse_test = np.sqrt(mse_test)
  r2_test = r2_score(y_test, y_test_pred)

  return pd.DataFrame({
    'model_type': f"Feedforward NN ({len(layers)} layers, [{layers}] activations)",
    'n_train': n_train,
    'n_test': n_test,
    'mse_train': mse_train,
    'rmse_train': rmse_train,
    'r2_train': r2_train,
    'mse_test': mse_test,
    'rmse_test': rmse_test,
    'r2_test': r2_test,
    'y_test_mean': test_mean,
    'bias': '',
  }, index=[0])

# main func to run models
def run_regressions(player_name):
  train = pd.read_csv(f"./player_game_logs/{player_name}/{player_name}_TRAIN.csv")
  test = pd.read_csv(f"./player_game_logs/{player_name}/{player_name}_TEST.csv")

  # ablate Team/Opponent Features
  cols_to_drop = train.filter(regex='(Team|Opponent)').columns
  train = train.drop(columns=cols_to_drop)
  cols_to_drop = test.filter(regex='(Team|Opponent)').columns
  test = test.drop(columns=cols_to_drop)

  try:
    summary = pd.read_csv(f"./player_game_logs/{player_name}/{player_name}_SUMMARY_ABLATED.csv")
  except:
    summary = pd.DataFrame()

  X_train = train.drop(columns=['PTS'])
  X_test = test.drop(columns=['PTS'])
  y_train = train['PTS']
  y_test = test['PTS']

  n_train = y_train.count()
  n_test = y_test.count()
  test_mean = np.mean(y_test)

  # scale features
  scaler = MinMaxScaler()
  X_train_scaled = scaler.fit_transform(X_train)
  X_test_scaled = scaler.transform(X_test)

  # run models
  models = []
  models.append(linear_regression(X_train, X_train_scaled, y_train, X_test_scaled, y_test, n_train, n_test, test_mean))
  models.append(lasso_regression(X_train, X_train_scaled, y_train, X_test_scaled, y_test, n_train, n_test, test_mean, l=0.05))
  models.append(random_forest_regression(X_train, y_train, X_test, y_test, n_train, n_test, test_mean, n_estimators=500, max_depth=5))
  models.append(random_forest_regression(X_train, y_train, X_test, y_test, n_train, n_test, test_mean, n_estimators=100, max_depth=5))
  models.append(ridge_regression(X_train, X_train_scaled, y_train, X_test_scaled, y_test, n_train, n_test, test_mean, l=2.0))
  #models.append(svm(X_train, y_train, X_test, y_test, n_train, n_test, test_mean, 'linear'))
  #models.append(feedforward_nn(X_train, y_train, X_test, y_test, n_train, n_test, test_mean, layers=[16, 4, 1], epochs=20))

  summary_df = pd.concat([summary] + models)

  # discard old outputs
  #summary_df = summary_df[summary_df['model_type'] != 'Feedforward NN (3 layers, [[32, 16, 1]] activations)']

  summary_df.to_csv(f"./player_game_logs/{player_name}/{player_name}_SUMMARY_ABLATED.csv", index=False)

def run_model(model, model_type, X_train, y_train, X_test, y_test, col_names, n_train, n_test, test_mean):
  y_train_pred = model.predict(X_train)
  mse_train = mean_squared_error(y_train, y_train_pred)
  rmse_train = np.sqrt(mse_train)
  r2_train = r2_score(y_train, y_train_pred)

  y_pred_test = model.predict(X_test)
  mse_test = mean_squared_error(y_test, y_pred_test)
  rmse_test = np.sqrt(mse_test)
  r2_test = r2_score(y_test, y_pred_test)
  
  try:
    # linear models
    weights = {f"{col}_weight": coef for col, coef in zip(col_names, model.coef_)}
    bias = model.intercept_
  except AttributeError:
    # tree-based models
    weights = {f"{col}_weight": coef for col, coef in zip(col_names, model.feature_importances_)}
    bias = ''
  
  summary_df = pd.DataFrame({
    'model_type': model_type,
    'n_train': n_train,
    'n_test': n_test,
    'mse_train': mse_train,
    'rmse_train': rmse_train,
    'r2_train': r2_train,
    'mse_test': mse_test,
    'rmse_test': rmse_test,
    'r2_test': r2_test,
    'y_test_mean': test_mean,
    'bias': bias,
  }, index=[0])
  for key, value in weights.items():
    summary_df[key] = value
  
  return summary_df

def regression_wrapper(player_names):
  for name in player_names:
    print(f"Running regressions: {name}")
    run_regressions(name)

######## SCRIPT: run clean function on all NBA players
NUM_THREADS = 5
thread_func(NUM_THREADS, regression_wrapper, os.listdir('./player_game_logs'))

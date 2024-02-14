from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from utils import thread_func
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
    model, 'Lasso',
    X_train_scaled, y_train, X_test_scaled, y_test,
    X_train.columns, n_train, n_test, test_mean
  )

# model 3: Ridge Regression
def ridge_regression(X_train, X_train_scaled, y_train, X_test_scaled, y_test, n_train, n_test, test_mean, l):
  model = Ridge(alpha=l)
  model.fit(X_train_scaled, y_train)
  return run_model(
    model, 'Ridge',
    X_train_scaled, y_train, X_test_scaled, y_test,
    X_train.columns, n_train, n_test, test_mean
  )

# model 3: Random Forest Regression
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

def run_regressions(player_name):
  train = pd.read_csv(f"./player_game_logs/{player_name}/{player_name}_TRAIN.csv")
  test = pd.read_csv(f"./player_game_logs/{player_name}/{player_name}_TEST.csv")

  try:
    summary = pd.read_csv(f"./player_game_logs/{player_name}/{player_name}_SUMMARY.csv")
  except:
    summary = pd.DataFrame()

  # # drop columns that are zero to reduce dimensionality
  # train_columns_to_drop = [col for col in train.columns if train[col].sum() == 0]
  # test_columns_to_drop = [col for col in test.columns if test[col].sum() == 0]
  # cols_to_drop = set(train_columns_to_drop + test_columns_to_drop)
  # print(cols_to_drop)
  # train.drop(columns=cols_to_drop, inplace=True)
  # test.drop(columns=cols_to_drop, inplace=True)

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
  models.append(lasso_regression(X_train, X_train_scaled, y_train, X_test_scaled, y_test, n_train, n_test, test_mean, l=0.1))
  models.append(random_forest_regression(X_train, y_train, X_test, y_test, n_train, n_test, test_mean, n_estimators=50, max_depth=10))

  summary_df = pd.concat([summary, models])
  summary_df.to_csv(f"./player_game_logs/{player_name}/{player_name}_SUMMARY.csv", index=False)

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
    weights = {}
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
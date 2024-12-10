from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
from selenium import webdriver
import numpy as np
import threading
import time
import re
import os

def init_web_driver(width=1300, height=950):
  chrome_options = webdriver.ChromeOptions()
  chrome_options.add_argument("--disable-dev-shm-usage")
  chrome_options.add_argument("--no-sandbox")
  chrome_options.add_argument('--window-size={},{}'.format(width, height))

  if os.environ.get("ENV") == "PROD":
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
  else:
    # local dev mode
    from webdriver_manager.chrome import ChromeDriverManager
    chrome_options.add_argument('--ignore-certificate-errors')
    chromedriver_path = ChromeDriverManager().install()
    driver = webdriver.Chrome(service=webdriver.ChromeService(chromedriver_path), options=chrome_options)
  return driver

def patient_click(element, delay=1):
  element.click()
  time.sleep(delay)

def thread_func(num_threads, func, input_args):
  chunks = np.array_split(input_args, num_threads)
  threads = []
  for i in range(num_threads):
    thread = threading.Thread(target=func, args=(chunks[i],))
    threads.append(thread)

  for thread in threads:
    thread.start()
  for thread in threads:
    thread.join()

def generate_dates(start_date=datetime(2005, 10, 1)):
  end_date = datetime.now()
  delta = end_date - start_date
  date_list = [start_date + timedelta(days=i) for i in range(delta.days + 1)]
  date_strs = [date.strftime('%Y-%m-%d') for date in date_list]

  with open('./dates.py', "w") as file:
    file.write('DATES = ' + str(date_strs))
  return date_strs

# adjust date based on the date string in the game recap
def adjust_date(date_str):
  date_str = re.sub(r'(\d)(st|nd|rd|th)', r'\1', date_str)
  dt = datetime.strptime(date_str, '%A, %B %d, %Y %I:%M %p')
  if "AM" in date_str and dt.hour < 12:
    dt = dt - timedelta(days=1)
  return dt.date()

# Helper: convert time in mm:ss format to a float
def convert_time_to_float(time_series):
  split_series = time_series.split(':')
  minutes = int(split_series[0])
  seconds = int(split_series[1])
  return round(minutes + seconds / 60, 2)

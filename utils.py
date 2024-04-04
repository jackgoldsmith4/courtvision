from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
from selenium import webdriver
import numpy as np
import threading
import time
import re

def init_web_driver(width=1400, height=950):
  chrome_options = webdriver.ChromeOptions()
  chrome_options.add_argument("--disable-dev-shm-usage")
  chrome_options.add_argument("--no-sandbox")
  chrome_options.add_argument('--window-size={},{}'.format(width, height))
  chrome_options.add_argument("--headless")
  chrome_options.add_argument('--ignore-certificate-errors')
  # disable images
  chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
  return webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

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

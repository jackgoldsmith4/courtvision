from selenium import webdriver
import numpy as np
import threading
import time

def init_web_driver(width=1400, height=950):
  chrome_options = webdriver.ChromeOptions()
  chrome_options.add_argument("--disable-dev-shm-usage")
  chrome_options.add_argument("--no-sandbox")
  chrome_options.add_argument('--window-size={},{}'.format(width, height))
  chrome_options.add_argument("--headless")
  chrome_options.add_argument('--ignore-certificate-errors')
  # disable images
  chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
  return webdriver.Chrome(chrome_options=chrome_options)

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

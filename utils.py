from selenium import webdriver
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

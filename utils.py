from selenium import webdriver
import time
import os

def init_web_driver(width=1400, height=950, mobile=False):
  chrome_options = webdriver.ChromeOptions()
  chrome_options.add_argument("--disable-dev-shm-usage")
  chrome_options.add_argument("--no-sandbox")
  chrome_options.add_argument('--window-size={},{}'.format(width, height))

  if mobile:
    mobile_emulation = {
      "deviceName": 'iPhone X'
    }
    chrome_options.add_experimental_option('mobileEmulation', mobile_emulation)

  if os.environ.get("ENV") == "PROD":
    # mimic a browser in headless mode
    if not mobile:
      user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
      chrome_options.add_argument(f"--user-agent={user_agent}")

    chrome_options.add_argument("--headless")
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
  else:
    # local dev mode
    chrome_options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(chrome_options=chrome_options)

  return driver

def patient_click(element, delay=1):
  element.click()
  time.sleep(delay)

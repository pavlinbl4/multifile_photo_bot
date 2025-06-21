from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


def setting_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("webdriver.chrome.driver=chromedriver")
    chrome_options.add_argument("--headless")  # фоновый режим
    chrome_options.add_argument("--window-size=1280,800")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # невидимость автоматизации
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")
    return chrome_options

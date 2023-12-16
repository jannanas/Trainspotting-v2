import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import urllib.parse
from ..model.Exceptions import *
from datetime import datetime

class QueryService:

    def __init__(self, date=datetime(2024, 1, 31), tfl=3, md=0, checkSeats=0):
        self.session = requests.Session()
        self.params = {
            "layer_name": "e3-route",
            "code0": None,
            "code1": None,
            "dt0": date.strftime("%d.%m.%Y"),
            "tfl": tfl,
            "md": md,
            "checkSeats": checkSeats
        }
        self.url = "https://pass.rzd.ru/tickets/public/en?"
        self.headers = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
    
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        # options.add_argument('--headless')
        self.driver = webdriver.Chrome(r"D:\Jannes\Documents\Trainspotting v2\src\miner\util\chromedriver.exe", chrome_options=options)


    def setDate(self, date):
        self.params["dt0"] = date.strftime("%d.%m.%Y")


    def handleException(self, pageSource):
        soup = BeautifulSoup(pageSource, 'lxml')
        alerts = soup.find_all("div", class_="alert alert-err alert-border-ext alert-square alert-err-back")

        if len(alerts) == 0:
            raise BlankPageException
        elif alerts[0].next.text == "Request failed":
            raise InternalSystemException
        elif alerts[0].text.strip() == "No direct trains found":
            raise NoDirectJourneysException
        elif alerts[0].text.strip() == "No trains on a given date":
            raise NoJourneysOnDateException
        elif alerts[0].text.strip() == "Departure date is beyond sale range.":
            raise DateException
        else:
            raise Exception
        

    def get(self, fromStationCode, toStationCode):
        self.params["code0"] = fromStationCode
        self.params["code1"] = toStationCode

        constructedUrl = self.url + urllib.parse.urlencode(self.params)
        self.driver.get(constructedUrl)

        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//span[@class="route-timezone-switch-item j-route-timezone-switch-item timezone-msk"]'))).click()
        except:
            self.handleException(self.driver.page_source)

        return self.driver.page_source

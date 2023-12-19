from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from ..model.Exceptions import *
import logging
from .DataExtractorService import DataExtractorService 
import threading
import traceback

class QueryService:

    def __init__(self, headless=True):
        threadId = threading.current_thread().getName().split('-')[-1]
        self.logger = logging.getLogger(f"QueryService {threadId}")

        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument('--incognito')
        if headless:
            options.add_argument('--headless')
        self.driver = webdriver.Chrome(r"D:\Jannes\Documents\Trainspotting v2\src\miner\util\chromedriver.exe", options=options)


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


    def get(self, url):
        self.driver.get(url)

        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[2]/div[4]/div/div[1]/div/div[2]/div/form/div/div[2]/div/div[1]/div/span[2]'))).click()
        except:
            self.handleException(self.driver.page_source)

        return self.driver.page_source
        

    def getQuery(self, fromStationCode, toStationCode, url):
        try:
            pageSource = self.get(url)
            journeys = DataExtractorService.extract(fromStationCode, toStationCode, pageSource)
            
            #Change what is sent back and stored
            return [fromStationCode, toStationCode, len(journeys), None]
        
        except Exception as e:
            self.logger.warning(f'{type(e).__name__} for {fromStationCode} -> {toStationCode}')

            normalExceptions = [BlankPageException, InternalSystemException, NoDirectJourneysException, NoJourneysOnDateException, DateException]
            if type(e) not in normalExceptions:
                self.logger.error(traceback.format_exc())

            return [fromStationCode, toStationCode, 0, type(e).__name__]
        
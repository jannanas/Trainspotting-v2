import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from ..model.Exceptions import *
import logging
from .DataExtractorService import DataExtractorService 
import threading
import traceback
from selenium.webdriver.chrome.service import Service
import os

class QueryService:

    def __init__(self, headless=True):
        # threadId = threading.current_thread().getName().split('-')[-1]
        self.logger = logging.getLogger(f"QueryService")

        # service = Service(executable_path=r"C:\Users\janne\Documents\Trainspotting-v2\util\chromedriver.exe")
        # options = webdriver.ChromeOptions()
        # options.add_argument('--ignore-certificate-errors')
        # options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # options.add_argument('--incognito')
        # if headless:
        #     options.add_argument('--headless')
        # self.driver = webdriver.Chrome(service=service, options=options)
        # # self.driver.set_page_load_timeout(12)

        driverPath = fr"{os.getcwd()}\util\geckodriver.exe"
        service = Service(executable_path=driverPath)
        options = webdriver.FirefoxOptions()
        options.headless = headless
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        self.driver = webdriver.Firefox(service=service, options=options)



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
            #Optimize timeout
            WebDriverWait(self.driver, timeout=13).until(EC.any_of(
                EC.presence_of_element_located((By.XPATH, '//div[@class="j-sort-prop filter-sort-item active"]')),
                EC.presence_of_element_located((By.XPATH, '//div[@class="alert alert-err alert-border-ext alert-square alert-err-back"]'))
            ))
        except Exception as e:
            self.handleException(self.driver.page_source)

        if len(self.driver.find_elements(By.XPATH, '//div[@class="alert alert-err alert-border-ext alert-square alert-err-back"]')) > 0:
            self.handleException(self.driver.page_source)

        return self.driver.page_source
        

    def getQuery(self, fromStationCode, toStationCode, url):
        try:
            # startRequestTime = time.perf_counter()
            pageSource = self.get(url)
            # self.logger.debug(f"Got html in {time.perf_counter() - startRequestTime}")
            
            # startExtractTime = time.perf_counter()
            journeys = DataExtractorService.extract(fromStationCode, toStationCode, pageSource)
            # self.logger.debug(f"Extracted data in {time.perf_counter() - startExtractTime}")

            #Change what is sent back and stored depening on goal
            return [fromStationCode, toStationCode, len(journeys), None]
        
        except Exception as e:
            self.logger.warning(f'{type(e).__name__} for {fromStationCode} -> {toStationCode}')

            normalExceptions = [BlankPageException, InternalSystemException, NoDirectJourneysException, NoJourneysOnDateException, DateException]
            if type(e) not in normalExceptions:
                self.logger.error(traceback.format_exc())

            return [fromStationCode, toStationCode, 0, type(e).__name__]
        
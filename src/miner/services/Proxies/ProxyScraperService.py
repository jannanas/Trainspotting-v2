import time
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import pandas as pd
import datetime
import os

class ProxyScraperService:
    def __init__(self):
        driverPath = fr"{os.getcwd()}\util\geckodriver.exe"
        service = Service(executable_path=driverPath)
        options = webdriver.FirefoxOptions()
        options.headless = False
        options.add_argument('--ignore-certificate-errors')
        # options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument('--incognito')
        self.driver = webdriver.Firefox(service=service, options=options)


    def getHtml(self, url):
        self.driver.get(url) 

        # select = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[2]/div[1]/div[3]/div[2]/button[1]/p"))).click()

        # select = Select(WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "xpp"))))
        # select.select_by_value('5')  

        # select = Select(WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "xf5"))))
        # select.select_by_value('1')  
        
        # time.sleep(5)
        
        return self.driver.page_source


    def extractProxies(self, html):
        proxies = []

        soup = BeautifulSoup(html, 'lxml')

        for proxyHtml in soup.find_all("tr", {"class": ["spy1x", "spy1xx"]})[2:]:
            proxies.append(proxyHtml.find("td").text)

        return proxies

proxyScraper = ProxyScraperService()
html = proxyScraper.getHtml("https://spys.one/free-proxy-list/KZ/")
proxies = proxyScraper.extractProxies(html)

columns = ["proxy"]
proxiesDF = pd.DataFrame(proxies, columns=columns)

# Make filepath dynamic
fileName = f"proxies_KZ_{datetime.date.today().strftime('%d_%m_%Y')}.csv"
filePath = fr"C:\Users\janne\Documents\Trainspotting-v2\output\{fileName}"

proxiesDF.to_csv(filePath, mode='a', index=False)

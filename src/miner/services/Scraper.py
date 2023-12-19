from datetime import timedelta
from ..model.Exceptions import *
import pandas as pd
import logging
import csv
from miner.services.DataExtractorService import DataExtractorService
from miner.services.QueryService import QueryService
import time
import urllib
from concurrent.futures import ThreadPoolExecutor
import threading
import numpy as np

class Scraper:
    # Inject services to reuse them on each call
    def __init__(self):
        self.logger = logging.getLogger("Scraper")
        self.params = {
            "layer_name": "e3-route",
            "code0": None,
            "code1": None,
            "dt0": None,
            "tfl": 3,
            "md": 0,
            "checkSeats": 0
        }
        self.url = "https://pass.rzd.ru/tickets/public/en?"

        self.logger.debug(f"Loading station codes")
        self.codes = self.getCodes()
        self.logger.debug(f"Station codes loaded")


    def buildUrl(self, journeyDate, fromStationCode, toStationCode):
        self.params["code0"] = fromStationCode
        self.params["code1"] = toStationCode
        self.params["dt0"] = journeyDate.strftime("%d.%m.%Y")

        return self.url + urllib.parse.urlencode(self.params)


    def buildQueriesOnDateRange(self, fromDate, toDate):
        queryListByDate = []

        for journeyDate in self.daterange(fromDate, toDate):
            queryInfoList = []

            for indexFrom in range(1, 2): # fix upper bound
                fromStationCode = self.codes[indexFrom][3]

                for indexTo in range(indexFrom+1, 4): # fix upper bound
                    toStationCode = self.codes[indexTo][3]

                    queryInfoList.append((
                        journeyDate,
                        fromStationCode,
                        toStationCode
                    ))

            queryListByDate.append((journeyDate, queryInfoList))

        return queryListByDate


    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days + 1)):
            yield start_date + timedelta(n)
        
    
    def getCodes(self, path=r"D:\Jannes\Documents\Trainspotting v2\src\miner\util\stationcodes.csv"):
        with open(path) as csvfile:
            return list(csv.reader(csvfile))


    def scrapeJourneysOnDate(self, queryList):
        threadId = threading.current_thread().getName().split('-')[-1]
        threadLogger = logging.getLogger(f"Scraper {threadId}")

        threadLogger.debug(f"Initiated thread to scrape {len(queryList)} connections")

        journeyList = []
        queryService = QueryService(headless=True)

        # Consider implementing tab switching
        for query in queryList:
            journeyDate = query[0]
            fromStationCode = query[1]
            toStationCode = query[2]
            startTime = time.perf_counter()

            url = self.buildUrl(journeyDate, fromStationCode, toStationCode)
            journeyList.append(queryService.getQuery(fromStationCode, toStationCode, url))

            threadLogger.debug(f"Scraped {fromStationCode} -> {toStationCode} on {journeyDate} in {time.perf_counter() - startTime} seconds")
        
        #Close session
        queryService.driver.quit()

        # with ThreadPoolExecutor() as executor:
        #     results = executor.map(self.getQuery, queryList)
        #     for result in results:
        #         journeyList.append(result)        

        columns = ["fromStationCode", "toStationCode", "journeyCount", "exception"]
        journeysDF = pd.DataFrame(journeyList, columns=columns)

        # Make filepath dynamic
        fileName = f"journeys_stats_{journeyDate.strftime('%d_%m_%Y')}_{threadId}.parquet"
        filePath = fr"D:\Jannes\Documents\Trainspotting v2\output\{fileName}"

        threadLogger.info(f"Writing to {fileName}")
        startTime = time.perf_counter()
        # journeysDF.to_csv(filePath, mode='a', index=False)
        journeysDF.to_parquet(filePath, index=False)
        threadLogger.info(f"Finished writing to {fileName} in {time.perf_counter() - startTime}")


    def scrapeJourneysOnDateRange(self, fromDate, toDate, maxThreadCount=1):
        self.logger.info(f"Scraping journeys on range: {fromDate} - {toDate}")
        
        self.logger.debug(f"Building query combos")
        queryListByDate = self.buildQueriesOnDateRange(fromDate, toDate)

        for journeyDate, queryList in queryListByDate:
            startTime = time.perf_counter()
            self.logger.debug(f"Scraping journeys on {journeyDate}")

            #Decide max workers well
            splitQueryList = np.array_split(queryList, maxThreadCount)
            with ThreadPoolExecutor(max_workers=maxThreadCount) as executor:
                executor.map(self.scrapeJourneysOnDate, splitQueryList)

            self.logger.debug(f"Completed scraping journeys on {journeyDate} in {time.perf_counter() - startTime}")
        
        self.logger.info(f"Finished scraping!")


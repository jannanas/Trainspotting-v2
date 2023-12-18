from datetime import datetime, date, timedelta
from ..model.Exceptions import *
import pandas as pd
import logging
import csv
from miner.services.DataExtractorService import DataExtractorService
from miner.services.QueryService import QueryService
import time
import urllib

logger = logging.getLogger("Scraper")

class Scraper:
    # Inject services to reuse them on each call
    def __init__(self):
        self.queryService = QueryService(headless=True) 
        self.dataExtractorService = DataExtractorService()

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

        logger.debug(f"Loading station codes")
        self.codes = self.getCodes()
        logger.debug(f"Station codes loaded")


    def buildUrl(self, fromStationCode, toStationCode, journeyDate):
        self.params["code0"] = fromStationCode
        self.params["code1"] = toStationCode
        self.params["dt0"] = journeyDate.strftime("%d.%m.%Y")

        return self.url + urllib.parse.urlencode(self.params)


    def buildQueriesOnDateRange(self, fromDate, toDate):
        queryListByDate = []

        for journeyDate in self.daterange(fromDate, toDate):
            queryList = []

            for indexFrom in range(1, 4): # fix upper bound
                fromStationCode = self.codes[indexFrom][3]

                for indexTo in range(indexFrom+1, 4): # fix upper bound
                    toStationCode = self.codes[indexTo][3]

                    queryList.append((
                        fromStationCode,
                        toStationCode,
                        self.buildUrl(fromStationCode, toStationCode, journeyDate)
                    ))

            queryListByDate.append((journeyDate, queryList))
        
        return queryListByDate


    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days + 1)):
            yield start_date + timedelta(n)
        
    
    def getCodes(self, path=r"D:\Jannes\Documents\Trainspotting v2\src\miner\util\stationcodes.csv"):
        with open(path) as csvfile:
            return list(csv.reader(csvfile))


    def getQuery(self, query):
        try:
            logger.debug(f"Scraping {query[0]} -> {query[1]}: {query[2]}")

            startPageTime = time.perf_counter()
            pageSource = self.queryService.get(query[2])
            endPageTime = time.perf_counter()

            journeys = self.dataExtractorService.extract(query[0], query[1], pageSource)
            endExtractingTime = time.perf_counter()
            logger.debug(f"Loaded HTML in {endPageTime - startPageTime} seconds. Extracted data in {endExtractingTime - endPageTime} seconds.")
            
            #Change what is sent back and stored
            return (len(journeys), None)
        
        except Exception as e:
            logger.warning(f'{type(e).__name__}')
            return (0, type(e))


    def scrapeJourneysOnDate(self, journeyDate, queryList):
        # columns = ["journeyId", "fromStationCode", "toStationCode", "trainId", "trainCarrier", "journeyStart", "journeyEnd", "journeyDepartureDatetime", "journeyArrivalDatetime", "journeySeats"]
        # columns = ["journeyId", "fromStationCode", "toStationCode", "trainId", "trainCarrier", "journeyStart", "journeyEnd", "journeyDepartureDatetime", "journeyArrivalDatetime", "journeySeats"]
        journeyList = []

        for query in queryList:
            count, exception = self.getQuery(query)
            journeyList.append({
                "fromStationCode": query[0], 
                "toStationCode": query[0],
                "journeyCount": count, 
                "exception": exception
            })

        columns = ["fromStationCode", "toStationCode", "journeyCount", "exception"]
        journeysDF = pd.DataFrame(journeyList, columns=columns)

        # Make filepath dynamic
        fileName = f"journeys_stats_{journeyDate.strftime('%d_%m_%Y')}.parquet"
        filePath = fr"D:\Jannes\Documents\Trainspotting v2\output\{fileName}"
        logger.info(f"Writing to {fileName}")
        startWritingTime = time.perf_counter()

        with open(filePath, 'a') as file:
            journeysDF.to_parquet(file, mode='a', header=file.tell()==0, index=False)
        
        logger.info(f"Finished validating journeys: {journeyDate} in {time.perf_counter() - startWritingTime}")


    def scrapeJourneysOnDateRange(self, fromDate, toDate):
        logger.info(f"Scraping journeys on range: {fromDate} - {toDate}")
        
        logger.debug(f"Building urls")
        queryListByDate = self.buildQueriesOnDateRange(fromDate, toDate)

        for journeyDate, queryList in queryListByDate:
            startTime = time.perf_counter()

            logger.debug(f"Scraping journeys on {journeyDate}")
            self.scrapeJourneysOnDate(journeyDate, queryList)
            logger.debug(f"Completed scraping journeys on {journeyDate} in {time.perf_counter() - startTime}")
        
        logger.info(f"Finished scraping!")
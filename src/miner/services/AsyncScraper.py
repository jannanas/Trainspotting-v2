from datetime import datetime, date, timedelta
from ..model.Exceptions import *
import asyncio
import pandas as pd
import logging
import csv
from miner.services.DataExtractorService import DataExtractorService
from miner.services.AsyncQueryService import AsyncQueryService
import time
from requests_html import AsyncHTMLSession

logger = logging.getLogger("JourneyValidatorService")

class AsyncScraper:
    # Inject services to reuse them on each call
    def __init__(self):
        self.queryService = AsyncQueryService(headless=True) 
        self.dataExtractorService = DataExtractorService()
        logger.debug(f"Loading station codes")
        self.codes = self.getCodes()
        logger.debug(f"Station codes loaded")
        self.session = AsyncHTMLSession()


    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days + 1)):
            yield start_date + timedelta(n)


    def setDate(self, date):
        self.queryService.setDate(date)    


    def getCodes(self, path=r"D:\Jannes\Documents\Trainspotting v2\src\miner\util\stationcodes.csv"):
        with open(path) as csvfile:
            return list(csv.reader(csvfile))


    def buildUrlList(self, fromDate, toDate):
        urlListByDate = []

        for date in self.daterange(fromDate, toDate):
            urlList = []
            self.queryService.setDate(date)

            for indexFrom in range(1, 4): # fix upper bound
                fromStationCode = self.codes[indexFrom][3]

                for indexTo in range(indexFrom+1, 4): # fix upper bound
                    toStationCode = self.codes[indexTo][3]

                    urlList.append(
                        self.queryService.buildUrl(fromStationCode, toStationCode)
                    )

            urlListByDate.append((date, urlList))
        
        return urlListByDate


    async def scrapeUrl(self, url):
        try:
            logger.debug(f"Scraping: {url}")

            startPageTime = time.perf_counter()
            pageSource = await self.queryService.get(self.session, url)
            endPageTime = time.perf_counter()

            journeys = self.dataExtractorService.extract(pageSource)
            endExtractingTime = time.perf_counter()
            logger.debug(f"Loaded HTML in {endPageTime - startPageTime} seconds. Extracted data in {endExtractingTime - endPageTime} seconds.")
            
            return (len(journeys), None)
        
        except Exception as e:
            logger.warning(f'{type(e).__name__}')
            return (0, type(e).__name__)
        

    async def scrapeUrls(self, journeyDate, urlList):
        tasks = (self.scrapeUrl(url) for url in urlList)
        journeyData = await asyncio.gather(*tasks)

        #Concat all the results into a DF

        #Make filepath dynamic
        # filePath = fr"D:\Jannes\Documents\Trainspotting v2\output\validation\connections_{date.strftime('%d_%m_%Y')}.csv"
        # logger.info(f"Writing connections_{date.strftime('%d_%m_%Y')}.csv")
        # startWritingTime = time.perf_counter()
        # validated.to_csv(filePath, mode='a', index=False)
        # logger.info(f"Finished validating journeys: {date} in {time.perf_counter() - startWritingTime}")

    def scrapeJourneys(self, fromDate, toDate):
        logger.info(f"Scraping journeys on range: {fromDate} - {toDate}")
        
        logger.debug(f"Building urls")
        urlListByDate = self.buildUrlList(fromDate, toDate)

        for journeyDate, urlList in urlListByDate:
            startTime = time.perf_counter()
            logger.debug(f"Scraping journeys on {journeyDate}")
            asyncio.run(self.scrapeUrls(journeyDate, urlList))
            logger.debug(f"Completed scraping journeys on {journeyDate} in {time.perf_counter() - startTime}")
        
        logger.info(f"Finished scraping!")


    
from datetime import datetime, date, timedelta
from ..model.Exceptions import *
import pandas as pd
import logging
import csv

logger = logging.getLogger("JourneyValidatorService")

class JourneyValidatorService:
    # Inject services to reuse them on each call
    def __init__(self, queryService, dataExtractorService):
        self.queryService = queryService
        self.dataExtractorService = dataExtractorService
        logger.debug(f"Loading station codes")
        self.codes = self.getCodes()
        logger.debug(f"Station codes loaded")


    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days + 1)):
            yield start_date + timedelta(n)


    def setDate(self, date):
        self.queryService.setDate(date)    


    def getJourneys(self, fromStationCode, toStationCode):
        pageSource = self.queryService.get(fromStationCode, toStationCode)
        journeys = self.dataExtractorService.extract(pageSource)
        return journeys
        
    
    def getCodes(self, path=r"D:\Jannes\Documents\Trainspotting v2\src\miner\util\stationcodes.csv"):
        with open(path) as csvfile:
            return list(csv.reader(csvfile))


    def validateJourney(self, fromStationCode, toStationCode):
        logger.debug(f"{fromStationCode} -> {toStationCode}")
        try:
            journeys = self.getJourneys(fromStationCode, toStationCode)
            return (len(journeys), None)
        except Exception as e:
            logger.warning(f'{type(e).__name__}')
            return (0, type(e).__name__)
        
    
    def validateJourneysOnDate(self, date):
        logger.debug(f"Validating journeys: {date}")
        self.setDate(date)
        validatedList = []

        for indexFrom in range(1, 4): # fix upper bound
            fromStationCode = self.codes[indexFrom][3]

            for indexTo in range(indexFrom+1, 4): # fix upper bound
                toStationCode = self.codes[indexTo][3]

                count, exception = self.validateJourney(fromStationCode, toStationCode)

                validatedList.append({
                    "fromStationCode": fromStationCode, 
                    "toStationCode": toStationCode,
                    "journeyCount": count, 
                    "exception": exception
                })
        
        #Make filepath dynamic
        filePath = fr"D:\Jannes\Documents\Trainspotting v2\output\validation\connections_{date.strftime('%d_%m_%Y')}.csv"
        validated = pd.DataFrame(validatedList, columns=["fromStationCode", "toStationCode", "journeyCount", "exception"])
        logger.debug(f"Writing connections_{date.strftime('%d_%m_%Y')}.csv")
        validated.to_csv(filePath)


    def validateJourneys(self, fromDate, toDate):
        logger.info(f"Validating journeys on range: {fromDate} - {toDate}")
        for date in self.daterange(fromDate, toDate):
            self.validateJourneysOnDate(date)
        logger.info(f"Finished validating journeys on range: {fromDate} - {toDate}")


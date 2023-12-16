from datetime import datetime
from ..model.Exceptions import *
import traceback
import sys

class JourneyValidatorService:
    # Inject services to reuse them on each call
    def __init__(self, queryService, dataExtractorService):
        self.queryService = queryService
        self.dataExtractorService = dataExtractorService

    def setDate(self, date):
        self.queryService.setDate(date)    

    def getJourneys(self, fromStationCode, toStationCode):
        try:
            pageSource = self.queryService.get(fromStationCode, toStationCode)
            journeys = self.dataExtractorService.extract(pageSource)
            return journeys
        except Exception as e:
            print(f'{type(e)} for {fromStationCode} -> {toStationCode} on {self.queryService.params["dt0"]}')
            # print(print(traceback.format_exc()))
            return []
    
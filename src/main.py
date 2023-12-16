from miner.services.QueryService import QueryService
from miner.services.DataExtractorService import DataExtractorService
from miner.services.JourneyValidatorService import JourneyValidatorService
from datetime import datetime
import pprint

def main():
    pp = pprint.PrettyPrinter()

    # Setup services to inject
    # Reuse same queryService for queries so new connection doesnt need to be established each time
    queryService = QueryService() 
    dataExtractorService = DataExtractorService()
    journeyValidatorService = JourneyValidatorService(queryService, dataExtractorService)
    
    journeyValidatorService.setDate(datetime(2024, 5, 31))
    journeys = journeyValidatorService.getJourneys(2010000, 2060500)
    pp.pprint(journeys)

if __name__ == "__main__":
    main()
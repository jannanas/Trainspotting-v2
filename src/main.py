import logging
from miner.services.QueryService import QueryService
from miner.services.DataExtractorService import DataExtractorService
from miner.services.JourneyValidatorService import JourneyValidatorService
from datetime import datetime, date

def setupLogging():
    logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    logging.basicConfig(level=logging.NOTSET, format='%(asctime)s.%(msecs)03d %(levelname)s -- %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename=fr'D:\Jannes\Documents\Trainspotting v2\output\log\validation_{datetime.now().strftime("%Y-%m-%d--%H-%M-%S")}.log', filemode='w')
    return logging.getLogger("main")

def main():
    logger = setupLogging()
    logger.info("Started execution")

    # Setup services to inject
    # Reuse same queryService for queries so new connection doesnt need to be established each time
    queryService = QueryService(headless=True) 
    dataExtractorService = DataExtractorService()
    journeyValidatorService = JourneyValidatorService(queryService, dataExtractorService)
    
    journeyValidatorService.validateJourneys(date(2023, 12, 17), date(2023, 12, 18))
    
    logger.info("Finished execution")


if __name__ == "__main__":
    main()
   
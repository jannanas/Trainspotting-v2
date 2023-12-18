import logging
from miner.services.Scraper import Scraper
from datetime import datetime, date
import time
import traceback

def setupLogging():
    logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    logging.basicConfig(level=logging.NOTSET, format='%(asctime)s %(levelname)s -- %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename=fr'D:\Jannes\Documents\Trainspotting v2\output\log\validation_{datetime.now().strftime("%Y-%m-%d--%H-%M-%S")}.log', filemode='w')
    return logging.getLogger("main")


def main():
    logger = setupLogging()
    startTime = time.perf_counter()
    logger.info(f"Started execution")

    try:
        scraper = Scraper()
        scraper.scrapeJourneysOnDateRange(date(2023, 12, 19), date(2023, 12, 20))
    
    except Exception as e:
        logger.error(traceback.format_exc())


    logger.info(f"Finished execution in {time.perf_counter() - startTime} seconds")


if __name__ == "__main__":
    main()
   
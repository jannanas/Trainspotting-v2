import logging
from miner.services.Scraper import Scraper
from miner.services.QueryService import QueryService
from datetime import datetime, date
import time
import traceback
import os

def setupLogging():
    logging.getLogger("selenium.webdriver.common.service").setLevel(logging.WARN)
    logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    filePath = fr'{os.getcwd()}\.\output\log\scrape_{datetime.now().strftime("%Y-%m-%d--%H-%M-%S")}.log'
    logging.basicConfig(level=logging.NOTSET, format='%(asctime)s %(levelname)s %(name)s -- %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename=filePath, filemode='w')
    return logging.getLogger("main")


def main():
    logger = setupLogging()
    startTime = time.perf_counter()
    logger.info(f"Started execution")

    try:
        scraper = Scraper()
        scraper.scrapeJourneysOnDateRange(date(2023, 12, 22), date(2023, 12, 22), maxThreadCount=5)
    
    except Exception as e:
        logger.error(traceback.format_exc())

    logger.info(f"Finished execution in {time.perf_counter() - startTime} seconds")


if __name__ == "__main__":
    main()
   

# 3 x 11781 = 33343 urls to verify
    
# GOOD: minQueryTime = round(random.uniform(1, 3.8), 2)
# E[X] = 2.4 secs per request without exception

# GOOD: minQueryTime = round(random.uniform(0.5, 2.8), 2)
# E[X] = 2 secs per request without exception

# GOOD: minQueryTime = round(random.uniform(0.5, 1.9), 2)
# 1.6356979849999993 secs per url

# GOOD: minQueryTime = round(random.uniform(0.5, 1.5), 2)
# 1.2136067609999963 secs per url.

# GOOD: minQueryTime = 0
# 1.131144508999996 secs per url.
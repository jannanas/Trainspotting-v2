import logging
from miner.services.Scraper import Scraper
from miner.services.QueryService import QueryService
from datetime import datetime, date
import time
import random

def setupLogging():
    logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    logging.basicConfig(level=logging.NOTSET, format='%(asctime)s %(levelname)s %(name)s -- %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename=fr'D:\Jannes\Documents\Trainspotting v2\output\log\validation_{datetime.now().strftime("%Y-%m-%d--%H-%M-%S")}.log', filemode='w')
    return logging.getLogger("main")


def main():
    queryService = QueryService()

    urls = []
    for i in range(100):
        urls.append("https://pass.rzd.ru/tickets/public/en?layer_name=e3-route&st0=Sankt-Peterburg&code0=2004000&st1=Moscow&code1=2000000&dt0=13.03.2024&tfl=3&md=0&checkSeats=0")

    startExecTime = time.perf_counter()
    for url in urls:


        minQueryTime = 0
        startQueryTime = time.perf_counter()
        queryService.getQuery(2004000, 2000000, url)

        totalQueryTime = time.perf_counter() - startQueryTime
        if totalQueryTime < minQueryTime:
            time.sleep(minQueryTime - totalQueryTime)
            print(f"Sleeping to execute in {minQueryTime} seconds")
        else:
            print(f"Executed in {totalQueryTime} seconds")

    totalExecTime = time.perf_counter() - startExecTime
    print(f"Finished in {totalExecTime} seconds. {totalExecTime / len(urls)} secs per url.")


    # logger = setupLogging()
    # startTime = time.perf_counter()
    # logger.info(f"Started execution")

    # try:
    #     scraper = Scraper()
    #     scraper.scrapeJourneysOnDateRange(date(2023, 12, 20), date(2023, 12, 20), maxThreadCount=5)
    
    # except Exception as e:
    #     logger.error(traceback.format_exc())

    # logger.info(f"Finished execution in {time.perf_counter() - startTime} seconds")


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
from requests_html import AsyncHTMLSession
import urllib.parse
import asyncio
import time
# from ..model.Exceptions import *
from datetime import datetime
import nest_asyncio
nest_asyncio.apply()
from pyppeteer.errors import PageError
from requests_html import MaxRetries

class AsyncQueryService:

    def __init__(self, date=datetime(2024, 1, 31), tfl=3, md=0, checkSeats=0, headless=True):
        self.params = {
            "layer_name": "e3-route",
            "code0": None,
            "code1": None,
            "dt0": date.strftime("%d.%m.%Y"),
            "tfl": tfl,
            "md": md,
            "checkSeats": checkSeats
        }
        self.url = "https://pass.rzd.ru/tickets/public/en?"


    def setDate(self, date):
        self.params["dt0"] = date.strftime("%d.%m.%Y")


    # def handleException(self, pageSource):
    #     soup = BeautifulSoup(pageSource, 'lxml')
    #     alerts = soup.find_all("div", class_="alert alert-err alert-border-ext alert-square alert-err-back")

    #     if len(alerts) == 0:
    #         raise BlankPageException
    #     elif alerts[0].next.text == "Request failed":
    #         raise InternalSystemException
    #     elif alerts[0].text.strip() == "No direct trains found":
    #         raise NoDirectJourneysException
    #     elif alerts[0].text.strip() == "No trains on a given date":
    #         raise NoJourneysOnDateException
    #     elif alerts[0].text.strip() == "Departure date is beyond sale range.":
    #         raise DateException
    #     else:
    #         raise Exception
        

    def buildUrl(self, fromStationCode, toStationCode):
        self.params["code0"] = fromStationCode
        self.params["code1"] = toStationCode

        return self.url + urllib.parse.urlencode(self.params)
        

    async def get(self, asession, url):
        # try:
            time.sleep(2)
            response = await asession.get(url)
            await response.html.arender(sleep=2.5, timeout=7)
            return response.html.html
        # except ConnectionError as e:
        #     return "ConnectionError - wait a few minutes before reconnecting"
        # except PageError as e:
        #     return "PageError"
        # except MaxRetries as e:
        #     return "MaxRetries"
        # except Exception as e:
        #     return type(e).__name__


    async def main(self, urls):
        s = AsyncHTMLSession(workers=2)
        tasks = (self.get(s, url) for url in urls)
        # try:
        return await asyncio.gather(*tasks)
        # except:
        #     return tasks
        # await s.close()
        

test = AsyncQueryService()
urls = []
for i in range(1):
    urls.append("https://pass.rzd.ru/tickets/public/en?layer_name=e3-route&code0=2000000&code1=2004000&dt0=20.04.2024&tfl=3&md=0&checkSeats=0")

start = time.perf_counter()
responses = asyncio.run(test.main(urls))
print(f"{time.perf_counter() - start} second total. {(time.perf_counter() - start) / len(urls)} seconds per url")
print()

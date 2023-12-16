from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from ..model.JourneySeats import JourneySeats
from ..model.Journey import Journey
from datetime import datetime

class DataExtractorService:
    def __init__(self):
        self.dateFormat = '%d.%m.%Y%H:%M'

    def extract(self, pageElement):
        journeys = []
        journeyElements = pageElement.find_elements(By.XPATH, './/div[@class="route-item__purpose__direct"]')

        for journeyElement in journeyElements:
            trainId = self.findElementText(journeyElement, './/span[@class="route-trnum"]')
            trainCarrier = self.findElementText(journeyElement, './/span[@class="route-tr-carrier"]').split()[-1]
            journeyRoute = self.findElementText(journeyElement, './/span[@class="train-info__route-stations"]').split(" ", 3)[-1]
            
            journeyTimes = journeyElement.find_elements(By.XPATH, './/span[@class="train-info__route_time"]')
            journeyDepartureTime = journeyTimes[0].text
            journeyArrivalTime = journeyTimes[2].text

            journeyDates = journeyElement.find_elements(By.XPATH, './/span[@class="train-info__route_date"]')
            journeyDepartureDate = journeyDates[0].text
            journeyArrivalDate = journeyDates[2].text

            journeyDepartureDatetime = datetime.strptime(journeyDepartureDate + journeyDepartureTime, self.dateFormat)
            journeyArrivalDatetime = datetime.strptime(journeyArrivalDate + journeyArrivalTime, self.dateFormat)
            
            journeySeats = []
            journeySeatsElements = journeyElement.find_elements(By.XPATH, './/div[@class="route-carType-item"]')
            for journeySeatsElement in journeySeatsElements:
                journeySeatsType = self.findElementText(journeySeatsElement, './/span[@class="serv-cat"]')
                journeySeatsAvailable = int(self.findElementText(journeySeatsElement, './/span[@class="route-cartype-places-left"]').split()[-1])
                journeySeatsPrice = int(self.findElementText(journeySeatsElement, './/span[@class="route-cartype-price-rub"]').replace(",", ""))
                journeySeats.append(JourneySeats(journeySeatsType, journeySeatsAvailable, journeySeatsPrice))
            
            journeys.append(Journey(None, trainId, trainCarrier, journeyRoute, journeyDepartureDatetime, journeyArrivalDatetime, journeySeats))            
        
        return journeys
    
    def findElementText(self, element, search):
        return element.find_element(By.XPATH, search).text     

    




# from bs4 import BeautifulSoup
# from lxml import etree 

# class DataExtractorService:
#     def __init__(self):
#         pass

#     def extract(self, pageSource):
#         soup = BeautifulSoup(pageSource, 'html.parser')
#         dom = etree.HTML(str(soup))
        
#         trainElement = dom.xpath("//div[@class="j-routes route-items-cont"]")
#         trainElements = trainElement.find_all
        
#         return trainElement
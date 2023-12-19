from bs4 import BeautifulSoup
from ..model.JourneySeats import JourneySeats
from ..model.Journey import Journey
from datetime import datetime

class DataExtractorService:

    def extract(fromStationCode, toStationCode, pageSource):
        journeys = []
        dateFormat = '%d.%m.%Y%H:%M'

        soup = BeautifulSoup(pageSource, 'lxml')

        journeyElements = soup.find_all("div", class_="route-item__purpose__direct")

        for journeyElement in journeyElements:
            trainId = journeyElement.find("span", class_="route-trnum").text.strip()
            trainCarrier = journeyElement.find("span", class_="route-tr-carrier").text.strip().split(" ", 1)[-1]
            
            journeyRoute = journeyElement.find("span", class_="train-info__route-stations").text.split(" ", 2)[-1].split("\n")[2].split(" — ")
            journeyStart = journeyRoute[0].strip()
            journeyEnd = journeyRoute[1].strip()

            journeyTimes = journeyElement.find_all("span", class_="train-info__route_time")
            journeyDepartureTime = journeyTimes[0].text.strip()
            journeyArrivalTime = journeyTimes[2].text.strip()

            journeyDates = journeyElement.find_all("span", class_="train-info__route_date")
            journeyDepartureDate = journeyDates[0].text.strip()
            journeyArrivalDate = journeyDates[2].text.strip()

            journeyDepartureDatetime = datetime.strptime(journeyDepartureDate + journeyDepartureTime, dateFormat)
            journeyArrivalDatetime = datetime.strptime(journeyArrivalDate + journeyArrivalTime, dateFormat)
            
            journeySeats = []
            journeySeatsElements = journeyElement.find_all("div", class_="route-carType-item")
            for journeySeatsElement in journeySeatsElements:
                journeySeatsType = journeySeatsElement.find("span", "serv-cat").text.strip()
                journeySeatsAvailable = journeySeatsElement.find("span", "route-cartype-places-left").text.strip().split()[-1]
                journeySeatsPrice = journeySeatsElement.find("span", "route-cartype-price-rub").text.strip().replace(",", "")  
                journeySeats.append(JourneySeats(journeySeatsType, journeySeatsAvailable, journeySeatsPrice))
            
            journeys.append(Journey(None, fromStationCode, toStationCode, trainId, trainCarrier, journeyStart, journeyEnd, journeyDepartureDatetime, journeyArrivalDatetime, journeySeats))            
        
        return journeys

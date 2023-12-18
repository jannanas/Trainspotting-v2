from dataclasses import dataclass
from datetime import datetime
from .JourneySeats import JourneySeats
from typing import List

@dataclass
class Journey:
    journeyId: int
    fromStationCode: int
    toStationCode: int
    trainId: str
    trainCarrier: str
    journeyStart: str
    journeyEnd: str
    journeyDepartureDatetime: datetime
    journeyArrivalDatetime: datetime
    journeySeats: List[JourneySeats]
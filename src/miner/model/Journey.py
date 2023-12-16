from dataclasses import dataclass
from datetime import datetime
from .JourneySeats import JourneySeats
from typing import List

@dataclass
class Journey:
    journeyId: int
    trainId: str
    trainCarrier: str
    journeyRoute: str
    journeyDepartureDatetime: datetime
    journeyArrivalDatetime: datetime
    journeySeats: List[JourneySeats]

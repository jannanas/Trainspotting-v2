

class NoJourneysOnDateException(Exception):
    "Raised when no journeys are found"

# Validated
class InternalSystemException(Exception):
    "Raised when rzd has an internal error"

class DateException(Exception):
    "Raised when departure date is beyond sale range"

# Validated
class NoDirectJourneysException(Exception):
    "Raised when no direct journeys found"

# Validated
class BlankPageException(Exception):
    "Raised when page blank (most likely due to illegal parameters or internet crashing)"
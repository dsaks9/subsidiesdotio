from enum import Enum

REGIONS = [
    "Drenthe",
    "Flevoland",
    "Friesland",
    "Gelderland",
    "Groningen",
    "Limburg",
    "Noord-Brabant",
    "Noord-Holland",
    "Overijssel",
    "Utrecht",
    "Zeeland",
    "Zuid-Holland",
]

STATUS = [
    "Open",
    "Aangekondigd",
    "Gesloten"
]

class RegionEnum(str, Enum):
    DRENTHE = "Drenthe"
    FLEVOLAND = "Flevoland"
    FRIESLAND = "Friesland"
    GELDERLAND = "Gelderland"
    GRONINGEN = "Groningen"
    LIMBURG = "Limburg"
    NOORD_BRABANT = "Noord-Brabant"
    NOORD_HOLLAND = "Noord-Holland"
    OVERIJSSEL = "Overijssel"
    UTRECHT = "Utrecht"
    ZEELAND = "Zeeland"
    ZUID_HOLLAND = "Zuid-Holland"

class StatusEnum(str, Enum):
    OPEN = "Open"
    AANGEKONDIGD = "Aangekondigd"
    GESLOTEN = "Gesloten"

PARAMETER_DESCRIPTION_INCLUDE_NATIONAL = """
If the user wants to include national level reports, set this parameter to True, otherwise set it to False. The default value for include_national is True.
"""

PARAMETER_DESCRIPTION_REGIONS = """
If a specific region or regions are provided in the text, and the region or regions are one of the valid regions, include that region name.
The list of valid regions is: {REGIONS}. The default value for regions is {REGIONS}.
"""

PARAMETER_DESCRIPTION_STATUS = """
If a specific status or statuses are provided in the text, and the status or statuses are one of the valid statuses, include that status.
The list of valid statuses is: {STATUS}. The default value for status is {STATUS}.
"""

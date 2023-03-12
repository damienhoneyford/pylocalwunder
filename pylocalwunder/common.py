from decimal import Decimal
from typing import Callable

UOM_CELCIUS = '°C'
UOM_WATTS_PER_METRE_SQ = 'w/m2';
UOM_MILLIMETRE = "mm"
UOM_MILLIMETRE_PER_HOUR = "mm/h"
UOM_KILOMETRE_PER_HOUR = "km/h"

def convert_f_to_c(value: str) -> str:
    return str(round((Decimal(value) - Decimal(32)) * Decimal(5/9), 1)) if value is not None else None

def convert_in_to_mm(value: str) -> str:
    return str(round(Decimal(value) * Decimal(25.4), 2)) if value is not None else None

def convert_mph_to_kph(value:str) -> str:
    return str(round(Decimal(value) * Decimal(1.609344), 1)) if value is not None else None

class ParameterDefinition:
    input_parameter: str
    ha_sensor_id: str
    ha_sensor_name: str
    ha_sensor_uom: str
    ha_sensor_icon: str
    transform: Callable[[str], str]

    def __init__(self, input_parameter: str, ha_sensor_id: str, ha_sensor_name: str, ha_sensor_uom: str = None, ha_sensor_icon: str = None, transform: Callable[[str], str] = None):
        self.input_parameter = input_parameter
        self.ha_sensor_id = ha_sensor_id
        self.ha_sensor_name = ha_sensor_name
        self.ha_sensor_uom = ha_sensor_uom
        self.ha_sensor_icon = ha_sensor_icon
        self.transform = transform

class Configuration:
    ha_server_uri: str
    ha_long_lived_token: str
    parameter_definitions: list[ParameterDefinition]
    weather_station_uri: str = '/weatherstation/updateweatherstation.php'
    weather_station_port: int = 5723

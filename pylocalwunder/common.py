"""Includes common methods and classes"""

from decimal import Decimal
from math import sqrt
from typing import Protocol

from attr import dataclass

UOM_CELCIUS = '°C'
UOM_WATTS_PER_METRE_SQ = 'w/m2'
UOM_MILLIMETRE = "mm"
UOM_MILLIMETRE_PER_HOUR = "mm/h"
UOM_KILOMETRE_PER_HOUR = "km/h"

WS_INPUT_TEMP_FAHRENHEIT = "tempf"
WS_INPUT_DEWPOINT_FAHRENHEIT = "dewptf"
WS_INPUT_HUMIDITY = "humidity"
WS_INPUT_WIND_CHILL_FAHRENHEIT = "windchillf"
WS_INPUT_WIND_SPEED_MPH = "windspeedmph"
WS_INPUT_WIND_GUST_MPH = "windgustmph"
WS_INPUT_WIND_DIRECTION = "winddir"
WS_INPUT_RAIN_CURRENT_INCHES = "rainin"
WS_INPUT_RAIN_TODAY_INCHES = "dailyrainin"
WS_INPUT_SOLAR_RADIATION = "solarradiation"
WS_INPUT_UV = "UV"

def convert_f_to_c(**values) -> any:
    """Converts a temperature in Fahrenheit to Celcius"""
    value = values[next(iter(values))]
    return round((Decimal(value) - Decimal(32)) * Decimal(5/9), 1) if value is not None else None

def convert_in_to_mm(**values) -> any:
    """Converts a length from Inches to Millimetres"""
    value = values[next(iter(values))]
    return round(Decimal(value) * Decimal(25.4), 2) if value is not None else None

def convert_mph_to_kph(**values) -> any:
    """Converts a speed from Miles/Hour to Kilometres/Hour"""
    value = values[next(iter(values))]
    return round(Decimal(value) * Decimal(1.609344), 1) if value is not None else None

def calculate_heat_index(**values) -> any:
    """Calculates the Heat Index (i.e. Feels Like temperature)"""

    #pylint: disable=invalid-name
    C = [Decimal(-42.379), Decimal(2.04901523), Decimal(10.14333127), Decimal(-0.22475541),
         Decimal(-6.83783 * pow(10, -3)), Decimal(-5.481717 * pow(10, -2)),
         Decimal(1.22874 * pow(10, -3)), Decimal(8.5282 * pow(10, -4)),
         Decimal(-1.99 * pow(10, -6))]

    tempf = Decimal(values['tempf'])
    r_h = Decimal(values['humidity'])

    if not Decimal(0) <= r_h <= Decimal(100):
        raise ValueError('Humidity must be in the range 0-100%')
    if tempf < Decimal(40):
        heat_idx = tempf
    else:
        hi_temp = Decimal(61) + ((tempf - Decimal(68)) * Decimal(1.2)) + (r_h * Decimal(0.094))
        hi_final = Decimal(0.5) * (tempf + hi_temp)

        if hi_final > Decimal(79):
            heat_idx = (
                C[0] + C[1] * tempf + C[2] * r_h + C[3] * tempf * r_h + C[4] * pow(tempf, 2)
                + C[5] * pow(r_h, 2) + C[6] * pow(tempf, 2) * r_h + C[7] * tempf
                * pow(r_h, 2) + C[8] * pow(tempf, 2) * pow(r_h, 2)
            )
            if r_h <= Decimal(13) and Decimal(79) <= tempf <= Decimal(112):
                adj1 = Decimal((13 - r_h) / 4)
                adj2 = sqrt((17 - abs(tempf - 95)) / 17)
                heat_idx = heat_idx - (adj1 * adj2)
            elif r_h > Decimal(85) and Decimal(79) <= tempf <= Decimal(87):
                adj1 = (r_h - Decimal(85)) / Decimal(10)
                adj2 = (Decimal(87) - tempf) / Decimal(5)
                heat_idx = heat_idx - (adj1 * adj2)
        else:
            heat_idx = hi_final

    return round(heat_idx, 1)

def calculate_heat_index_c(**values) -> any:
    """Calculates the Heat Index (i.e. Feels Like temperature) in Celcius"""
    return convert_f_to_c(tempf=calculate_heat_index(**values))

#pylint: disable=too-few-public-methods
class TransformerFunc(Protocol):
    """
    Defines a method used to transform an input value ready for use in Home Assistant
    """
    def __call__(self, **kwargs) -> any:
        pass

@dataclass
class ParameterDefinition:
    """Defines how to map input parameters to Home Assistant sensor values"""
    input_parameters: list[str]
    """Specifies one or more parameters from the weather station"""
    ha_sensor_id: str
    """Specifies the Entity ID of the Sensor in Home Assistant"""
    ha_sensor_name: str
    """Specifies the Entity Name of the Sensor in Home Assistant"""
    ha_sensor_uom: str
    """Specifies the Unit of Measure of the Sensor in Home Assistant"""
    ha_sensor_icon: str
    """Specifies the Icon to use for the Sensor in Home Assistant"""
    transform: TransformerFunc
    """Specifies a function to transform the weather station input for use in Home Assistant"""

    #pylint: disable=too-many-arguments
    def __init__(self, input_parameters: list[str], ha_sensor_id: str, ha_sensor_name: str,
                 ha_sensor_uom: str = None, ha_sensor_icon: str = None,
                 transform: TransformerFunc = None):
        self.input_parameters = input_parameters
        self.ha_sensor_id = ha_sensor_id
        self.ha_sensor_name = ha_sensor_name
        self.ha_sensor_uom = ha_sensor_uom
        self.ha_sensor_icon = ha_sensor_icon
        self.transform = transform

@dataclass
class Configuration:
    """Defines the configuration of the LocalWunderServer"""
    ha_server_uri: str = None
    """
    Specifies the base URI of the Home Assistant server, e.g. http://localhost:8123/
    """
    ha_long_lived_token: str = None
    """Specifies a 'Long Lived Token' to authenticate with the Home Assistant server"""
    parameter_definitions: list[ParameterDefinition] = None
    """Specifies how to process the values sent from the weather station"""
    weather_station_uri: str = '/weatherstation/updateweatherstation.php'
    """Specifies the URI that will accept uploaded values from the weather station"""
    weather_station_port: int = 5723
    """Specifies the port that will listen for uploaded values from the weather station"""

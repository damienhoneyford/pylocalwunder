"""Used as the entry point when debugging"""

import logging
from aiohttp import web

from pylocalwunder.common import (UOM_CELCIUS, WS_INPUT_HUMIDITY, WS_INPUT_TEMP_FAHRENHEIT,
                                  Configuration, calculate_heat_index_c, convert_f_to_c)
from pylocalwunder.common import ParameterDefinition
from pylocalwunder.localwunderserver import LocalWunderServer

my_config = Configuration()
my_config.ha_server_uri = 'http://localhost:8123/'
my_config.ha_long_lived_token = '{YOUR TOKEN HERE}'
my_config.weather_station_port = 8080
my_config.parameter_definitions = [
    ParameterDefinition([WS_INPUT_TEMP_FAHRENHEIT], 'wupws_temp', 'Temperature', UOM_CELCIUS,
                        'mdi:thermometer', convert_f_to_c),
    ParameterDefinition([WS_INPUT_TEMP_FAHRENHEIT, WS_INPUT_HUMIDITY],
                        'wupws_heatindex', 'Heat Index', UOM_CELCIUS, 'mdi:thermometer',
                        calculate_heat_index_c)
]

logging.basicConfig(level=logging.DEBUG)

local_wunder_server = LocalWunderServer(my_config)
web.run_app(local_wunder_server.application, port=my_config.weather_station_port)

from aiohttp import web
import logging

from pylocalwunder import common
from pylocalwunder.localwunderserver import LocalWunderServer

my_config = common.Configuration()

logging.basicConfig(level=logging.DEBUG)

local_wunder_server = LocalWunderServer(my_config)
web.run_app(local_wunder_server.application, port=my_config.weather_station_port)

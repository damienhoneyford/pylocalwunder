"""Used as the entry point for running via Gunicorn"""

from pylocalwunder.common import *
from pylocalwunder.localwunderserver import LocalWunderServer

my_config = Configuration()

local_wunder_server = LocalWunderServer(my_config)
web_app = local_wunder_server.application

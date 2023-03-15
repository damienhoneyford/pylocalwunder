"""Provides the LocalWunderServer functionality"""
import logging
import asyncio
from aiohttp import ClientSession
from aiohttp.web import Application, Request, HTTPOk
import simplejson as json

from . import common

class LocalWunderServer:
    """
    Provides a HTTP server with a Weather Underground-like upload API which can be used by
    weather stations to directly update sensors in Home Assistant
    """
    application: Application = None
    client_session: ClientSession = None
    config: common.Configuration = None

    def __init__(self, config: common.Configuration) -> None:
        self.config = config
        self.application = Application()
        self.application.router.add_get(self.config.weather_station_uri,
                                        self.update_weather_station)
        self.application.on_startup.append(self.create_client_session)
        self.application.on_shutdown.append(self.cleanup_client_session)

    async def update_weather_station(self, request: Request):
        """
        Receives the updated values from the weather station and sends them on to
        Home Assistant as required by the Configuration
        """
        for param in self.config.parameter_definitions:
            input_params = dict((k, request.query.get(k)) for k in param.input_parameters)

            asyncio.create_task(self.update_home_assistant(param, input_params))

        return HTTPOk()

    async def update_home_assistant(self, parameter: common.ParameterDefinition,
                                    values: dict[str, str]):
        """Updates individual Home Assistant sensors with the value(s) from the weather station"""
        val = values[next(iter(values))]
        if parameter.transform is not None:
            val = parameter.transform(**values)

        attrs = { 'unit_of_measurement': parameter.ha_sensor_uom or '',
                  'icon': parameter.ha_sensor_icon or '',
                  'friendly_name': parameter.ha_sensor_name }
        payload = json.dumps({'state': val, 'attributes': attrs })
        logging.info("Updating Sensor %s, JSON payload: %s", parameter.ha_sensor_id, payload)

        try:
            sensor_id = f'/api/states/sensor.{parameter.ha_sensor_id}'
            async with self.client_session.post(sensor_id, data = payload) as resp:
                logging.info('Sent request to %s, got result %s', resp.url, resp.status)
        except Exception as ex: #pylint: disable=broad-except
            logging.error("Failed to update Home Assistant Sensor %s due to error:\r\n%s",
                          parameter.ha_sensor_id, ex)

    async def create_client_session(self, _app):
        """Initializes dependencies"""
        auth_header = ('Authorization', f'Bearer {self.config.ha_long_lived_token}')
        self.client_session = ClientSession(self.config.ha_server_uri, headers = [auth_header])

    async def cleanup_client_session(self, _app):
        """Cleans up dependencies"""
        await self.client_session.close()

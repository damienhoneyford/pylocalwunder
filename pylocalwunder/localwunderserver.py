import asyncio
import logging
from aiohttp import web
import aiohttp

import common

class LocalWunderServer:
    application: web.Application = None
    client_session: aiohttp.ClientSession = None
    config: common.Configuration = None

    def __init__(self, config: common.Configuration) -> None:
        self.config = config
        self.application = web.Application()
        self.application.router.add_get(self.config.weather_station_uri, self.update_weather_station)
        self.application.on_startup.append(self.create_client_session);
        self.application.on_shutdown.append(self.cleanup_client_session);

    async def update_weather_station(self, request: web.Request):
        for p in self.config.parameter_definitions:
            val = request.query.get(p.input_parameter)

            if val is not None:
                asyncio.create_task(self.update_home_assistant(p, val))

        return web.HTTPOk()

    async def update_home_assistant(self, parameter: common.ParameterDefinition, val: str):
        if parameter.transform is not None:
            val = parameter.transform(val)

        async with self.client_session.post(f'/api/states/sensor.{parameter.ha_sensor_id}', json={'state': val, 'attributes': { 'unit_of_measurement': parameter.ha_sensor_uom or '', 'icon': parameter.ha_sensor_icon or '', 'friendly_name': parameter.ha_sensor_name }}) as resp:
            logging.info(f'Sent request to {resp.url}, got result {resp.status}')

    async def create_client_session(self, app: web.Application):
        self.client_session = aiohttp.ClientSession(self.config.ha_server_uri, headers = [('Authorization', f'Bearer {self.config.ha_long_lived_token}')])

    async def cleanup_client_session(self, app: web.Application):
        await self.client_session.close()


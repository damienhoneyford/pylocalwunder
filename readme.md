# pylocalwunder
A local Weather Underground PWS server that relays weather data to Home Assistant.

Some weather stations allow you to setup Custom integrations that work like existing ones,
allowing you to host a server locally that your weather station can upload readings to,
which can then be sent to HTTP Sensors in Home Assistant.

# Motivation
For some reason my PWS on Weather Underground went offline, even though my weather station
is still sending it readings, leaving me without any weather data in my home automation
server (Home Assistant).

When I noticed my weather station allow me to direct weather readings to custom end points
I set about creating this, and now I have weather readings back in Home Assistant and with
a far higher frequency than they were originally when using the WundergroundPWS integration
to pull data out of Weather Underground.
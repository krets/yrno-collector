#!/usr/bin/python3
"""
Intent: collect pressure into the future
This should help predict Penelope's freak-outs.

yr.no is very generous in their API, so it is important to provide:
 - a useful user-agent "yrno_collector/0.2 someemail@example.com"
 - caching to avoid repeated requests
 - Creative Commons attribution where appropriate.


https://api.met.no/weatherapi/locationforecast/2.0/complete?altitude=40&lat=52.50&lon=13.45


"""
from datetime import timedelta, datetime
import time

import requests_cache
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY

__version__ = "0.2"
__app__ = "yrno_collector"
__email__ = "jesse@krets.com"
HEADERS = {
    'User-Agent': f"{__app__}/{__version__} {__email__}"
}
URL = "https://api.met.no/weatherapi/locationforecast/2.0/complete.json"
LOCATIONS = {
    "Berlin": {
        "altitude": 40,
        "lat": 52.5,
        "lon": 13.45
    },
    "Laconia": {
        "altitude": 154,
        "lat": 43.6042,
        "lon": -71.5001
    },
    "Harpenden": {
        "altitude": 128,
        "lat": 51.8180,
        "lon": -0.3510
    },
    "NewYorkCity": {
        "altitude": 10,
        "lat": 40.7128,
        "lon": -74.0060
    },
    "LosAngeles": {
        "altitude": 55,
        "lat": 34.0631,
        "lon": -118.3455
    }
}
_DATETIME_FMT = "%Y-%m-%dT%H:%M:%SZ"
PORT = 9991

def convert_datetimes(data):
    new_data = []
    for entry in data:
        entry['time'] = datetime.strptime(entry['time'], _DATETIME_FMT)
        new_data.append(entry)
    return new_data


class Forecast(object):

    def __init__(self, location, url=URL, params=None):
        self.session = requests_cache.CachedSession(__app__, cache_control=True, expire_after=timedelta(hours=1))
        self.session.headers.update(HEADERS)
        self.url = url
        self.params = params
        self.location = location

    def collect(self):
        res = self.session.get(self.url, params=self.params)
        data = res.json()['properties']['timeseries']
        now = datetime.utcnow()
        gauges = {}
        for entry in data:
            timestamp = datetime.strptime(entry['time'], _DATETIME_FMT)
            hours = "%d" % ((timestamp-now).total_seconds() // 60 // 60)

            details = entry['data']['instant']['details']
            try:
                details.update(entry['data']['next_1_hours']['details'])
            except KeyError:
                pass
            for key, val in details.items():
                gauge = gauges.get(key)
                if not gauge:
                    gauge = GaugeMetricFamily("yrno_" + key, key, labels=["hours", "location"])
                    gauges[key] = gauge
                gauge.add_metric([hours, self.location], val)
        for gauge in gauges.values():
            yield gauge


def main():
    start_http_server(PORT)
    for name, params in LOCATIONS.items():
        REGISTRY.register(Forecast(name, params=params))
    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()


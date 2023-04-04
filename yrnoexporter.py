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
__email__ = "<YOUR_EMAIL@whatever.com>"
HEADERS = {
    'User-Agent': f"{__app__}/{__version__} {__email__}"
}
URL = "https://api.met.no/weatherapi/locationforecast/2.0/complete.json"
LOCATIONS = {
    "Berlin": {
        "altitude": 40,
        "lat": 52.5,
        "lon": 13.45
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

    def __init__(self, url=URL, params=None):
        self.session = requests_cache.CachedSession(__app__, cache_control=True, expire_after=timedelta(hours=1))
        self.session.headers.update(HEADERS)
        self.url = url
        self.params = params

    def collect(self):
        res = self.session.get(self.url, params=self.params)
        data = res.json()['properties']['timeseries']
        now = datetime.utcnow()
        gauges = {}
        for entry in data:
            timestamp = datetime.strptime(entry['time'], _DATETIME_FMT)
            hours = "%d" % ((timestamp-now).total_seconds() // 60 // 60)
            for key, val in entry['data']['instant']['details'].items():
                gauge = gauges.get(key)
                if not gauge:
                    gauge = GaugeMetricFamily("yrno_" + key, key, labels=["hours"])
                    gauges[key] = gauge
                gauge.add_metric([hours], val)
        for gauge in gauges.values():
            yield gauge


def main():
    start_http_server(PORT)
    REGISTRY.register(Forecast(params=LOCATIONS["Berlin"]))
    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()


# Yr.no Prometheus Exporter

This is a Prometheus exporter that collects weather data from the yr.no API and exposes it as Prometheus metrics. Each metric is prefixed with `yrno_` and labeled with the number of hours into the future that it is predicted.

The metrics calls are cached using requests-cache, and the yr.no API. Please read their terms of service before running any of this code.

https://developer.yr.no/doc/TermsOfService/

## Metrics

The exporter collects the following metrics (and more), each labeled with `location` and `hours` (hours into the future the value is predicted for):

- `yrno_air_temperature{hours="<x>", location="<loc>"}`: Temperature in Celsius for `<x>` hours ahead.
- `yrno_wind_speed{hours="<x>", location="<loc>"}`: Wind speed in meters per second for `<x>` hours ahead.
- `yrno_relative_humidity{hours="<x>", location="<loc>"}`: Relative humidity in percent for `<x>` hours ahead.
- `yrno_air_pressure_at_sea_level{hours="<x>", location="<loc>"}`: .

## Running

With Docker Compose:

```
docker compose up -d --build
```

Metrics are then available at `http://localhost:9991/metrics`. The HTTP cache persists in the `yrno-cache` named volume, so restarts don't hammer the yr.no API. Override the cache location by setting `YRNO_CACHE_DIR` in the environment.

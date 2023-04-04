# Yr.no Prometheus Exporter

This is a Prometheus exporter that collects weather data from the yr.no API and exposes it as Prometheus metrics. Each metric is prefixed with `yrno_` and labeled with the number of hours into the future that it is predicted.

The metrics calls are cached using requests-cache, and the yr.no API. Please read their terms of service before running any of this code.

https://developer.yr.no/doc/TermsOfService/

## Metrics

The exporter collects the following metrics (and more):

- `yrno_air_temperature{hours="<x>"}`: Temperature in Celsius for `<x>` hours ahead.
- `yrno_wind_speed{hours="<x>"}`: Wind speed in meters per second for `<x>` hours ahead.
- `yrno_relative_humidity{hours="<x>"}`: Relative humidity in percent for `<x>` hours ahead.
- `yrno_air_pressure_at_sea_level{hours="<x>"}`: .

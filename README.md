# Weather Station
Small weather station using Raspberry Pi 2 and Raspberry Pi Zero W

# Sensors
All code related to sensors is located in `sensors/` folder.

Supported sensors:
* DHT11
* BMP180
* TEMT6000
* YL-69 with YL-38

## Running sensor publishing as service

**BEWARE**: Change path to your local copy of repo in `sensors/weather-station.service` before doing anything with it.

In order to run sensors publisher copy `sensors/weather-station.service` to `/etc/systemd/system/` and run `sudo systemctl enable weather-station.service && sudo systemctl start weather-station.service`.

# MQTT Topics
MQTT topics are set as follows: `home/ws/<sensor,actor>/<name of sensor/actor>`

Currently published topics:
* home/ws/sensor/temperature
* home/ws/sensor/humidity
* home/ws/sensor/pressure
* home/ws/sensor/light
* home/ws/sensor/moisture

import Adafruit_BMP.BMP085 as BMP085
import logging

log = logging.getLogger(__name__)

# Initialize sensor BMP185 (library is the same as for previous model BMP085)
bmp = BMP085.BMP085()

def read():
	"""
	Read data from BMP180 sensor. Available data:
		* temperature
		* pressure (sea level and normal)
	"""
	log.debug("Reading BMP180 sensor")
	r = range(5)
    vals = {
            "temperature" : [bmp.read_temperature() for _ in r],
            "pressure" : [bmp.read_pressure() for _ in r],
            "alt" : [bmp.read_altitude() for _ in r],
            "sea_pressure" : [bmp.read_sealevel_pressure() for _ in r]
            }

    return({
            "temperature" : average(vals['temperature']),
            "pressure" : average(vals['pressure']),
            "alt" :  average(vals['alt'])),
            "sea_pressure" :  average(vals['sea_pressure'])
            })

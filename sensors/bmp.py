import Adafruit_BMP.BMP085 as BMP085
import logging

log = logging.getLogger(__name__)

# Initialize sensor BMP185 (library is the same as for previous model BMP085)
bmp = BMP085.BMP085()

def read_bmp():
	"""
	Read data from BMP180 sensor. Available data:
		* temperature
		* pressure (sea level and normal)
	"""
	log.debug("Reading BMP180 sensor")
	return({
		"temperature" : bmp.read_temperature(),
		"pressure" : bmp.read_pressure(),
		"alt" : int(bmp.read_altitude()),
		"sea_pressure" : bmp.read_sealevel_pressure()
		})


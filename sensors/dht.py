import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../modules'))

from DHT11_Python import dht11
import logging

log = logging.getLogger(__name__)

# Set DHT11 to read data from pin 4
dht = dht11.DHT11(pin=4)

def read():
	"""
	For reading DHT11 sensor which is very unreliable
	"""
	log.debug("Reading DHT11 sensor")
	return dht.read()


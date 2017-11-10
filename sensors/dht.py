import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../modules'))

from DHT11_Python import dht11
import logging

from average import average

log = logging.getLogger(__name__)

# Set DHT11 to read data from pin 4
dht = dht11.DHT11(pin=4)

def read():
	"""
	For reading DHT11 sensor which is very unreliable
	"""
	log.debug("Reading DHT11 sensor")
	vals = []

    for i in range(5):
        vals.append(dht.read())
	return (average(vals))


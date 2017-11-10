import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import logging

from average import average

log = logging.getLogger(__name__)

# Software SPI configuration:
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

def read():
	log.debug("Reading light sensor")
	vals = []

    for i in range(5):
        vals.append(mcp.read_adc(0))

	return(average(vals))

if __name__ == "__main__":
	print(read())

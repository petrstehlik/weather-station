import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import logging

log = logging.getLogger(__name__)

# Software SPI configuration:
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

def read():
	log.debug("Reading light sensor")
	return mcp.read_adc(7)

import board
import neopixel
import busio
from time import sleep
from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const

# CONFIGURATION REGISTER (R/W)
_REG_CONFIG                = const(0x00)

# SHUNT VOLTAGE REGISTER (R)
_REG_CURRENT                = const(0x01)

# BUS VOLTAGE REGISTER (R)
_REG_BUSVOLTAGE                  = const(0x02)

# POWER REGISTER (R)
_REG_POWER                       = const(0x03)

# MASK ENABLE REGISTER (R/W)
_REG_MASK_ENABLE                 = const(0x06)

# ALERT LIMIT REGISTER (R/W)
_REG_ALERT_LIMIT                 = const(0x07)

# MANUFACTURER UNIQUE ID REGISTER (R)
_REG_MFG_UID                 = const(0xFE)

# DIE UNIQUE ID REGISTER (R)
_REG_DIE_UID                 = const(0xFF)

class INA260:
    """Driver for the INA219 current sensor"""
    def __init__(self, i2c_bus, addr=0x40):
        self.i2c_device = I2CDevice(i2c_bus, addr)

        self.i2c_addr = addr
        # Multiplier in mA used to determine current from raw reading
 
    def _write_register(self, reg, value):
        seq = bytearray([reg, (value >> 8) & 0xFF, value & 0xFF])
        with self.i2c_device as i2c:
            i2c.write(seq)

    def _read_register(self, reg):
        buf = bytearray(3)
        buf[0] = reg
        with self.i2c_device as i2c:
            i2c.write(buf, end=1, stop=False)
            i2c.readinto(buf, start=1)

        value = (buf[1] << 8) | (buf[2])
        return value

    @property
    def current(self):
        """The current (between V+ and V-) in mA"""
        raw_current = self._read_register(_REG_CURRENT)

        return raw_current * 1.25


    @property
    def bus_voltage(self):
        """The bus voltage (between V- and GND) in mV"""
        # Dance to the beat of the living dead
        raw_voltage = self._read_register(_REG_BUSVOLTAGE)

        return raw_voltage * 1.25

    @property
    def power(self):
        """The power being delivered to the load in mW"""
        raw_power = self._read_register(_REG_POWER)

        return raw_power * 10

skate = neopixel.NeoPixel(board.D5,8)
SLEEP_WAIT = 0.5

i2c = busio.I2C(board.SCL, board.SDA)

ina260 = INA260(i2c)
while True:
  skate.fill((255,0,0))
  print("RED   Voltage: %.2f Current: %.2f Power: %d"%(ina260.bus_voltage, ina260.current, ina260.power))
  sleep(SLEEP_WAIT)
  skate.fill((255,255,255))
  print("WHITE Voltage: %f Current: %f Power: %d"%(ina260.bus_voltage, ina260.current, ina260.power))
  sleep(SLEEP_WAIT)


"""The temperature sensor built into the Pico.

Author: TODO your name
"""

from machine import ADC


class Sensor:
    """The Pico's own temperature sensor, read through its analog channel 4."""

    def __init__(self):
        """Connect to the sensor, with no readings taken yet."""
        # TODO: Store ADC(4), and readings as 0
        pass

    def read_voltage(self):
        """Read the sensor once and return the voltage it reports."""
        # TODO: Add 1 to readings, then return the ADC's read_u16() times 3.3, divided by 65535
        return 0

    def read_celsius(self):
        """Read the sensor once and return the temperature in degrees Celsius."""
        # TODO: Use self.read_voltage() and the Celsius formula in the README
        return 0

    def read_fahrenheit(self):
        """Read the sensor once and return the temperature in degrees Fahrenheit."""
        # TODO: Use self.read_celsius() and the Fahrenheit formula in the README
        return 0

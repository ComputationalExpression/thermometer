"""The two temperature sensors: the DHT22 in the air, and the one inside the Pico's chip.

Author: TODO your name
"""

import dht
from machine import ADC, Pin


class Sensors:
    # TODO: Write a docstring for the class: Sensors holds the DHT22 that measures the air, and
    # the sensor inside the Pico's chip

    def __init__(self, air_pin):
        # TODO: Write a docstring: this method connects to both sensors, with no air reading
        # taken yet
        # TODO: Assign ADC(4) to an attribute, such as self.chip, so the other methods can read
        # the chip's sensor through it
        # TODO: Assign dht.DHT22(Pin(air_pin)) to an attribute, such as self.air, so the other
        # methods can measure the air through it
        # TODO: Assign 0 to each of the attributes self.air_celsius, self.humidity and
        # self.readings
        pass

    def read_air(self):
        # TODO: Write a docstring: this method measures the air once, and keeps its temperature
        # and humidity
        # TODO: Call .measure() on your DHT22 attribute, so the sensor takes a new reading
        # TODO: Assign the DHT22's .temperature() to self.air_celsius, and its .humidity() to
        # self.humidity
        # TODO: Add 1 to self.readings
        pass

    def air_fahrenheit(self):
        # TODO: Write a docstring: this method returns the temperature of the air from the last
        # reading, in degrees Fahrenheit
        # TODO: Use the Fahrenheit formula in the README to turn self.air_celsius into degrees
        # Fahrenheit, and return the result
        return 0

    def chip_fahrenheit(self):
        # TODO: Write a docstring: this method reads the sensor inside the chip once and returns
        # its temperature in degrees Fahrenheit
        # TODO: Call .read_u16() on your ADC attribute to get the reading, then use the formulas
        # in the README to turn it into volts, then degrees Celsius, then degrees Fahrenheit, and
        # return the result
        return 0

    def difference(self):
        # TODO: Write a docstring: this method returns how many degrees warmer the chip is than
        # the air
        # TODO: Call self.chip_fahrenheit() and self.air_fahrenheit() to get the two
        # temperatures, and return the chip's minus the air's
        return 0

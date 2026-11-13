"""The temperature sensor built into the Pico.

Author: TODO your name
"""

from machine import ADC


class Sensor:
    # TODO: Write a docstring for the class: a Sensor is the Pico's own temperature sensor, read
    # through its analog channel 4

    def __init__(self):
        # TODO: Write a docstring: this method connects to the sensor, with no readings taken yet
        # TODO: Assign ADC(4) to an attribute, such as self.adc, so the other methods can read
        # the sensor through it
        # TODO: Assign 0 to the attribute self.readings
        pass

    def read_voltage(self):
        # TODO: Write a docstring: this method reads the sensor once and returns the voltage
        # TODO: Add 1 to self.readings
        # TODO: Call read_u16() on your ADC attribute to get the reading, multiply it by 3.3,
        # divide it by 65535, and return the result
        return 0

    def read_celsius(self):
        # TODO: Write a docstring: this method reads the sensor once and returns the temperature
        # in degrees Celsius
        # TODO: Call self.read_voltage() to get the voltage, then use the Celsius formula in the
        # README to turn that voltage into degrees Celsius, and return the result
        return 0

    def read_fahrenheit(self):
        # TODO: Write a docstring: this method reads the sensor once and returns the temperature
        # in degrees Fahrenheit
        # TODO: Call self.read_celsius() to get the temperature in Celsius, then use the
        # Fahrenheit formula in the README to turn it into degrees Fahrenheit, and return the result
        return 0

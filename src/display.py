"""Three LEDs that show the temperature level.

Author: TODO your name
"""

from time import sleep

from machine import Pin


class Display:
    """One LED for each level, with at most one of them on."""

    def __init__(self, hot_pin, warm_pin, cold_pin):
        """Make an output pin for each level and start with the LEDs off."""
        # TODO: Store a dictionary of three output Pins with the keys "hot", "warm" and "cold"
        self.lights = {}
        # TODO: Store showing as "off", then turn the LEDs off with self.all_off()

    def all_off(self):
        """Turn the three LEDs off."""
        # TODO: Loop over the dictionary to turn each LED off, then set showing to "off"
        pass

    def show(self, level):
        """Light the LED for one level, and only that one."""
        # TODO: Turn the others off first, then light this level's LED and set showing to the level
        pass

    def test_lights(self):
        """Light the three LEDs for one second, so a loose wire shows before the readings start."""
        # TODO: Turn each LED on, sleep(1), then turn them all off
        pass

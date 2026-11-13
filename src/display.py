"""Three LEDs that show the temperature level.

Author: TODO your name
"""

from time import sleep

from machine import Pin


class Display:
    # TODO: Write a docstring for the class: a Display has one LED for each temperature level,
    # with at most one of them on

    def __init__(self, hot_pin, warm_pin, cold_pin):
        # TODO: Write a docstring: this method makes an output pin for each level and starts with
        # the LEDs off
        # TODO: Assign to the attribute self.lights a dictionary with the keys "hot", "warm" and
        # "cold", where each value is an output Pin: Pin(hot_pin, Pin.OUT) for "hot", and the
        # same for the other two
        # TODO: Assign "off" to the attribute self.showing
        # TODO: Call self.all_off() so the LEDs start dark
        pass

    def all_off(self):
        # TODO: Write a docstring: this method turns the three LEDs off
        # TODO: Loop over the keys of self.lights, and call .off() on the Pin for each key
        # TODO: Assign "off" to self.showing
        pass

    def show(self, level):
        # TODO: Write a docstring: this method lights the LED for one level, and only that one
        # TODO: Call self.all_off() to turn the three LEDs off, so that only one is on at the end
        # TODO: Call .on() on the Pin for level in self.lights
        # TODO: Assign level to self.showing
        pass

    def flash(self, level):
        # TODO: Write a docstring: this method lights the LED for one level for half a second,
        # then turns it off
        # TODO: Call self.show(level) to light it, then sleep(0.5), then call self.all_off()
        pass

    def test_lights(self):
        # TODO: Write a docstring: this method lights the three LEDs for one second, so a loose
        # wire shows before the readings start
        # TODO: Loop over the keys of self.lights, and call .on() on the Pin for each key
        # TODO: Call sleep(1), then call self.all_off()
        pass

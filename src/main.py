"""Lab 8: Thermometer.

A thermometer that reads the Pico's own temperature sensor, lights one of three LEDs for cold,
warm or hot, and keeps a log of what it read. Press the button to stop early.

This file is provided. Your team writes the four classes it uses.

Author: The Thermometer team
"""

from time import sleep

from machine import Pin

from display import Display
from levels import Levels
from log import Log
from sensor import Sensor

# Degrees Fahrenheit. Change these to try the lights at the temperature of your room
COLD_BELOW = 70
HOT_ABOVE = 80


def main():
    """Take a number of readings, one a second, then print the thermometer log."""
    print("=" * 50)
    print("THERMOMETER")
    print("=" * 50)
    place = input("Where is the thermometer? ")
    wanted = int(input("How many readings should it take? "))

    # The GP numbers match the Lab 7 circuit, so the board needs no new wiring
    sensor = Sensor()
    levels = Levels(COLD_BELOW, HOT_ABOVE)
    display = Display(15, 14, 13)
    log = Log(place)
    button = Pin(16, Pin.IN, Pin.PULL_UP)

    display.test_lights()
    print("Press the button to stop early")
    stopped = False
    reading = 1
    while reading <= wanted and not stopped:
        fahrenheit = sensor.read_fahrenheit()
        level = levels.level(fahrenheit)
        display.show(level)
        log.record(fahrenheit, level)
        print(f"Reading {reading}: {levels.describe(fahrenheit)}")
        sleep(1)
        # The button is read after a reading, so the log has at least one temperature
        if button.value() == 0:
            stopped = True
            print("Stopped by the button")
        reading += 1
    display.all_off()

    print()
    print("=" * 50)
    print(f"THERMOMETER LOG: {place}")
    print("=" * 50)
    print(f"Readings: {sensor.readings}")
    print(f"Highest: {round(log.highest(), 1)}")
    print(f"Lowest: {round(log.lowest(), 1)}")
    print(f"Average: {round(log.average(), 1)}")
    print(f"Cold: {log.counts['cold']}")
    print(f"Warm: {log.counts['warm']}")
    print(f"Hot: {log.counts['hot']}")
    print(f"Comfortable now: {levels.is_comfortable(fahrenheit)}")


if __name__ == "__main__":
    main()

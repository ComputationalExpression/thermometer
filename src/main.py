"""Lab 8: Thermometer.

A thermometer that measures the air with a DHT22, lights one of three LEDs for cold, warm or hot,
and flashes it when the air is too dry or too humid. It also reads the sensor inside the Pico's
chip, to compare the two thermometers. Press the button to stop early.

This file is provided. Your team writes the four classes it uses.

Author: The Thermometer team
"""

from time import sleep

from machine import Pin

from comfort import Comfort
from display import Display
from log import Log
from sensors import Sensors

# Your team's dividing values, in degrees Fahrenheit and percent humidity. Set them for your room
COLD_BELOW = 68
HOT_ABOVE = 78
DRY_BELOW = 30
HUMID_ABOVE = 60


def main():
    """Take a number of readings, one every two seconds, then print the thermometer log."""
    print("=" * 50)
    print("THERMOMETER")
    print("=" * 50)
    place = input("Where is the thermometer? ")
    wanted = int(input("How many readings should it take? "))

    # The DHT22 is on GP2, and the LEDs and button match the Lab 7 circuit
    sensors = Sensors(2)
    comfort = Comfort(COLD_BELOW, HOT_ABOVE, DRY_BELOW, HUMID_ABOVE)
    display = Display(15, 14, 13)
    log = Log(place)
    button = Pin(16, Pin.IN, Pin.PULL_UP)

    display.test_lights()
    print("Press the button to stop early")
    stopped = False
    reading = 1
    while reading <= wanted and not stopped:
        sensors.read_air()
        fahrenheit = sensors.air_fahrenheit()
        humidity = sensors.humidity
        level = comfort.level(fahrenheit)
        log.record(fahrenheit, humidity, level)
        print(f"Reading {reading}: {comfort.describe(fahrenheit, humidity)}")
        # A steady light means comfortable humidity, and a flashing light means too dry or too humid.
        # Either way the loop waits two seconds, because the DHT22 needs that long between readings
        if comfort.humidity_level(humidity) == "comfortable":
            display.show(level)
            sleep(2)
        else:
            for flash in range(2):
                display.flash(level)
                sleep(0.5)
        # The button is read after a reading, so the log has at least one
        if button.value() == 0:
            stopped = True
            print("Stopped by the button")
        reading += 1
    display.all_off()

    print()
    print("=" * 50)
    print(f"THERMOMETER LOG: {place}")
    print("=" * 50)
    print(f"Readings: {sensors.readings}")
    print(f"Highest: {round(log.highest(), 1)}")
    print(f"Lowest: {round(log.lowest(), 1)}")
    print(f"Average humidity: {round(log.average_humidity(), 1)}")
    print(f"Cold readings: {log.counts['cold']}")
    print(f"Warm readings: {log.counts['warm']}")
    print(f"Hot readings: {log.counts['hot']}")
    print(f"Chip minus air: {round(sensors.difference(), 1)}")
    print(f"Comfortable now: {comfort.is_comfortable(fahrenheit, humidity)}")


if __name__ == "__main__":
    main()

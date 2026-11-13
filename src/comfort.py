"""How comfortable a temperature and a humidity are.

Author: TODO your name
"""


class Comfort:
    # TODO: Write a docstring for the class: Comfort holds the dividing values that sort a
    # temperature and a humidity into levels

    def __init__(self, cold_below, hot_above, dry_below, humid_above):
        # TODO: Write a docstring: this method keeps the dividing temperatures, in degrees
        # Fahrenheit, and humidities, in percent
        # TODO: Assign each parameter to the attribute with the same name, such as the parameter
        # cold_below to self.cold_below, so the other methods can use them
        pass

    def level(self, fahrenheit):
        # TODO: Write a docstring: this method returns "cold", "warm" or "hot" for a temperature
        # in degrees Fahrenheit
        # TODO: Use if, elif and else: if fahrenheit is below self.cold_below, return "cold";
        # elif it is above self.hot_above, return "hot"; else return "warm"
        return "warm"

    def humidity_level(self, humidity):
        # TODO: Write a docstring: this method returns "dry", "comfortable" or "humid" for a
        # humidity in percent
        # TODO: Use if, elif and else: if humidity is below self.dry_below, return "dry"; elif
        # it is above self.humid_above, return "humid"; else return "comfortable"
        return "comfortable"

    def is_comfortable(self, fahrenheit, humidity):
        # TODO: Write a docstring: this method returns True when the temperature is warm and the
        # humidity is comfortable
        # TODO: Call self.level(fahrenheit) and self.humidity_level(humidity) to get the two
        # levels, then return True if the first is "warm" and the second is "comfortable", and
        # False if not
        return False

    def describe(self, fahrenheit, humidity):
        # TODO: Write a docstring: this method returns a short description of a temperature and
        # a humidity, with their levels
        # TODO: Call round(fahrenheit, 1) and round(humidity, 1) to round the two values to one
        # decimal place, and self.level and self.humidity_level to get their levels, then return
        # the four in one string, such as "72.5 F, warm, 44.0% humidity, comfortable"
        return ""

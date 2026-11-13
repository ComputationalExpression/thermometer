"""The temperature levels: cold, warm and hot.

Author: TODO your name
"""


class Levels:
    # TODO: Write a docstring for the class: Levels holds two dividing temperatures, in degrees
    # Fahrenheit, that sort a reading into a level

    def __init__(self, cold_below, hot_above):
        # TODO: Write a docstring: this method keeps the two dividing temperatures
        # TODO: Assign the parameter cold_below to the attribute self.cold_below, and the
        # parameter hot_above to the attribute self.hot_above, so the other methods can use them
        pass

    def level(self, fahrenheit):
        # TODO: Write a docstring: this method returns "cold", "warm" or "hot" for a temperature
        # in degrees Fahrenheit
        # TODO: Use if, elif and else: if fahrenheit is below self.cold_below, return "cold";
        # elif it is above self.hot_above, return "hot"; else return "warm"
        return "warm"

    def is_comfortable(self, fahrenheit):
        # TODO: Write a docstring: this method returns True when a temperature is warm, neither
        # cold nor hot
        # TODO: Call self.level(fahrenheit) to get the level of the temperature, then return True
        # if the level is "warm", and False if it is not
        return False

    def describe(self, fahrenheit):
        # TODO: Write a docstring: this method returns a short description of a temperature,
        # with its level
        # TODO: Call round(fahrenheit, 1) to round the temperature to one decimal place, and
        # self.level(fahrenheit) to get its level, then return both in one string, such as
        # "72.5 F, warm"
        return ""

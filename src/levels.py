"""The temperature levels: cold, warm and hot.

Author: TODO your name
"""


class Levels:
    """Two dividing temperatures, in degrees Fahrenheit, that sort a reading into a level."""

    def __init__(self, cold_below, hot_above):
        """Keep the two dividing temperatures."""
        # TODO: Store cold_below and hot_above
        pass

    def level(self, fahrenheit):
        """Return "cold", "warm" or "hot" for a temperature in degrees Fahrenheit."""
        # TODO: Cold below cold_below, hot above hot_above, and warm otherwise
        return "warm"

    def is_comfortable(self, fahrenheit):
        """Return True when a temperature is warm, neither cold nor hot."""
        # TODO: Use self.level(fahrenheit)
        return False

    def describe(self, fahrenheit):
        """Return a short description of a temperature, with its level."""
        # TODO: Return a string such as "72.5 F, warm", with round(fahrenheit, 1) and self.level(fahrenheit)
        return ""

"""The record of the temperatures the thermometer took.

Author: TODO your name
"""


class Log:
    """The temperatures taken in one place, and how many fell in each level."""

    def __init__(self, place):
        """Start an empty log for a place."""
        # TODO: Store place, an empty list of temperatures, and counts, a dictionary with 0 for
        # "cold", "warm" and "hot"
        pass

    def record(self, fahrenheit, level):
        """Add one temperature and count it under its level."""
        # TODO
        pass

    def highest(self):
        """Return the highest temperature recorded."""
        # TODO: Loop over the temperatures, starting from the first one
        return 0

    def lowest(self):
        """Return the lowest temperature recorded."""
        # TODO
        return 0

    def average(self):
        """Return the average of the temperatures recorded."""
        # TODO: Total them in a loop, then divide by how many there are
        return 0

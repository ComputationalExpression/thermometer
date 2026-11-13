"""The record of the readings the thermometer took.

Author: TODO your name
"""


class Log:
    # TODO: Write a docstring for the class: a Log keeps the temperatures and humidities measured
    # in one place, and how many fell in each level

    def __init__(self, place):
        # TODO: Write a docstring: this method starts an empty log for a place
        # TODO: Assign the parameter place to the attribute self.place
        # TODO: Assign an empty list to each of the attributes self.temperatures and
        # self.humidities
        # TODO: Assign to the attribute self.counts a dictionary with the keys "cold", "warm" and
        # "hot", each with the value 0
        pass

    def record(self, fahrenheit, humidity, level):
        # TODO: Write a docstring: this method adds one reading and counts it under its
        # temperature level
        # TODO: Append fahrenheit to self.temperatures, and humidity to self.humidities
        # TODO: Add 1 to self.counts[level]
        pass

    def highest(self):
        # TODO: Write a docstring: this method returns the highest temperature recorded
        # TODO: Assign the first temperature, self.temperatures[0], to a variable such as highest
        # TODO: Loop over self.temperatures, and if a temperature is above highest, assign it
        # to highest
        # TODO: Return highest
        return 0

    def lowest(self):
        # TODO: Write a docstring: this method returns the lowest temperature recorded
        # TODO: Assign the first temperature, self.temperatures[0], to a variable such as lowest
        # TODO: Loop over self.temperatures, and if a temperature is below lowest, assign it
        # to lowest
        # TODO: Return lowest
        return 0

    def average_humidity(self):
        # TODO: Write a docstring: this method returns the average of the humidities recorded
        # TODO: Assign 0 to a variable such as total, then loop over self.humidities and add
        # each humidity to total
        # TODO: Return total divided by len(self.humidities)
        return 0

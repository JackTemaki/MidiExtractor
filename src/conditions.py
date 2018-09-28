from typing import List

from src.constants import Instrument, InstrumentCategory


class Condition(object):

    def __init__(self, command : str):
        pass

    def validate(self, track_container):
        pass

class InstrumentCondition(Condition):

    def __init__(self, parameter : str):
        parameter = parameter.upper()
        self.instrument = None
        for instrument in Instrument:
            if instrument.name == parameter:
                self.instrument = instrument
                break

        if self.instrument == None:
            assert False, "Could not match instrument to any existing instrument class"

    def validate(self, track_container):
        return track_container.instrument == self.instrument

class CategoryCondition(Condition):

    def __init__(self, parameter : str):
        parameter = parameter.upper()
        self.category = None
        for category in InstrumentCategory:
            if category.name == parameter:
                self.category = category
                break

        if self.category == None:
            assert False, "Could not match category to any existing category class"

    def validate(self, track_container):
        return track_container.category == self.category

class ConditionManager(object):

    condition_dict = {
        'instrument': InstrumentCondition,
        'category': CategoryCondition,
    }

    def _create_condition(self, condition_string : str):
        split = condition_string.split("=")
        assert len(split) == 2, "Invalid condition syntax"
        command = split[0]
        parameter = split[1]
        return self.condition_dict[command](parameter)

    def __init__(self, condition_strings : List[str]):
        self.conditions = []

        for string in condition_strings:
            self.conditions.append(self._create_condition(string))

    def validate(self, track):
        for condition in self.conditions:
            val = condition.validate(track_container=track)
            if val is False:
                return False

        return True


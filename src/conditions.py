from typing import List
from src.database import TrackContainer

class Condition(object):

    def __init__(self, conditions : List[str]):
        pass

    def validate(self, track : TrackContainer):
        return True
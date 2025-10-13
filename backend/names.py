from enum import Flag, Enum

class Algorithm(Enum):
    SEVEN_MINUTES_RULE = 0
    SEEKING_HEAD_RULE = 1
    @staticmethod
    def Name(value) :
        for a in Algorithm :
            if a.value == value :
                return a.name
        return None

class Theorem(Flag) :
    SEEKING_HEAD_CONSIDER_MAX = 1 # If this flag is enabled, the theoric gap will be the maximum, otherwise the average
    @staticmethod
    def Names(values) :
        return [t.name for t in Theorem if t.value & values]
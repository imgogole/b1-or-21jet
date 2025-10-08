from enum import Flag, Enum

class Algorithm(Enum):
    SEVEN_MINUTES_RULE = 0
    def Name(value) :
        for a in Algorithm :
            if a.value == value :
                return a.name
        return None

class Theorem(Flag) :
    def Names(values) :
        return [t.name for t in Theorem if t.value & values]
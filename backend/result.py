from flask import Flask, jsonify
import time

class Result :
    @staticmethod
    def NoResult() :
        result = {
            "status" : "not_generated_yet",
        }
        return jsonify(result), 200
    def __init__(self, _b1_prob, _21jet_prob, at_time) :
        self.__b1_prob = _b1_prob           # Probability to take B1 at this time
        self.__21jet_prob = _21jet_prob     # Probability to take 21Jet at this time
        self.__at_time = at_time            # Time of results
    def Time(self) :
        return self.__at_time
    def Success(self) :
        result = {
            "status" : "success",
            "b1_prob" : self.__b1_prob,
            "21jet_prob" : self.__21jet_prob,
            "time" : self.__at_time
        }
        return jsonify(result), 200
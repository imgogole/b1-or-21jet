from flask import Flask, jsonify
import time

class Result :
    @staticmethod
    def NoResult() :
        result = {
            "status" : "failure",
            "code" : "not_generated_yet",
            "message" : "The result is not generated yet. Please try again later."
        }
        return jsonify(result), 200
    @staticmethod
    def InvalidAlgorithm() :
        result = {
            "status" : "failure",
            "code" : "invalid_algorithm",
            "message" : "The specified algorithm does not exist."
        }
        return jsonify(result), 400
    def __init__(self, _b1_prob, _21jet_prob, at_time) :
        self.__b1_prob = _b1_prob               # Probability to take B1 at this time
        self.__21jet_prob = _21jet_prob         # Probability to take 21Jet at this time
        self.__at_time = at_time                # Time of results
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
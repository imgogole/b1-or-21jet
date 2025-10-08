from flask import Flask
from markupsafe import escape
from enum import Flag

class Theorems(Flag) :
    THEOREM_1 = 1
    THEOREM_2 = 2
    THEOREM_3 = 4
    THEOREM_4 = 8
    THEOREM_5 = 16
    def get_values(flags) :
        return [t.name for t in Theorems if t.value & flags]

app = Flask(__name__)

@app.route("/")
def on_home_page() :
    return "Hello, World !", 200

@app.route("/api/<int:algortihm>/<int:theorems>")
def on_request(algorithm :int, theorems: int) :
    pass


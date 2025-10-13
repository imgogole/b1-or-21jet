from flask import Flask
from flask_cors import CORS
from markupsafe import escape
from searcher import *
import logging

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": [
    "https://b1-or-21jet.fr",
    "https://www.b1-or-21jet.fr",
    "https://b1-or-21jet-frontend.onrender.com",
    "http://localhost:5000",
    "http://localhost:3000"
]}})

Algorithms.InitConstants()

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

@app.route("/")
def on_home_page() :
    return escape("MIPS MIPS, c'est moi le MIPS"), 200

@app.route("/api/<int:algorithm>/<int:theorems>", methods=["GET"])
def on_request(algorithm :int, theorems: int) :
    must_update = Searcher.CheckForUpdate(algorithm, theorems)
    if must_update :
        Searcher.Update(algorithm, theorems)
        logging.info(f"Request algo : {Algorithm.Name(algorithm)}, theorems : {Theorem.Names(theorems)}. Cache must be updated")
    else :
        logging.info(f"Request algo : {Algorithm.Name(algorithm)}, theorems : {Theorem.Names(theorems)}. Cache up to date")

    result : Result = Searcher.GetResult(algorithm, theorems)

    if result is None :
        return Result.NoResult()

    return result.Success()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


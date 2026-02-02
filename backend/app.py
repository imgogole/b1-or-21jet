from flask import Flask, jsonify
from flask_cors import CORS
from markupsafe import escape
from searcher import *
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import os

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["2000 per day", "500 per hour"],
    storage_uri="memory://"
)

CORS(app, resources={r"/api/*": {"origins": [
    "https://b1-or-21jet.fr",
    "https://www.b1-or-21jet.fr",
    "https://b1-or-21jet-frontend.onrender.com",
    "http://localhost:5000",
    "http://localhost:8000"
]}})

Algorithms.InitConstants()

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

@app.route("/")
@limiter.exempt
def on_home_page() :
    return escape("MIPS MIPS, c'est moi le MIPS"), 200

@app.route("/api/next_buses", methods=["GET"])
@limiter.limit("20 per minute")
def next_buses() :
    b1_delta, jet_delta = Algorithms.GetNextBuses()
    return jsonify({
        "b1": b1_delta,
        "21jet": jet_delta
    }), 200

@app.route("/api/<int:algorithm>/<int:theorems>", methods=["GET"])
@limiter.limit("10 per minute")
def on_request(algorithm :int, theorems: int) :
    # Check if the algorithm exists
    if not Algorithm.Name(algorithm) :
        logging.info(f"Request algo : {Algorithm.Name(algorithm)}, theorems : {Theorem.Names(theorems)}. Algorithm does not exist")
        return Result.InvalidAlgorithm()

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

@app.errorhandler(429)
def ratelimit_handler(e):
    return Result.RateLimitExceeded(e.description)

if __name__ == "__main__":
    production = os.environ.get("RENDER") is not None or os.environ.get("FLASK_ENV") == "production"
    app.run(host="0.0.0.0", port=5000, debug=not production)
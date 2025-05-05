from flask import Flask
from logger import get_logger

log = get_logger("health")
app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return "OK", 200

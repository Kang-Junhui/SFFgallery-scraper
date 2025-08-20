# app.py
from flask import Flask, jsonify, request
import json
import scraper

app = Flask(__name__)

@app.route("/")
def index():
    mode = request.args.get("mode", "normal") # mode = normal or hotdeal

    try:
        with open(f"data/data_{mode}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "data not found"}), 404

    return jsonify(data)

@app.route("/update")
def update():
    mode = request.args.get("mode", "normal")
    scraper.scrape(mode)
    return jsonify({"status": f"{mode} updated"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

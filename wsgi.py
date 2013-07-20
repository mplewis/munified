import munified
from flask import Flask, Request, Response, jsonify

application = app = Flask(__name__)

@app.route('/')
def muni_data():
    predictions = munified.fetch_predictions(munified.STOPS)
    stops_with_predictions = munified.merge_predictions(munified.STOPS, predictions)
    return jsonify({'stops': stops_with_predictions})

if __name__ == '__main__':
    app.run(debug=True)
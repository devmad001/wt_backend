from flask import Flask, render_template, jsonify
from flask_cors import CORS  # Import the CORS class

app = Flask(__name__)
CORS(app)  # Enable CORS on your Flask app


@app.route("/get_pois")
def get_pois():
    poi_data = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-123.115898, 49.295868] # Example coordinates
                },
                'properties': {
                    'title': 'POI 1',
                    'description': 'Description for POI 1'
                }
            },
            #... Add more POIs as necessary
        ]
    }
    return jsonify(poi_data)

@app.route("/")
def index():
    return render_template("index_here_map_async.html")

if __name__ == "__main__":
    app.run(debug=True)
    

"""
CHANGE MAP STYLES REQUIRES CREATING MAP

watchtower_map_here_hybrid
https://us-east-1.console.aws.amazon.com/location/maps/home?region=us-east-1#/describe/watchtower_map_here_hybrid

here_explore_neutral

"""

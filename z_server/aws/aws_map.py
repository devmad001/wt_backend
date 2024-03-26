

#https://us-east-1.console.aws.amazon.com/location/maps/home?region=us-east-1#/describe/watchtower_map_here_hybrid/embed

"""
<html>
  <head>
    <link href="https://unpkg.com/maplibre-gl@3.x/dist/maplibre-gl.css" rel="stylesheet" />
    <style>
      body { margin: 0; }
      #map { height: 100vh; }
    </style>
  </head>
  <body>
    <div id="map" />
    <script src="https://unpkg.com/maplibre-gl@3.x/dist/maplibre-gl.js"></script>
    <script>
      const apiKey = "v1.public.eyJqdGkiOiJjZGVmNWRmMi0yNzRiLTRhOWItYmQ1Zi02ZWVkMDBiMDYxMjkifTfg432tsDiP2LK67yuhA1SpI9VKmtpaf3eK1R2HS8cipDAsdQq0RM_lFbdc8m6YYoIfbY7R9Mk5fiM7MhqdIF9Cs_6QIlacVYw6tLQVzyLbWQUQfEHCM8cN8_n7FmA_p7GdWQt4QhIc5e3osa0pFLGUmmrMrDlwOOwsZjHBN2t2SpYKfbWibGcObt9Mb4D-LxXdkfbNlYj-ifjxcHzH_r-b9TCNVFvCn8x0wRth-xmqCIS0CISr_nFwp87-6vPs4aIoXNUz6domUp4xTK_j6HvZixoMU8ADAOvPoucma2bkJCkr-4a7jF0q20acGrdseO6GaYFlp_1_YfkaY-UguDk.ZWU0ZWIzMTktMWRhNi00Mzg0LTllMzYtNzlmMDU3MjRmYTkx";
      const mapName = "watchtower_map_here_hybrid";
      const region = "us-east-1";

      const map = new maplibregl.Map({
        container: "map",
        style: `https://maps.geo.${region}.amazonaws.com/maps/v0/maps/${mapName}/style-descriptor?key=${apiKey}`,
        center: [-123.115898, 49.295868],
        zoom: 11,
      });
      map.addControl(new maplibregl.NavigationControl(), "top-left");
    </script>
  </body>
</html>

"""
"""
Save the file above as index.html, making sure to provide the apiKey as necessary.
From the same directory run:

npx serve
Open your browser to http://localhost:5000/ 

"""

"""
MY KEY:
v1.public.eyJqdGkiOiJjZGVmNWRmMi0yNzRiLTRhOWItYmQ1Zi02ZWVkMDBiMDYxMjkifTfg432tsDiP2LK67yuhA1SpI9VKmtpaf3eK1R2HS8cipDAsdQq0RM_lFbdc8m6YYoIfbY7R9Mk5fiM7MhqdIF9Cs_6QIlacVYw6tLQVzyLbWQUQfEHCM8cN8_n7FmA_p7GdWQt4QhIc5e3osa0pFLGUmmrMrDlwOOwsZjHBN2t2SpYKfbWibGcObt9Mb4D-LxXdkfbNlYj-ifjxcHzH_r-b9TCNVFvCn8x0wRth-xmqCIS0CISr_nFwp87-6vPs4aIoXNUz6domUp4xTK_j6HvZixoMU8ADAOvPoucma2bkJCkr-4a7jF0q20acGrdseO6GaYFlp_1_YfkaY-UguDk.ZWU0ZWIzMTktMWRhNi00Mzg0LTllMzYtNzlmMDU3MjRmYTkx

arn:aws:geo:us-east-1:487320324532:place-index/explore.place.Esri
Actions
This key authorizes the following actions.

Service
Actions
Maps	N/A
Places	GetPlace, SearchPlaceIndexForPosition, SearchPlaceIndexForSuggestions, SearchPlaceIndexForText
Routes	N/A


CREATE MAP:
"""

"""
CREATE MAP
watchtower_map_here_hybrid
key:  per above
esri_places_key

Name
watchtower_map_here_hybrid
Map style
HERE Hybrid
Description
 
ARN
 arn:aws:geo:us-east-1:487320324532:map/watchtower_map_here_hybrid

 

"""
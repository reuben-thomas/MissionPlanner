import dash_leaflet as dl
import pandas as pd
import numpy as np

# waypoint cluster
waypoint_icon = {
    "iconUrl": "assets/icons/yellow_dot.png",
    "shadowUrl": "assets/icons/move.png",
    "iconSize": [4, 4],  # size of the icon
    "shadowSize": [0, 0],  # size of the shadow
    "iconAnchor": [2, 2],  # point of the icon which will correspond to marker's location
    "shadowAnchor": [0, 0],  # the same for the shadow
    "popupAnchor": [-5, -5]  # point from which the popup should open relative to the iconAnchor
}

# waypoint cluster
edited_waypoint_icon = {
    "iconUrl": "assets/icons/red_dot.png",
    "shadowUrl": "assets/icons/move.png",
    "iconSize": [4, 4],  # size of the icon
    "shadowSize": [0, 0],  # size of the shadow
    "iconAnchor": [2, 2],  # point of the icon which will correspond to marker's location
    "shadowAnchor": [0, 0],  # the same for the shadow
    "popupAnchor": [-5, -5]  # point from which the popup should open relative to the iconAnchor
}

# waypoint cluster
optimized_waypoint_icon = {
    "iconUrl": "assets/icons/purple_dot.png",
    "shadowUrl": "assets/icons/move.png",
    "iconSize": [4, 4],  # size of the icon
    "shadowSize": [0, 0],  # size of the shadow
    "iconAnchor": [2, 2],  # point of the icon which will correspond to marker's location
    "shadowAnchor": [0, 0],  # the same for the shadow
    "popupAnchor": [-5, -5]  # point from which the popup should open relative to the iconAnchor
}
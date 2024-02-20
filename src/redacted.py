import plotly.express as px
import dash_html_components as html
import dash_core_components as dcc
from dash import Dash
from dash.dependencies import Input, Output
import dash_leaflet as dl

import pandas as pd
import numpy as np
import utm
import json
import math

from road_feature_layer import curb
from waypoint_layer import waypoint_icon, edited_waypoint_icon

#initialize app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(prevent_initial_callbacks=True, external_stylesheets=external_stylesheets)

#-------------------------------------------------------------------------
# WAYPOINT / PATH EDITOR
#
# This section defines the functions for loading a master set of waypoints
# that are editable by dragging, enables adding new waypoint functionality
# all while keeping the master list up to date
#-------------------------------------------------------------------------

# for each path, create a marker cluster group of waypoints
waypoint_sets = []
waypoint_markers = []
path_id_dict = {"0f":"0.0", "1f":"1.0", "1r":"1.1", "2f":"2.0", "2r":"2.1", "3f":"3.0", 
            "3r":"3.1", "4f":"4.0", "5f":"5.0", "5r":"5.1", "6f":"6.0", "6r":"6.1", "7f":"7.0"}

waypoint_position_input_list = []


# for each path waypoints file
for path_id in path_id_dict:

    dir_path = "waypoints/" + path_id_dict[path_id] + ".csv"
    df = pd.read_csv(dir_path, sep=';')
    ax = df['x'].values.tolist()
    ay = df['y'].values.tolist()
    path_positions = [[ay[i], ax[i]] for i in range(len(ax))]
    waypoint_sets.append(path_positions)

    # for each point in waypoints file
    for wp_id in range(len(path_positions)):
        waypoint_html_id = "path_" + path_id + "_wp_" + str(wp_id)
        print(waypoint_html_id)
        waypoint_markers.append(dl.Marker(icon=waypoint_icon, draggable=True, position=path_positions[wp_id], id=waypoint_html_id))
        
        waypoint_position_input_list.append(Input(waypoint_html_id, "position"))

        @app.callback(Output(waypoint_html_id, "icon"), Input(waypoint_html_id, "position"))
        def print_position(position):
            print("waypoint ", waypoint_html_id, " was moved to ", position)
            return edited_waypoint_icon


# def update_waypoints(waypoint_html_id):

    







#-------------------------------------------------------------------------
# LEAFLET MAP TILING
#
# The order of placing each of the leaflet map components with layers control
#-------------------------------------------------------------------------

drag_marker = dl.Marker(id="marker", draggable=True, position=(56,10))

# Map layer
image_url = "assets/maps/ngee_ann.png"
map_origin = np.array([5, 18.75])
map_size = np.array([0.1*7760, 0.1*8548])
image_bounds = [-0.5*map_size + map_origin, 0.5*map_size + map_origin]
map = dl.ImageOverlay(opacity=0.5, url=image_url, bounds=image_bounds)

image_url = "assets/icons/black.png"
shadow = dl.ImageOverlay(opacity=0.5, url=image_url, bounds=image_bounds)

# Map contrainer
map_div = html.Div(dl.Map([
    dl.LayersControl(
        [dl.BaseLayer(map, name="Occupancy Map", checked=True)] +
        [dl.Overlay(dl.LayerGroup(shadow), name="Shadow", checked=True),
         dl.Overlay(dl.LayerGroup(drag_marker), name="Drag Marker Test", checked=True),
         dl.Overlay(dl.LayerGroup(curb), name="Curb", checked=True),
         dl.Overlay(dl.LayerGroup(waypoint_markers), name="Waypoints", checked=True),
         dl.Overlay(dl.LayerGroup(id="selection"), name="ClickedPoint")]
    )
], id="map", maxZoom=7, maxBounds=image_bounds, maxBoundsViscosity=1.0, bounds=image_bounds, crs="Simple"), style={'width': '100%', 'height': '90vh', 'margin': "auto", "display": "block"})


#-------------------------------------------------------------------------
# APP LAYOUT AND CONFIG
#-------------------------------------------------------------------------

# Output container
output_div = html.Div(id="output")
app.layout = html.Div( children=[map_div, output_div] )

# # callback for drag motion
# @app.callback(Output("output", "children"), [Input("id_1", "position")])
# def print_position(position):
#     print("moved first waypoint with pose ", position)
#     return json.dumps(position)

@app.callback(Output("selection", "children"), [Input("map", "click_lat_lng")])
def map_click(click_lat_lng):

    # print("clicks ", clicks)
    # print("select position ", click_lat_lng)
    return [dl.CircleMarker(center=click_lat_lng, radius=5, children=dl.Tooltip("({:.3f}, {:.3f})".format(*click_lat_lng)))]


def find_closest_path():
    ...

if __name__ == '__main__':
    clicks = []
    app.run_server(debug=False)
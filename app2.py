import plotly.express as px
import dash_html_components as html
import dash_core_components as dcc
from dash import Dash
from dash.dependencies import Input, Output
import dash_leaflet as dl
from dash import callback_context
import dash_bootstrap_components as dbc

import pandas as pd
import numpy as np
import utm
import json
import math

from cubic_spline_planner import calc_spline_course
from analysis_functions import calc_yaw_curvature

from road_feature_layer import curb
from waypoint_layer import waypoint_icon, edited_waypoint_icon, optimized_waypoint_icon

#initialize app 'https://codepen.io/chriddyp/pen/bWLwgP.css'
external_stylesheets = [dbc.themes.LUX]
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
waypoint_markers, opt_waypoint_markers = [], []
path_lines = []
path_id_dict = {"0f":"0.0", "1f":"1.0", "1r":"1.1", "2f":"2.0", "2r":"2.1", "3f":"3.0", 
            "3r":"3.1", "4f":"4.0", "5f":"5.0", "5r":"5.1", "6f":"6.0", "6r":"6.1", "7f":"7.0",
            "0f_opt":"Dynamic Boundary/0.0", 
            "1f_opt":"Dynamic Boundary/1.0", "1r_opt":"Dynamic Boundary/1.1",
            "2f_opt":"Dynamic Boundary/2.0", "2r_opt":"Dynamic Boundary/2.1",
            "5f_opt":"Dynamic Boundary/5.0"
            }

path_dict = path_id_dict.copy()
waypoint_position_input_list = []

for path_id in path_id_dict:

    dir_path = "waypoints/" + path_id_dict[path_id] + ".csv"
    df = pd.read_csv(dir_path, sep=';')
    laneInd =  df['laneInd'].values.tolist()
    pointInd =  df['pointInd'].values.tolist()
    ax = df['x'].values.tolist()
    ay = df['y'].values.tolist()
    path_positions = [[ay[i], ax[i]] for i in range(len(ax))]
    waypoint_sets.append(path_positions)

    path = [laneInd, pointInd, ax, ay]
    path_dict[path_id] = path

    # for each point in waypoints file
    for wp_id in range(len(path_positions)):

        waypoint_html_id = path_id + "_ln_" + str(laneInd[wp_id]) + "_pt_" + str(pointInd[wp_id])

        if path_id in ['0f_opt', '1f_opt', '1r_opt', '2f_opt', '2r_opt', '5f_opt']:
            opt_waypoint_markers.append(dl.Marker(icon=optimized_waypoint_icon, draggable=True, position=path_positions[wp_id], children=dl.Tooltip(waypoint_html_id), id=waypoint_html_id))
        else:
            waypoint_markers.append(dl.Marker(icon=waypoint_icon, draggable=True, position=path_positions[wp_id], children=dl.Tooltip(waypoint_html_id), id=waypoint_html_id))

        @app.callback(Output(waypoint_html_id, "icon"), Input(waypoint_html_id, "position"))
        def waypoint_moved(position):

            html_id = callback_context.triggered[0]["prop_id"].split(".")[0]
            info = html_id.split('_')

            path_name = info[0]
            point_Ind = int(info[-1])
            path_Ind = path_dict[path_name][1]
            id = path_Ind.index(point_Ind)

            path_dict[path_name][2][id] = position[1]
            path_dict[path_name][3][id] = position[0]

            return edited_waypoint_icon


@app.callback(Output("path", "children"), Input("update_btn", "n_clicks"))
def update_path_lines(n_clicks):
    return create_path_lines()

def create_path_lines():

    path_lines = []
    opt_path_lines = []
    for path_id in path_dict:

        laneInd = path_dict[path_id][0]
        pathInd = path_dict[path_id][1]
        ax = path_dict[path_id][2]
        ay = path_dict[path_id][3]
        # path_positions = [[ay[i], ax[i]] for i in range(len(ax))]

        startpoint = 0
        endpoint = 0

        for i in range(len(pathInd)):
        
            if i == len(pathInd)-1:
                ix, iy = ax[startpoint:], ay[startpoint:]
                n_path_positions = [[iy[n], ix[n]] for n in range(len(ix))]

                if path_id in ['0f_opt', '1f_opt', '1r_opt', '2f_opt', '2r_opt', '5f_opt']:
                    n_path_line = dl.Polyline(color="#e6097b50", weight=2, positions=n_path_positions)
                    opt_path_lines.append(n_path_line)
                else:
                    n_path_line = dl.Polyline(color="#e6a00950", weight=2, positions=n_path_positions)
                    path_lines.append(n_path_line)

            elif pathInd[i+1] == pathInd[i] + 1:
                endpoint = i+1

            else:
                ix, iy = ax[startpoint:endpoint+1], ay[startpoint:endpoint+1]
                # ix, iy, _, _, _ = calc_spline_course(ix, iy, ds=0.1)
                n_path_positions = [[iy[n], ix[n]] for n in range(len(ix))]

                if path_id in ['0f_opt', '1f_opt', '1r_opt', '2f_opt', '2r_opt', '5f_opt']:
                    n_path_line = dl.Polyline(color="#e6097b50", weight=2, positions=n_path_positions)
                    opt_path_lines.append(n_path_line)
                else:
                    n_path_line = dl.Polyline(color="#e6a00950", weight=2, positions=n_path_positions)
                    path_lines.append(n_path_line)
                
                startpoint = i+1

    return path_lines, opt_path_lines
        
path_lines, opt_path_lines = create_path_lines()

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
         dl.Overlay(dl.LayerGroup(drag_marker), name="Drag Marker Test", checked=False),
         dl.Overlay(dl.LayerGroup(id='path', children=path_lines), name="Paths", checked=True),
         dl.Overlay(dl.LayerGroup(id='opt_path', children=opt_path_lines), name="Optimized Paths", checked=True),
         dl.Overlay(dl.LayerGroup(curb), name="Curb", checked=True),
         dl.Overlay(dl.LayerGroup(id='waypoints', children=waypoint_markers), name="Waypoints", checked=True),
         dl.Overlay(dl.LayerGroup(id='opt_waypoints', children=opt_waypoint_markers), name="Optimized Waypoints", checked=True),
         dl.Overlay(dl.LayerGroup(id="selection"), name="ClickedPoint")]
    )
], id="map", maxZoom=6, maxBounds=image_bounds, maxBoundsViscosity=1.0, bounds=image_bounds, crs="Simple"), style={'width': '100%', 'height': '100vh', 'margin': "none", "display": "block"})

#-------------------------------------------------------------------------
# APP LAYOUT AND CONFIG
#-------------------------------------------------------------------------

# TITLE TAB
title = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("GITHUB", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="MOOVITA",
    brand_href="#",
    color="primary",
    dark=True,
    style={"height":'3vh'}
)

# MAIN TAB CONTENT

curve_constraint_slider = dcc.Slider(
    min=-1,
    max=1,
    step=0.001,
    value=[-1, 1],
)  

steering_constraint_slider = dcc.Slider(
    min=-1,
    max=1,
    step=0.001,
    value=[-1, 1]
)  

boundary_constraint_slider = dcc.Slider(
    min=-1,
    max=1,
    step=0.001,
    value=[-1, 1]
)  


dir_path = 'waypoints/0.0.csv'
df = pd.read_csv(dir_path, sep=';')
ax = df['x'].values.tolist()
ay = df['y'].values.tolist()
ax, ay = ax[0:115], ay[0:115]
_, _, _, k, _ = calc_spline_course(ax, ay)
y_default = np.array(k)


dir_path = 'waypoints/1.0.csv'
df = pd.read_csv(dir_path, sep=';')
ax = df['x'].values.tolist()
ay = df['y'].values.tolist()
ax, ay = ax[0:115], ay[0:115]
_, _, _, k, _ = calc_spline_course(ax, ay)
y_opt = np.array(k)

x_default = list(range(0, len(y_default)))
curvature_graph = dcc.Graph(
    figure=dict(
        data=[
            dict(
                x=x_default,
                y=y_default,
                name='Default',
                marker=dict(
                    color='rgb(181, 44, 212)'
                )
            ),
            dict(
                x=x_default,
                y=y_opt,
                name='Optimized',
                marker=dict(
                    color='rgb(277, 208, 0)'
                )
            )
        ],
        layout=dict(
            showlegend=True,
            legend=dict(
                x=0,
                y=1.0
            ),
            margin=dict(l=10, r=0, t=10, b=20)
        )
    ),
    style={'height': 300},
    id='my-graph'
)  




tab1_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("CURVATURE CONSTRAINT", className="curve_constraint_text", style={"font-size":"0.2rem;"}),
            curve_constraint_slider,
            html.P("STEERING CONSTRAINT", className="steering_constraint_text", style={"font-size":"0.2rem;"}),
            steering_constraint_slider,
            html.P("BOUNDARY CONSTRAINT", className="boundary_constraint_text", style={"font-size":"0.2rem;"}),
            boundary_constraint_slider,
            html.P("CURVATURE PROFILE", className="boundary_constraint_text", style={"font-size":"0.2rem;"}),
            curvature_graph

        ]
    ),
    className="mt-3",
)

# WAYPOINT DATA VIEWER CONTENT
output_div = html.Div(id="output")
update_button = dbc.Button('Update Path', size="sm", className="mr-1", id='update_btn', color='success', outline=True, n_clicks=0)
reset_button = dbc.Button('Reset Path', size="sm", className="mr-1", id='reset_btn', color='secondary', outline=True, n_clicks=0)
add_button = dbc.Button('Add Point', size="sm", className="mr-1", id='add_btn',  color='secondary', outline=True, n_clicks=0)
delete_button = dbc.Button('Remove Point', size="sm", className="mr-1", id='secondary', color='danger', outline=True, n_clicks=0)
path_dropdown_items = [dbc.DropdownMenuItem("{}".format(key)) for key in path_dict] 
path_select_dropdown = dbc.DropdownMenu(label="Select Path", children=path_dropdown_items, direction="down", bs_size="sm", style={"display":"inline"})
dir_path = "waypoints/2.0.csv"
df = pd.read_csv(dir_path, sep=';')
points_table = dbc.Table.from_dataframe(df, size="sm", striped=True, responsive=True, bordered=True, hover=True, style={"margin-top":"1rem"})
tab2_content = dbc.Card(
    dbc.CardBody(
        [
            update_button,
            reset_button,
            add_button,
            delete_button,
            path_select_dropdown,
            points_table,
        ], style={"width":"37.2rem", "height":"85vh","overflow":"scroll"}
    ),
    className="mt-3",
)



# OPTIMIZATION VIEWER CONTENT
tab3_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("This is tab 2!", className="card-text"),
            dbc.Button("Don't click here", color="danger"),
        ]
    ),
    className="mt-3",
)


tabs = dbc.Tabs(
    [
        dbc.Tab(tab1_content, label="ANALYSIS"),
        dbc.Tab(tab2_content, label="DATA"),
        dbc.Tab(tab3_content, label="OPTIMIZATION")
    ]
)


# OUTPUT COLUMN
output_col = html.Div(
    [
        title,
        tabs
    ],
    style={'margin':'none'}
)



app.layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(output_col, width=5, style={"padding-right":"0rem", "height":"100vh"}),
                dbc.Col(map_div, width=7, style={"padding-left":"0rem"})
            ]
        ),
    ],
    style={'margin':'none'}
)

@app.callback(Output("selection", "children"), [Input("map", "click_lat_lng")])
def map_click(click_lat_lng):

    # print("clicks ", clicks)
    # print("select position ", click_lat_lng)
    return [dl.CircleMarker(center=click_lat_lng, radius=5, children=dl.Tooltip("({:.3f}, {:.3f})".format(*click_lat_lng)))]



if __name__ == '__main__':
    app.run_server(debug=False)
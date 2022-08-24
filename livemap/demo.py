import plotly.express as px
import dash_html_components as html
import dash_core_components as dcc
from dash import Dash
from dash.dependencies import Input, Output
import dash_leaflet as dl

import pandas as pd
import numpy as np
from cubic_spline_planner import calc_spline_course
import utm
import math


# Input waypoints
dir_path = 'waypoints/ngeeann2.0.csv'
df = pd.read_csv(dir_path)
ax = df['x'].values.tolist()[0:115]
ay = df['y'].values.tolist()[0:115]

# Np coordinates in utm frame 48N
ngeeann_utm = np.array([363625, 147305])

""" converts path from cartesian coordinates to latitude longitude with
reference home position """
def path_to_latlon(x, y, home_utm):

    positions = []
    y = np.multiply(y, -1)
    x = np.multiply(x, -1)

    eastings = np.add(x, home_utm[0])
    northings = np.add(y, home_utm[1])

    lat, lon = utm.to_latlon(eastings, northings, zone_number=48, northern=True)
    
    for i in range(len(lat)):
        point = [lat[i], lon[i]]
        positions.append(point)

    return positions

""" Calculates bisector yaw angles """
def calc_bisector_yaw_curvature(x, y):

    dx, dy = calc_d(x,y)
    ddx, ddy = calc_d(dx, dy)
    yaw, k = [], []

    # curvature calculation
    for i in range(0, len(x)):
        k.append( (ddy[i] * dx[i] - ddx[i] * dy[i]) / ((dx[i]**2 + dy[i]**2)**(3/2)) )

    # firspoint yaw unchanged
    yaw.append(math.atan2(dy[0], dx[0]))

    for i in range(1, len(x)-1):
        #first derivative unit vectors at each point
        d0_dist = math.hypot(dx[i], dy[i])
        d0_hat_x = dx[i] / d0_dist
        d0_hat_y = dy[i] / d0_dist
        d1_dist = math.hypot(dx[i-1], dy[i-1])            
        d1_hat_x = dx[i-1] / d1_dist
        d1_hat_y = dy[i-1] / d1_dist
        yaw.append( math.atan2((d0_hat_y + d1_hat_y), (d0_hat_x + d1_hat_x)) )

    #lastpoint yaw unchanged
    yaw.append(math.atan2(dy[-1], dx[-1]))
    return yaw, k

""" Calculates the first derivatives of the input arrays """
def calc_d(x, y):

    dx, dy = [], []

    for i in range(0, len(x)-1):
        dx.append(x[i+1] - x[i])
    for i in range(0, len(y)-1):
        dy.append(y[i+1] - y[i])
    
    dx.append(dx[-1])
    dy.append(dy[-1])
    return dx, dy

""" Determines the position of boundary lines for visualization """
def init_boundary(x, y, bound=1.0):

    yaw, _ = calc_bisector_yaw_curvature(x, y)

    # initialize headings
    rax, ray, lax, lay = [], [], [], []

    for n in range(0, len(yaw)):
        lax.append(x[n] - bound*math.sin(yaw[n]))
        lay.append(y[n] + bound*math.cos(yaw[n]))
        rax.append(x[n] + bound*math.sin(yaw[n]))
        ray.append(y[n] - bound*math.cos(yaw[n]))
    
    return lax, lay, rax, ray

""" Rotates a point by an angle about the origin """
def rotate(origin, point, angle):

    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)

    return qx, qy

wp_x_utm, wp_y_utm = [], []

for i in range(len(ax)):
    x, y = rotate([0,0], [ax[i], ay[i]], -0.062)
    wp_x_utm.append(x)
    wp_y_utm.append(y)

# Cool, dark tiles by Stadia Maps.
url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'
attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '

# Path
path_x, path_y, _, _, _ = calc_spline_course(wp_x_utm, wp_y_utm)
path_positions = path_to_latlon(path_x, path_y, ngeeann_utm)
path = dl.Polyline(color="#ff7800", weight=1, positions=path_positions)

# Road Boundary
lax, lay, rax, ray = init_boundary(path_x, path_y, bound=1.5)
left_road_positions = path_to_latlon(lax, lay, ngeeann_utm)
right_road_positions = path_to_latlon(rax, ray, ngeeann_utm)
left_road = dl.Polyline(color="#adadad", weight=1, positions=right_road_positions)
right_road = dl.Polyline(color="#adadad", weight=1, positions=left_road_positions)

# Waypoints
waypoint_positions = path_to_latlon(wp_x_utm, wp_y_utm, ngeeann_utm)
patterns = [dict(offset='5%', repeat='10%', marker={})]
polyline = dl.Polyline(positions=waypoint_positions, color='#ffffff00')
waypoints = dl.PolylineDecorator(children=polyline, patterns=patterns)

markdown_text = '''
# Offline Path Planning Optimization
This is a concept application demonstrating offline path planning optimization for
mission planning. Implemented within Dash.
'''

# Create app.
app = Dash()
app.layout = html.Div(
    dl.Map([dl.TileLayer(url=url, maxZoom=25, attribution=attribution), path, left_road, right_road, waypoints], zoom=18, center=(1.331142, 103.774454)),
    style={'width': '100%', 'height': '70vh', 'margin': "auto", "display": "block"})


if __name__ == '__main__':
    app.run_server()
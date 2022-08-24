import dash_leaflet as dl
import pandas as pd
import numpy as np

curb_color = "#e6e6e6"

"""
CURB LAYER
"""
dir_path = "waypoints/curb.csv"
df = pd.read_csv(dir_path, sep=';')
shape_id = df['shapeid'].values.tolist()
shape_list = np.unique(shape_id)
x = df['x'].values.tolist()
y = df['y'].values.tolist()
curb = []

# for all individual shapes
for shape in shape_list:
    
    id = np.argwhere(shape_id == shape)
    positions = [[y[int(n)], x[int(n)]] for n in id]
    line = dl.Polyline(color=curb_color, weight=1, positions=positions)
    curb.append(line)


"""
SAFE ZONE LAYER
"""
dir_path = "waypoints/safe_zone_junction.csv"
df = pd.read_csv(dir_path, sep=';')
shape_id = df['id'].values.tolist()
shape_list = np.unique(shape_id)
x = df['x'].values.tolist()
y = df['y'].values.tolist()
safe_zone = []

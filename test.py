from dash import Dash
from dash import callback_context
import dash_html_components as html
import dash_leaflet as dl
from dash.dependencies import Input, Output

positions = [(11, 11), (33, 33), (55, 55)]
markers = [dl.Marker(dl.Tooltip("test"), position=pos, id="marker{}".format(i)) for i, pos in enumerate(positions)]
cluster = dl.MarkerClusterGroup(id="markers", children=markers, options={"polygonOptions": {"color": "red"}})

app = Dash(prevent_initial_callbacks=True)
app.layout = html.Div([
    html.Div(dl.Map([dl.TileLayer(), cluster], center=(33, 33), zoom=3, id="map",
                    style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"})),
    html.Div(id='clickdata')
])


@app.callback(Output("clickdata", "children"),
              [Input(marker.id, "n_clicks") for marker in markers])
def marker_click(*args):
    marker_id = callback_context.triggered[0]["prop_id"].split(".")[0]
    return "Hello from {}".format(marker_id)


if __name__ == '__main__':
    app.run_server()
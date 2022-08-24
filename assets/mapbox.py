import dash
import dash_html_components as html
import dash_leaflet as dl

from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, ALL

app = dash.Dash(prevent_initial_callbacks=True)
app.layout = html.Div([
    dl.Map([dl.TileLayer(), dl.LayerGroup(id="container", children=[])], id="map", center=(56, 10), zoom=10,
           style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}),
    html.Div(id="log")
])


@app.callback(Output("container", "children"), [Input("map", "click_lat_lng")], [State("container", "children")])
def add_marker(click_lat_lng, children):
    children.append(dl.Marker(position=click_lat_lng, n_clicks=0, id=dict(tag="marker", index=len(children))))
    return children


@app.callback(Output("log", "children"), [Input(dict(tag="marker", index=ALL), "n_clicks")])
def marker_click(n_clicks):
    triggered = dash.callback_context.triggered
    # Don't react of marker add event.
    if len(triggered) > 1 or (len(triggered) == 1 and triggered[0]['value'] == 0):
        raise PreventUpdate
    # Write to log div which marker was clicked.
    return f"You clicker marker with id {triggered[0]['prop_id'].split('.')[0]}", n_clicks


if __name__ == '__main__':
    app.run_server()
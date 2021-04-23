# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

engine = create_engine('postgres://localhost/bikecount', echo=False)
query = "SELECT * FROM count_2019;"
counts = pd.read_sql(query, engine)

engine = create_engine('postgres://localhost/bikecount', echo=False)
query = "SELECT * FROM standortdaten;"
stations = pd.read_sql(query, engine)

yearly_2020 = counts.groupby(counts.Date.dt.year, as_index=False).sum().transpose()
yearly_2020.columns = ['sum_2020']
yearly_2020 = yearly_2020.join(stations.set_index('Zählstelle'))
yearly_2020.reset_index(inplace=True)

fig = px.scatter_mapbox(yearly_2020, lat="Breitengrad", lon="Längengrad", hover_name='level_0',
                            hover_data={
                                'level_0' : False,
                                'Breitengrad': False,
                                'Längengrad': False,
                                'sum_2020' : True,
                                'Beschreibung - Fahrtrichtung': True,
                                'Installationsdatum': True},
                            color='level_0', size='sum_2020', size_max=100, zoom=50,
                            mapbox_style="open-street-map",
                            height=800)

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
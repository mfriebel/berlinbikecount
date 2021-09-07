# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import inspect

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
HOST = 'localhost'
DB = 'bikecount'

db_engine = create_engine(f'postgres://{HOST}/{DB}', echo=False)

def get_db_tables(engine):
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    return table_names

def get_sql_table(engine, table):
    query = f"SELECT * FROM {table};"
    table = pd.read_sql(query, engine)
    return table

tables = get_db_tables(db_engine)
tables.sort()

yearly_dev = pd.DataFrame(columns=get_sql_table(db_engine, 'count_2020').columns)
for table in tables[:-1]:
    df = get_sql_table(db_engine, table)
    agg_df = df.groupby(df.date.dt.year, as_index=False).sum()
    agg_df['date'] = df.date.dt.year[1]
    yearly_dev = yearly_dev.append(agg_df)

yearly_dev.set_index('date', inplace=True)
yearly_dev = yearly_dev.transpose()

development_fig = go.Figure()

for time_span in range(2015, 2021):
    development_fig.add_trace(go.Bar(x=yearly_dev.index, y=yearly_dev[time_span], name='Yearly Bike counts'))

sliders = [
    {'steps': [
        {'method': 'update', 'label': '2015', 
        'args' : [{'visible': [True,  False, False, False,  False, False]}]},
        {'method': 'update', 'label': '2016', 
        'args' : [{'visible': [False,  True, False, False,  False, False]}]},
        {'method': 'update', 'label': '2017', 
        'args' : [{'visible': [False,  False, True, False,  False, False]}]},
        {'method': 'update', 'label': '2018', 
        'args' : [{'visible': [False,  False, False, True,  False, False]}]},
        {'method': 'update', 'label': '2019', 
        'args' : [{'visible': [False,  False, False, False,  True, False]}]},
        {'method': 'update', 'label': '2020', 
        'args' : [{'visible': [False, False,  False, False, False, True]}]}
        ]}
]

# Hide traces for other time intervals than 2019
development_fig.data[1].visible=False
development_fig.data[2].visible=False
development_fig.data[3].visible=False
development_fig.data[4].visible=False
development_fig.data[5].visible=False


# Set layout with sliders included
development_fig.update_layout({
    'showlegend':False,
    'title': {'text': "Yearly bike counts per station 2015-2021"},
    'xaxis': {'title':'Station'},
    'yaxis': {'title':'Counts', 'range':[0, 2000000]},
    'sliders' : sliders
    })
    
app.layout = html.Div(children=[
    html.H1(children='Berlin Bike Count'),

    html.Div(children='''
        Automatische Fahrradzählung Berlin.
    '''),

    html.Div([dcc.Dropdown(
        id='table_selection',
        options=[
            {'label': y, 'value': y} for y in tables],
        value='count_2020')], style = {'width' : '30%', 'padding' : 10}),

    dcc.Graph(
        id='station_map'),

    dcc.Graph(
        id='development',
        figure = development_fig
    )
])


@app.callback(
    dash.dependencies.Output('station_map', 'figure'),
   [dash.dependencies.Input('table_selection', 'value')])

def update_fig(value, engine=db_engine):
    counts = get_sql_table(engine, value)
    stations = get_sql_table(engine, 'standortdaten')
    yearly = counts.groupby(counts.date.dt.year, as_index=False).sum().transpose()
    yearly.columns = ['Radfahrer_pro_Jahr']
    yearly = yearly.join(stations.set_index('zählstelle'))
    yearly.index.name = 'zählstelle'
    yearly.reset_index(inplace=True)
    yearly['zählstelle_no'] = yearly['zählstelle'].apply(lambda x: x[0:2])
    

    figure = px.scatter_mapbox(yearly, lat="breitengrad", lon="längengrad", hover_name='zählstelle',
                            hover_data={
                                'zählstelle' : False,
                                'zählstelle_no': False,
                                'breitengrad': False,
                                'längengrad': False,
                                'Radfahrer_pro_Jahr' : True,
                                'beschreibung - fahrtrichtung': True,
                                'installationsdatum': False},
                            color='zählstelle_no', size='Radfahrer_pro_Jahr', size_max=30, zoom=10,
                            mapbox_style="open-street-map",
                            height=700)
    
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
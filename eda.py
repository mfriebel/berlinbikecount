#%%
import openpyxl
import pandas as pd
import seaborn as sns
from sql_data_import import count_sheet_to_df, station_sheet_to_df, clean_data
import plotly.express as px
from sqlalchemy import create_engine
from sqlalchemy import inspect
#%%
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
#%%
count_2020 = get_sql_table(db_engine, 'count_2020')
# %%
count_2020['year'] = count_2020.Date.dt.year
count_2020['month'] = count_2020.Date.dt.month
count_2020['season'] = count_2020.Date.dt.quarter
count_2020['weekday'] = count_2020.Date.dt.weekday
count_2020['hour'] = count_2020.Date.dt.hour
count_2020['week'] = count_2020.Date.dt.isocalendar().week
# %%
yearly_dev = pd.DataFrame(columns=get_sql_table(db_engine, 'count_2020').columns)
for table in tables[:-1]:
    df = get_sql_table(db_engine, table)
    agg_df = df.groupby(df.Date.dt.year, as_index=False).sum()
    agg_df['Date'] = df.Date.dt.year[1]
    yearly_dev = yearly_dev.append(agg_df)

yearly_dev.set_index('Date', inplace=True)
yearly_dev_per = (yearly_dev/yearly_dev.loc[2016])*100
# %%

# %%
stations = get_sql_table(db_engine, 'standortdaten')
yearly = count_2020.groupby(count_2020.Date.dt.year, as_index=False).sum().transpose()
yearly.columns = [f'sum{count_2020.Date.dt.year[1]}']
yearly = yearly.join(stations.set_index('Zählstelle'))
yearly.index.name = 'Zählstelle'
yearly.reset_index(inplace=True)
yearly['Zählstelle_no'] = yearly['Zählstelle'].apply(lambda x: x[0:2])

# %%
fig = px.scatter_mapbox(yearly, lat="Breitengrad", lon="Längengrad", hover_name="index",
                            hover_data={
                                'index' : False,
                                'Breitengrad': False,
                                'Längengrad': False,
                                'sum_2020' : True,
                                'Beschreibung - Fahrtrichtung': True,
                                'Installationsdatum': True},
                            color='index', size='sum_2020',zoom=10,
                            mapbox_style="open-street-map",
                            height=800)
# %%
# Sum of all years  - SQL view 
 # difficult
# Distribution / Histogram

# Proportion der Stationen an Gesamt

# Development of cyclist per year rel. to 2016 per station
 # bar plot

# Yearly cycle of cyclist per station (per month) rel. to 2019
    # point/line plot aggregated per month (mean or sum)

# Hourly data per station with data selector
    # line plot /  box plot

# Tag mit der höchsten Fahrraddichte

# Höchste Fahrraddichte zu bestimmter Uhrzeit pro Station

# Differenz Woche / Wochenende

# Differenz Richtung pro Stunde

# Nord/Süd OST/WEST

# Anomalies


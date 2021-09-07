"""An example of showing geographic data."""

import streamlit as st
import pandas as pd
import openpyxl
import numpy as np
import altair as alt
import pydeck as pdk

# SETTING PAGE CONFIG TO WIDE MODE
st.set_page_config(layout="wide")

# LOADING DATA
DATE_TIME = "date/time"
DATA_URL = (
    "https://www.berlin.de/sen/uvk/_assets/verkehr/verkehrsplanung/radverkehr/weitere-radinfrastruktur/zaehlstellen-und-fahrradbarometer/gesamtdatei_stundenwerte.xlsx"
)

@st.cache(persist=True)
def load_data(sheet_name):
    df = pd.read_excel(DATA_URL, sheet_name=sheet_name, header=0)
    header = [x.split()[0].replace('-', '_') for x in df.columns.values.tolist()]
    header[0] = 'date'
    df.columns = header
    df.drop(0, inplace=True)
    return df

def load_stations():
    stations = pd.read_excel(DATA_URL, sheet_name=2)
    return stations

sheet = st.slider("Select Year", 3, 11)
data = load_data(sheet)
stations = load_stations()

'data', data
'stations', stations
#%%
import openpyxl
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import numpy as np
import seaborn as sns
# %%
def count_sheet_to_df(wb, sheetname):

    sheet = wb[sheetname]
    df = pd.DataFrame(sheet.values)
    header = [x.split()[0] for x in df.loc[0].values.tolist()]
    header[0] = 'Date'
    df.columns = header
    df.drop(0, inplace=True)

    return df

def station_sheet_to_df(wb, sheetname):
    sheet = wb[sheetname]
    df = pd.DataFrame(sheet.values)
    df.columns = df.loc[0].values.tolist()
    df.drop(0, inplace=True)

    df['Installationsdatum'] = pd.to_datetime(df['Installationsdatum'], format='%Y-%m-%d %H:%M:%S')
    df['Breitengrad'] = pd.to_numeric(df['Breitengrad'], errors='ignore')
    df['Längengrad'] = pd.to_numeric(df['Längengrad'], errors = 'ignore')

    return df
# %%
def df_to_sql(df,  table_name, host='localhost', db='bikecount'):
    engine = create_engine(f'postgres://{host}/{db}', echo=False)
    df.to_sql(table_name, engine, method='multi', chunksize=1000)
    
def clean_data(df):
    df.iloc[:, 1:].replace([None], np.nan, inplace=True)
    df = df.apply(pd.to_numeric, downcast='signed', errors='ignore')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S')
    df.set_index('Date', inplace=True)

    return df

if __name__ == '__main__':
    wb = openpyxl.load_workbook('./data/gesamtdatei_stundenwerte.xlsx')
    sheets = wb.sheetnames

    station = station_sheet_to_df(wb, 'Standortdaten')
    df_to_sql(station, 'standortdaten')

    counts_dict = {}
    for sheet in sheets[3:]:
        df_to_sql(clean_data(count_sheet_to_df(wb, sheet)), f'count_{sheet[-4:]}')



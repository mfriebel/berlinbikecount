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
    header = [x.split()[0].replace('-', '_') for x in df.loc[0].values.tolist()]
    header[0] = 'date'
    df.columns = header
    df.drop(0, inplace=True)

    return df

def station_sheet_to_df(wb, sheetname):
    sheet = wb[sheetname]
    df = pd.DataFrame(sheet.values)
    df.columns = [x.lower() for x in df.loc[0].values.tolist()]
    df.drop(0, inplace=True)

    df['installationsdatum'] = pd.to_datetime(df['installationsdatum'], format='%Y-%m-%d %H:%M:%S')
    df['breitengrad'] = pd.to_numeric(df['breitengrad'], errors='ignore')
    df['längengrad'] = pd.to_numeric(df['längengrad'], errors = 'ignore')
    df['zählstelle'] = df['zählstelle'].apply(lambda x: x.replace('-','_'))

    return df
# %%
def df_to_sql(df,  table_name, host='localhost', db='bikecount'):
    engine = create_engine(f'postgres://{host}/{db}', echo=False)
    df.to_sql(table_name, engine, method='multi', chunksize=1000)
    
def clean_data(df):
    df.iloc[:, 1:].replace([None], np.nan, inplace=True)
    df = df.apply(pd.to_numeric, downcast='signed', errors='ignore')
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')
    df.set_index('date', inplace=True)

    return df

if __name__ == '__main__':
    wb = openpyxl.load_workbook('./data/gesamtdatei_stundenwerte.xlsx')
    sheets = wb.sheetnames

    station = station_sheet_to_df(wb, 'Standortdaten')
    df_to_sql(station, 'standortdaten')

    counts_dict = {}
    for sheet in sheets[3:]:
        df_to_sql(clean_data(count_sheet_to_df(wb, sheet)), f'count_{sheet[-4:]}')



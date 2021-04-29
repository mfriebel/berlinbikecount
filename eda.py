#%%
import openpyxl
import pandas as pd
import seaborn as sns
from sql_data_import import count_sheet_to_df, station_sheet_to_df, clean_data
import plotly.express as px
#%%
wb = openpyxl.load_workbook('./data/gesamtdatei_stundenwerte.xlsx')
#%%
wb.get_sheet_names()
#%%
count_2020 = count_sheet_to_df(wb, 'Jahresdatei 2020')
count_2020 = clean_data(count_2020)
stations = station_sheet_to_df(wb, 'Standortdaten')
# %%
count_2020['year'] = count_2020.Date.dt.year
count_2020['month'] = count_2020.Date.dt.month
count_2020['season'] = count_2020.Date.dt.quarter
count_2020['weekday'] = count_2020.Date.dt.weekday
count_2020['hour'] = count_2020.Date.dt.hour
count_2020['week'] = count_2020.Date.dt.isocalendar().week
# %%
sheets = wb.sheetnames
counts_dict = {}
for sheet in sheets[3:]:
    counts_dict[sheet[-4:]] = clean_data(count_sheet_to_df(wb, sheet))
# %%
# %%
yearly_dev = pd.DataFrame(columns = counts_dict['2020'].columns)
# %%
for key in counts_dict.keys():
    agg_df = counts_dict[key].groupby(counts_dict[key].Date.dt.year, as_index=False).sum()
    agg_df['Date'] = key
    yearly_dev = yearly_dev.append(agg_df)
# %%

# %%
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

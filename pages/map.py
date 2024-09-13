import dash
from dash import Dash, html, dcc, callback 
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime as dt
from datetime import date
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os
from dotenv import load_dotenv 
import dash_leaflet as dl
import dash_leaflet.express as dlx
from credentials import sql_engine_string_generator

print ('plotting map')

# register this as a page in the app
dash.register_page(__name__,    
    requests_pathname_prefix="/webapp-Borden/",
    routes_pathname_prefix="/webapp-Borden/"
)

# set the sql engine string
sql_engine_string=sql_engine_string_generator('DATAHUB_PSQL_SERVER','DATAHUB_DCP_DBNAME','DATAHUB_PSQL_USER','DATAHUB_PSQL_PASSWORD')
sql_engine=create_engine(sql_engine_string)


# sql query
sql_query="""
select distinct on (siteid) siteid, description, latitude, longitude, groundelevation from stations where siteid in ('BOR', 'EGB') ;
"""
# create the dataframe from the sql query
sites_df=pd.read_sql_query(sql_query, con=sql_engine)
sites_df.columns=['siteid', 'sitename', 'lat', 'lon', 'alt']
sites_df.set_index('siteid', inplace=True)

sites_df['description'] = sites_df.index + ' ' + sites_df['sitename']

# create the geojson data from the dataframe
sites_dict = sites_df.to_dict(orient='records')
# print (sites_dict)
sites_geojson = dlx.dicts_to_geojson([{**site, **dict(tooltip=site['description'])} for site in sites_dict])
# print (sites_geojson)

layout = dl.Map(
   [dl.TileLayer(), dl.GeoJSON(data=sites_geojson, id="geojson", zoomToBounds=True)],
   center=[44.27,-79.85], zoom=9, style={"width": "1000px", "height": "500px"},
)

# def create_figure(sites_df):
#     fig = px.scatter_geo(sites_df, lat='latitude', lon='longitude')
#     return fig








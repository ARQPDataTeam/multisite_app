import dash
from dash import Dash, html, dcc, callback 
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import date
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os
from dotenv import load_dotenv
import numpy as np

from credentials import sql_engine_string_generator
from postgres_query import fig_generator

print ('plotting Borden')

# register this as a page in the app
dash.register_page(__name__,
    requests_pathname_prefix="/webapp-SWAPIT/",
    routes_pathname_prefix="/webapp-SWAPIT/"
)

# set datetime parameters
now=dt.today()
start_date=(now-td(days=7)).strftime('%Y-%m-%d')
end_date=now.strftime('%Y-%m-%d')


csat_table='bor__csat_m_v0'
csat_species_list='ws_u, ws_v, vtempa'
csat_axis_list=[False, False, True]
csat_plot_title='Borden CSAT'
csat_y_title_1='Winds (m/s)'
csat_y_title_2='Virt Temp (C)'
csat_secondary_y_flag=True

pic_table='bor__g2311f_m_v0'
pic_species_list='ch4, co2'
pic_axis_list=[False, True]
pic_plot_title='Borden Picarro'
pic_y_title_1='CO2'
pic_y_title_1='CH4'
pic_secondary_y_flag=True

# set up the app layout
layout = html.Div(children=
                    [
                    html.H1(children=['Borden Dashboard']),
                    html.Div(children=['Borden CSAT Display']),

                    dcc.DatePickerRange(
                        id='csat-date-picker',
                        min_date_allowed='2024-01-01',
                        max_date_allowed=end_date
                    ),
                    dcc.Graph(id='csat_plot',figure=fig_generator(start_date,end_date,csat_table,csat_species_list,csat_axis_list,csat_plot_title,csat_y_title_1,csat_y_title_2,csat_secondary_y_flag)),
                    html.Div(children=['Borden Picarro Display']),

                    # dcc.DatePickerRange(
                    #     id='pic-date-picker',
                    #     min_date_allowed='2024-01-01',
                    #     max_date_allowed=end_date
                    # ),
                    # dcc.Graph(id='pic_plot',figure=fig_generator(start_date,end_date,pic_table,pic_species_list,pic_axis_list,pic_plot_title,pic_y_title_1,pic_y_title_2,pic_secondary_y_flag))
                    ] 
                    )

@callback(
    Output('csat_plot', 'figure'),
    Input('csat-date-picker', 'start_date'),
    Input('csat-date-picker', 'end_date'))

# @callback(
#     Output('pic_plot', 'figure'),
#     Input('pic-date-picker', 'start_date'),
#     Input('pic-date-picker', 'end_date'))

def update_output(start_date,end_date):
    if not start_date or not end_date:
        raise PreventUpdate
    else:
        csat_fig=fig_generator(start_date,end_date,csat_table,csat_species_list,csat_axis_list,csat_plot_title,csat_y_title_1,csat_y_title_2,csat_secondary_y_flag)
        return csat_fig

# if __name__=='__main__':
#     app.run(debug=True)

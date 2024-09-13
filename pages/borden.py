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
from postgres_query import first_entry

print ('plotting Borden')

# register this as a page in the app
dash.register_page(__name__,
    requests_pathname_prefix="/webapp-SWAPIT/",
    routes_pathname_prefix="/webapp-SWAPIT/"
)



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
pic_y_title_2='CH4'
pic_secondary_y_flag=True

# set datetime parameters
csat_first_date=first_entry(csat_table)
pic_first_date=first_entry(pic_table)
now=dt.today()
start_date=(now-td(days=7)).strftime('%Y-%m-%d')
end_date=now.strftime('%Y-%m-%d')

# set up the app layout
layout = html.Div(children=
                    [
                    html.H1(children=['Borden Dashboard']),
                    html.H2(children=['Borden CSAT Display']),

                    dcc.DatePickerRange(
                        id='csat-date-picker',
                        min_date_allowed=csat_first_date,
                        max_date_allowed=end_date,
                        display_format='YYYY-MM-DD'
                    ),
                    dcc.Graph(id='csat_plot',figure=fig_generator(start_date,end_date,csat_table,csat_species_list,csat_axis_list,csat_plot_title,csat_y_title_1,csat_secondary_y_flag,csat_y_title_2)),
                    html.Br(),
                    html.H2(children=['Borden Picarro Display']),

                    dcc.DatePickerRange(
                        id='pic-date-picker',
                        min_date_allowed=pic_first_date,
                        max_date_allowed=end_date
                    ),
                    dcc.Graph(id='pic_plot',figure=fig_generator(start_date,end_date,pic_table,pic_species_list,pic_axis_list,pic_plot_title,pic_y_title_1,pic_secondary_y_flag,pic_y_title_2))
                    ] 
                    )

@callback(
    Output('csat_plot', 'figure'),
    Input('csat-date-picker', 'csat_start_date'),
    Input('csat-date-picker', 'csat_end_date'))

def update_csat(csat_start_date,csat_end_date):
    if not csat_start_date or not csat_end_date:
        raise PreventUpdate
    else:
        print ('Updating plot')
        csat_fig=fig_generator(csat_start_date,csat_end_date,csat_table,csat_species_list,csat_axis_list,csat_plot_title,csat_y_title_1,csat_y_title_2,csat_secondary_y_flag)
    return csat_fig

@callback(
    Output('pic_plot', 'figure'),
    Input('pic-date-picker', 'pic_start_date'),
    Input('pic-date-picker', 'pic_end_date'))

def update_pic(pic_start_date,pic_end_date):
    if not pic_start_date or not pic_end_date:
        raise PreventUpdate
    else:
        print ('Updating plot')
        pic_fig=fig_generator(pic_start_date,pic_end_date,pic_table,pic_species_list,pic_axis_list,pic_plot_title,pic_y_title_1,pic_y_title_2,pic_secondary_y_flag)
    return pic_fig


# if __name__=='__main__':
#     app.run(debug=True)

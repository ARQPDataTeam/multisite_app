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

print ('plotting Borden')

# register this as a page in the app
dash.register_page(__name__,
    requests_pathname_prefix="/webapp-SWAPIT/",
    routes_pathname_prefix="/webapp-SWAPIT/"
)

# set the sql engine string
sql_engine_string=sql_engine_string_generator('DATAHUB_PSQL_SERVER','DATAHUB_BORDEN_DBNAME','DATAHUB_PSQL_USER','DATAHUB_PSQL_PASSWORD')
sql_engine=create_engine(sql_engine_string)

# set datetime parameters
now=dt.today()
start_time=(now-td(days=7)).strftime('%Y-%m-%d')


# csat sql query
csat_sql_query=("""
SET TIME ZONE 'GMT';
SELECT DISTINCT ON (datetime) * FROM (
	SELECT datetime, ws_u AS u, ws_v AS v, vtempa AS temp
	FROM bor__csat_m_v0         
	WHERE ws_u IS NOT NULL
	AND datetime >= '{}'
) AS csat
ORDER BY datetime;
""").format(start_time)

# picarro sql query
pic_sql_query="""
SET TIME ZONE 'GMT';
SELECT DISTINCT ON (datetime) * FROM (
	SELECT datetime, ch4, co2
	FROM bor__g2311f_m_v0
	WHERE ch4 IS NOT NULL
	AND datetime >= '{}'
) AS pic
ORDER BY datetime;
""".format(start_time)

# create the dataframes from the sql query
csat_output_df=pd.read_sql_query(csat_sql_query, con=sql_engine)
pic_output_df=pd.read_sql_query(pic_sql_query, con=sql_engine)

# print (csat_output_df)

# set a datetime index
csat_output_df.set_index('datetime', inplace=True)
csat_output_df.index=pd.to_datetime(csat_output_df.index)

# temporary fill of csat vtemps
csat_output_df.loc[:,'temp']=(np.random.randn(csat_output_df.shape[0]))*.2-10


pic_output_df.set_index('datetime', inplace=True)
pic_output_df.index=pd.to_datetime(pic_output_df.index)

beginning_date=csat_output_df.index[0]
ending_date=csat_output_df.index[-1]


# set plotting parameters
csat_output_df.loc['axis',:]=[False, False, True]
pic_output_df.loc['axis',:]=[False, True]

# print(beginning_date, ending_date)
# use specs parameter in make_subplots function
# to create secondary y-axis


# plot a scatter chart by specifying the x and y values
# Use add_trace function to specify secondary_y axes.
def create_figure (df_index, df, plot_title, y_title_1, y_title_2, df_columns):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for column in df_columns:
        print (df_index, df.loc[:,column])
        fig.add_trace(
            go.Scatter(x=df_index[-10500:], y=df.loc[df_index[-10500:],column[-10500:]], name=column),
            secondary_y=df.loc['axis',column])
    
    # set axis titles
    fig.update_layout(
        template='simple_white',
        title=plot_title,
        xaxis_title="Date",
        yaxis_title=y_title_1,
        yaxis2_title=y_title_2,
        legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )   
    )
    return fig

# set up the app layout
layout = html.Div(children=
                    [
                    html.H1(children=['Borden Dashboard']),
                    html.Div(children=['Borden CSAT Display']),

                    # dcc.DatePickerRange(
                    #     id='my-date-picker-range',
                    #     min_date_allowed=beginning_date,
                    #     max_date_allowed=ending_date
                    # ),
                    dcc.Graph(id='csat-winds_plot',figure=create_figure(csat_output_df.index,csat_output_df,'Borden CSAT','Winds (m/s)','Virt Temp (C)',csat_output_df.columns)),
                    html.Div(className='gap',style={'height':'10px'}),
                    html.Div(children=['Borden Picarro Display']),

                    # dcc.DatePickerRange(
                    #     id='my-date-picker-range',
                    #     min_date_allowed=beginning_date,
                    #     max_date_allowed=ending_date
                    # ),
                    dcc.Graph(id='csat-carbon_plot',figure=create_figure(pic_output_df.index,pic_output_df,'Borden Picarro','CO2 (ppbv)','CH4 (ppbv)',pic_output_df.columns)),

                    ] 
                    )

# @app.callback(
#     Output('graph_2', 'figure'),
#     [Input('date-picker', 'start_date'),
#     Input('date-picker', 'end_date')],
#     [State('submit_button', 'n_clicks')])

# @callback(
#     Output('csat-winds_plot', 'figure'),
#     Input('my-date-picker-range', 'start_date'),
#     Input('my-date-picker-range', 'end_date'))

# @callback(
#     Output('csat-carbon_plot', 'figure'),
#     Input('my-date-picker-range', 'start_date'),
#     Input('my-date-picker-range', 'end_date'))

# def update_output(start_date, end_date):
#     print (start_date, end_date)
#     if not start_date or not end_date:
#         raise PreventUpdate
#     else:
#         output_selected_df = csat_output_df.loc[
#             (csat_output_df.index >= start_date) & (csat_output_df.index <= end_date), :
#         ]
#         return create_figure(output_selected_df)


# if __name__=='__main__':
#     app.run(debug=True)

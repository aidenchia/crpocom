from typing import List
from datetime import datetime

import pandas as pd
import plotly
import plotly.graph_objects as go

def add_graph_info(fig: go.Figure,
                   title="", 
                   yaxis_title="",
                   xaxis_title="",
                   subtitle="",
                   secondary_y: List[str]=None,
                   xrange:List[int]=None,
                   yrange:List[int]=None):

    title = f"{title} <br><sup>{subtitle}</sup>"
    fig.update_layout(title=title, 
                      yaxis_title=yaxis_title, 
                      xaxis_title=xaxis_title)
    
    # Update range of axis
    fig.update_xaxes(range=xrange)
    fig.update_yaxes(range=yrange)

    if secondary_y:
        fig.update_yaxes(title_text=', '.join(secondary_y), secondary_y=True)


def plot_line(df: pd.DataFrame, 
             start_date: datetime = None, 
             end_date: datetime = None,
             sort=True, 
             title="", 
             yaxis_title="",
             xaxis_title="",
             subtitle="",
             secondary_y: List[str]=None,
             yrange:List[int]=None,
             return_fig=False):

    # Convert to df if needed
    if type(df) == pd.Series:
        df = df.to_frame()

    # Set up subplots if secondary y-axis is needed
    fig = go.Figure()
    
    # Filter to start and end dates
    df = df.loc[start_date:end_date]

    # Sort data by index if needed
    if sort:
        df.sort_index(inplace=True)
    
    # Handle x-axis as string dtypes so it won't look weird in plot
    if type(df.index) == pd.core.indexes.datetimes.DatetimeIndex:
        xaxis = [x.strftime("%d-%b-%y") for x in pd.to_datetime(df.index.values)]
    else:
        xaxis = df.index.values

    # Add traces to figure
    for col in df.columns.values:
            if secondary_y:
                secondary_y = [secondary_y] if type(secondary_y) != list else secondary_y
                if col in secondary_y:
                    fig.add_trace(go.Scatter(x=xaxis, 
                                             y=df[col].values, 
                                             name=f"{col}"), 
                                             secondary_y=True)
                else:
                    fig.add_trace(go.Scatter(x=xaxis, 
                                             y=df[col].values, 
                                             name=f"{col}"),
                                             secondary_y=False)
            else:
                fig.add_trace(go.Scatter(x=xaxis, 
                                         y=df[col].values, 
                                         name=f"{col}"))

    add_graph_info(fig=fig, title=title, subtitle=subtitle,
                   xaxis_title=xaxis_title, yaxis_title=yaxis_title,
                   secondary_y=secondary_y, xrange=None, yrange=yrange)

    return fig if return_fig else fig.show() 
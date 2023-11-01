# Data is visualized as a plotly (interactive map) - Working
from datetime import datetime, timedelta
from netCDF4 import Dataset as NetCDFFile
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

@st.cache_data
def get_data():
    filename = "/home/mohamed/Documents/CDS-API-Connect/CDS-API-App/data/dd_2023-10-31 11-55-39.444854.nc"
    return filename

filename = get_data()
nc = NetCDFFile(filename)
title = getattr(nc, 'title', 'Title Not Found')

# Extract data from the NetCDF file
st.title(title)  # Display the title, even if it's not found
st.header("Description")
description = getattr(nc, 'description', 'Description Not Found')
st.write(description)  # Display the description

# Access variables
alpha = nc.variables["t2m"][:]
lat = nc.variables["latitude"][:]
lon = nc.variables["longitude"][:]
time = nc.variables["time"][:]
time_units = nc.variables["time"].units 

# Fill missing values with 0
alpha = alpha.filled(fill_value=0)

def convert_time(t):
    origin_date = pd.to_datetime(time_units.split("since")[-1].strip())  # Extract and parse the origin date
    new_time = origin_date + pd.to_timedelta(t, unit=time_units.split("since")[0].strip())
    return new_time

# Function to format time for display
def id_to_time(i):
    return convert_time(time[i])

# Cache Plotly figure creation
@st.cache_data
def plotly_plot(time_idx):
    fig = go.Figure(data=go.Heatmap(x=lon, y=lat, z=alpha[time_idx], colorscale='RdBu_r'))
    fig.update_xaxes(title_text='Longitude')
    fig.update_yaxes(title_text='Latitude')
    fig.update_layout(width=800, height=600)
    return fig
# Slider to select a specific date
time_id = st.select_slider("Date", options=range(len(time)), format_func=id_to_time)
# Create the Plotly figure and display it
fig = plotly_plot(time_id)
st.write(fig)

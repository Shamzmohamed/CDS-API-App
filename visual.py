# netcdf file visualization working but using matplotlib not as Interactive Map
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from netCDF4 import Dataset as NetCDFFile

# Provide the path to your own NetCDF file
file_path = '/home/mohamed/Documents/ERA5/Data/t2m_201801.nc' 

# Load the NetCDF file 
nc = NetCDFFile(file_path)

# Access the "t2m" variable
t2m = nc.variables["t2m"][:]

# Access the "time" variable
time = nc.variables["time"][:]

# Access the "lon" and "lat" variables
lon = nc.variables["longitude"][:]
lat = nc.variables["latitude"][:]

# # Function to convert time
# def convert_time(t):
#     specific_date = datetime(2023, 10, 17,0, 0, 0)
#     new_time = specific_date + timedelta(hours=int(t))
#     return new_time
# Access the "time" variable
time = nc.variables["time"][:]
time_units = nc.variables["time"].units  # This should give you the time unit

# Function to convert time
def convert_time(t):
    origin_date = pd.to_datetime(time_units.split("since")[-1].strip())  # Extract and parse the origin date
    new_time = origin_date + pd.to_timedelta(t, unit=time_units.split("since")[0].strip())
    return new_time

# Function to format time for display
def id_to_time(i):
    return convert_time(time[i])

# Streamlit caching for plot
@st.cache
def plotly_plot(time_idx):
    fig = go.Figure(data=go.Heatmap(x=lon, y=lat, z=t2m[time_idx]))
    return fig

# Get the available description attribute or provide a default description
description = getattr(nc, 'description', 'No description available')

# Display the title and description
st.title("2 Meter Temperature Data")  # You can set a custom title here
st.header("Description")
st.write(description)

# Create a slider for selecting a specific date
time_id = st.select_slider("Date", options=range(len(time)), format_func=id_to_time)

t2m_1d = t2m[time_id].flatten()

# Flatten lon and lat arrays to match the dimensions of t2m
lon_grid, lat_grid = np.meshgrid(lon, lat)
lon_1d = lon_grid.flatten()
lat_1d = lat_grid.flatten()

# Ensure all arrays have the same length
if len(lon_1d) != len(lat_1d) or len(lat_1d) != len(t2m_1d):
    raise ValueError("All arrays must be of the same length")

# Create a heatmap using Matplotlib
fig, ax = plt.subplots(figsize=(18, 10))
extent = [lon.min(), lon.max(), lat.min(), lat.max()]
heatmap = ax.imshow(t2m[time_id], extent=extent, cmap='RdBu_r', aspect='auto')
plt.colorbar(heatmap, ax=ax, label='Temperature (°C)')
ax.set_title(f'2 Meter Temperature on {id_to_time(time_id)}')  # Use the formatted time
ax.set_xlabel('Longitude', fontsize=16, fontweight='bold')
ax.set_ylabel('Latitude', fontsize=16, fontweight='bold')

# Display the Matplotlib plot in Streamlit
st.pyplot(fig)

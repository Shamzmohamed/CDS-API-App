import urllib.request
import streamlit as st
from datetime import datetime, timedelta
import folium
from folium import plugins
from streamlit_folium import folium_static as st_folium
import pandas as pd
import xarray as xr
import numpy as np
from cdsapi import Client

st.set_page_config(page_title="CDS API", page_icon="🌤️")
st.title("ClimateDataStoreConnection")

# Function to download data from CDS API
def download_data(year, variable):
    c = Client()

    # Define the request parameters based on the selected variable
    if variable == "2m_temperature":
        request_params = {
            "variable": "2m_temperature",
            "product_type": "reanalysis",
            "year": year,
            "month": "01",
            "day": "01",
            "time": "00:00",
            "format": "netcdf",
        }
    elif variable == "2m_dewpoint_temperature":
        # Define parameters for dew point temperature
        # Add more cases for other variables
        pass
    else:
        st.error("Selected variable is not supported.")
        return None

    # Download the data
    with st.spinner(f"Downloading {variable} data for year {year}..."):
        r = c.retrieve("reanalysis-era5-single-levels", request_params)
        r.download("data.nc")

    st.success(f"{variable} data for year {year} downloaded successfully.")
    return "data.nc"

# Streamlit UI components
with st.form("data_fetch_api"):
    col1, col2 = st.columns(2)
    
    # Select year
    year = st.selectbox("Select Year", list(range(1979, datetime.now().year + 1)))

    # Select variable
    params = st.selectbox("Select Weather Parameter", ["2m_temperature", "2m_dewpoint_temperature"])
    
    st.write("Click on map to select location")
    DEFAULT_LATITUDE = 51.96
    DEFAULT_LONGITUDE = 7.62
    m = folium.Map(location=[DEFAULT_LATITUDE, DEFAULT_LONGITUDE], zoom_start=8)
    m.add_child(folium.LatLngPopup())
    f_map = st_folium(m, width=670, height=500)

    selected_latitude = DEFAULT_LATITUDE
    selected_longitude = DEFAULT_LONGITUDE

    if f_map.get("last_clicked"):
        selected_latitude = f_map["last_clicked"]["lat"]
        selected_longitude = f_map["last_clicked"]["lng"]

    submitted = st.form_submit_button("Submit")

if submitted:
    st.success(f"Selected location: {selected_latitude}, {selected_longitude}")

    # Download data based on user's selection
    nc_file = download_data(year, params)
    
    if nc_file:
        # Open the downloaded NetCDF file using xarray
        ds = xr.open_dataset(nc_file)

        # Visualize the data as desired
        st.write(f"Visualization of {params} data for year {year} here.")
        # You can create plots, maps, or other visualizations using the data from 'ds'

        # Close the NetCDF file
        ds.close()

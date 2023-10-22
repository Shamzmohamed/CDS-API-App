# Total precipitation added
import streamlit as st
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
import geopandas as gpd
import pandas as pd
import folium
import plotly.express as px

from climate_data_store_connection import ClimateDataStoreConnection

st.set_page_config(page_title="CDS API", page_icon="🌤️")

st.title("ClimateDataStoreConnection")
shapefile_path = '/home/mohamed/Documents/data/rheine-erft.shp'
gdf = gpd.read_file(shapefile_path)

# Plot the shapefile on the map
with st.form("data_fetch_api"):
    col1, col2 = st.columns(2)

    params = st.multiselect(
        "Select Weather Parameters",
        help="CDS offers many parameter but few selected for demo purpose.",
        options=[
            "Ambient Temperature (°C)",
            "Dew Point Temperature (°C)",
            "Surface Pressure (kPa)",
            "Total Precipitation (mm)",
        ],
    )

    date = st.date_input(
        "Select a date",
        value=datetime.today() - timedelta(days=6),
        min_value=datetime.fromisoformat("2023-01-01"),
        max_value=datetime.today() - timedelta(days=6),
    )

    st.write("Click on map to select location")

    # https://franekjemiolo.pl/using-selected-position-map-form-streamlit/
    DEFAULT_LATITUDE = 51.96
    DEFAULT_LONGITUDE = 7.62

    m = folium.Map(location=[DEFAULT_LATITUDE, DEFAULT_LONGITUDE], zoom_start=8)

    # The code below will be responsible for displaying
    # the popup with the latitude and longitude shown
    m.add_child(folium.LatLngPopup())

    f_map = st_folium(m, width=670, height=500)
    folium.LayerControl().add_to(m)
    folium.GeoJson(gdf).add_to(m)
    selected_latitude = DEFAULT_LATITUDE
    selected_longitude = DEFAULT_LONGITUDE

    submitted = st.form_submit_button("Submit")

if submitted:
    st.success(f"Selected location: {selected_latitude}, {selected_longitude}")

    if params:
        param_mapping_ip = {
            "Ambient Temperature (°C)": "2m_temperature",
            "Dew Point Temperature (°C)": "2m_dewpoint_temperature",
            "Surface Pressure (kPa)": "surface_pressure",
            "Total Precipitation (mm)": "total_precipitation",
        }

        param_mapping_op = {
            "t2m": "Ambient Temperature (°C)",
            "d2m": "Dew Point Temperature (°C)",
            "sp": "Surface Pressure (kPa)",
            "tp": "Total Precipitation (mm)",
        }

        data = {
            "product_type": "reanalysis",
            "format": "netcdf",
            "variable": [param_mapping_ip[p] for p in params],
            "year": [str(date.year)],
            "month": [str(date.month)],
            "day": [str(date.day)],
            "time": [
                "00:00",
                "01:00",
                "02:00",
                "03:00",
                "04:00",
                "05:00",
                "06:00",
                "07:00",
                "08:00",
                "09:00",
                "10:00",
                "11:00",
                "12:00",
                "13:00",
                "14:00",
                "15:00",
                "16:00",
                "17:00",
                "18:00",
                "19:00",
                "20:00",
                "21:00",
                "22:00",
                "23:00",
            ],
            "area": [
                selected_latitude,
                selected_longitude,
                selected_latitude,
                selected_longitude,
            ],
        }

        with st.spinner("Fetching weather data..."):
            conn = st.experimental_connection("", type=ClimateDataStoreConnection)
            df = conn.query(data)
            variable_names = df.columns.tolist()
            print("Variable Names:")
            for variable in variable_names:
                print(variable)
            with st.spinner("Plotting..."):
                if "t2m" in df.columns:
                    df["t2m"] = df["t2m"] - 273.15
                    # Filter the data for the selected location (latitude and longitude)
                    location_data = df[(df['latitude'] == selected_latitude) & (df['longitude'] == selected_longitude)]

                    monthly_avg = location_data.resample('M').mean()
                    fig = px.line(x=monthly_avg.index, y=monthly_avg['t2m'], labels={'x': 'Month', 'y': 'Temperature (°C)'},
                                  title="Monthly Average Temperature for the Selected Location")
                    st.plotly_chart(fig, use_container_width=True)

                df.columns = [param_mapping_op[c] for c in df.columns]
                for i in range(df.shape[1]):
                    fig = px.line(x=df.index, y=df.iloc[:, i], labels={'x':'Time', 'y':df.columns[i]},
                                   title="Time series plot of "+df.columns[i])
                    st.plotly_chart(fig, use_container_width=True)
            

else:
    st.error("Select a minimum of 1 weather parameter")

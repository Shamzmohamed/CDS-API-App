import streamlit as st
import cdsapi
import xarray as xr
import datetime
import numpy as np
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go

# Define constants
DATA_DIR = '/home/mohamed/Documents/ERA5/Data'
VARIABLE_NCDF = 't2m'  # Default variable
SHAPEFILE_PATH = '/home/mohamed/Documents/ERA5/World_Map/World_Map.shp'

# Function to download and process data for a specific country, year, and location
def download_and_visualize_data(country, year, latitude, longitude, selected_parameter):
    start_date = datetime.date(year, 1, 1)
    end_date = datetime.date(year, 12, 31)

    parameter_mapping = {
        'Ambient Temperature (°C)': '2m_temperature', 'Dew Point Temperature (°C)': '2m_dewpoint_temperature',
        'Surface Pressure (kPa)': 'surface_pressure','Total Precipitation (mm)': 'total_precipitation'}

    # Get the corresponding CDS parameter name
    cds_parameter = parameter_mapping[selected_parameter]

    # Define a separate mapping for CDS parameter names to NetCDF variable names
    cds_to_ncdf_mapping = {
        '2m_temperature': 't2m','2m_dewpoint_temperature': 'd2m',
        'surface_pressure': 'sp','total_precipitation': 'tp'}

    # Define a separate mapping for parameter conversions
    parameter_conversions = {
        '2m_temperature': lambda x: x - 273.15,  # Convert to Celsius
        '2m_dewpoint_temperature': lambda x: x - 273.15,  # Convert to Celsius
        'surface_pressure': lambda x: x / 1000,  # Divide by 1000 to get kPa
        'total_precipitation': lambda x: x  # No conversion for total precipitation
    }

    # Map the selected parameter to the corresponding VARIABLE_NCDF
    VARIABLE_NCDF = cds_to_ncdf_mapping[cds_parameter] 

    # Download data from CDS for the selected country and location
    c = cdsapi.Client()
    c.retrieve(
        'reanalysis-era5-single-levels',
        {'product_type': 'reanalysis','variable': cds_parameter,
            'year': str(year),
            'month': [str(month).zfill(2) for month in range(1, 13)],
            'day': [str(day).zfill(2) for day in range(1, 32)],
            'format': 'netcdf',
            'area': [latitude, longitude, latitude, longitude],  # Use the selected latitude and longitude
        },
        f'{DATA_DIR}/{VARIABLE_NCDF}_{country}_{year}.nc')

    # Open the NetCDF file
    ds = xr.open_dataset(f'{DATA_DIR}/{VARIABLE_NCDF}_{country}_{year}.nc')
    data = ds[VARIABLE_NCDF].values[:, 0, 0]
    converted_data = parameter_conversions[cds_parameter](data)

    months = [datetime.date(year, month, 1).strftime('%b') for month in range(1, 13)]

    # Calculate monthly averages
    monthly_averages = []
    for month in range(1, 13):
        month_data = converted_data[month - 1::12]
        month_avg = np.mean(month_data)
        monthly_averages.append(month_avg)

    # Create a Plotly line chart to visualize monthly averages
    figmavg = px.line(x=months,y=monthly_averages, markers='True',
        labels={'x': 'Month', 'y': f'Monthly Average {selected_parameter}'},
        title=f'Monthly {selected_parameter} Average for {country} in {year}',)
    st.plotly_chart(figmavg)

    # Create monthly statistics
    monthly_means = []
    monthly_mins = []
    monthly_maxs = []

    for month in range(1, 13):
        month_data = converted_data[month - 1::12]
        month_mean = np.mean(month_data)
        month_min = np.min(month_data)
        month_max = np.max(month_data)

        monthly_means.append(month_mean)
        monthly_mins.append(month_min)
        monthly_maxs.append(month_max)

    # Create a Plotly line chart to visualize monthly statistics
    figp = go.Figure()
    figp.add_trace(go.Scatter(x=months, y=monthly_maxs, mode='lines+markers', name=f'Monthly Max {selected_parameter}', line=dict(color='red')))
    figp.add_trace(go.Scatter(x=months, y=monthly_means, mode='lines+markers', name=f'Monthly Mean {selected_parameter}', line=dict(color='blue')))
    figp.add_trace(go.Scatter(x=months, y=monthly_mins, mode='lines+markers', name=f'Monthly Min {selected_parameter}', line=dict(color='green')))

    figp.update_layout(
        title=f'Monthly Statistics for {country} in {year}',
        xaxis_title='Month',yaxis_title=f'{selected_parameter} Values',
        legend=dict(x=1.02,y=1.0,
            traceorder='normal',bgcolor='rgba(255, 255, 255, 0.5)',
            bordercolor='rgba(255, 255, 255, 0.5)',borderwidth=2,),width=800,height=600)
    st.plotly_chart(figp)

# Streamlit app
st.title('Monthly Weather for Country')
gdf = gpd.read_file(SHAPEFILE_PATH)
country = st.selectbox('Select a country or region:', gdf['NAME'].tolist())
year = st.selectbox('Select a year:', list(range(2015, datetime.datetime.now().year + 1)))
selected_parameter = st.selectbox('Select a weather parameter:', [
    'Ambient Temperature (°C)','Dew Point Temperature (°C)','Surface Pressure (kPa)','Total Precipitation (mm)'])
selected_country = gdf[gdf['NAME'] == country]
if not selected_country.empty:
    geometry = selected_country.iloc[0].geometry
    # Select a latitude and longitude point from the geometry (e.g., centroid)
    latitude, longitude = geometry.centroid.y, geometry.centroid.x

if st.button('Visualize'):
    download_and_visualize_data(country, year, latitude, longitude, selected_parameter)

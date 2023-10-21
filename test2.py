# Total precipitation added
import streamlit as st
from datetime import datetime, timedelta
from streamlit_folium import st_folium
import folium
import plotly.express as px

from climate_data_store_connection import ClimateDataStoreConnection

st.set_page_config(page_title="CDS API", page_icon="🌤️")

st.title("CDS-API Connection")

with st.form("data_fetch_api"):

    col1, col2 = st.columns(2)

    params = st.multiselect(
        'Select Weather Parameters', help="CDS offers many parameter but few selected for demo purpose.",
        options=['Ambient Temperature (°C)', 'Dew Point Temperature (°C)', 'Surface Pressure (kPa)', 'Total Precipitation (mm)'])
    date = st.date_input('Select a date range',
                         value=[datetime(datetime.today().year, 1, 1), datetime(datetime.today().year, 12, 31)],
                         min_value=datetime(datetime.today().year, 1, 1),
                         max_value=datetime(datetime.today().year, 12, 31))
    st.write("Click on map to select location")
    
    # https://franekjemiolo.pl/using-selected-position-map-form-streamlit/
    DEFAULT_LATITUDE = 51.96
    DEFAULT_LONGITUDE = 7.62

    m = folium.Map(location=[DEFAULT_LATITUDE, DEFAULT_LONGITUDE], zoom_start=8)

    # The code below will be responsible for displaying 
    # the popup with the latitude and longitude shown
    m.add_child(folium.LatLngPopup())

    f_map = st_folium(m, width=670, height=500)

    selected_latitude = DEFAULT_LATITUDE
    selected_longitude = DEFAULT_LONGITUDE

    submitted = st.form_submit_button("Submit")

if submitted:
    st.success(f"Selected location: {selected_latitude}, {selected_longitude}")
    weather_map = folium.Map(location=[selected_latitude, selected_longitude], zoom_start=8)

    temperature_group = folium.FeatureGroup(name="Temperature")
    precipitation_group = folium.FeatureGroup(name="Precipitation")

    if params:  
        param_mapping_ip = {
            "Ambient Temperature (°C)": "2m_temperature", "Dew Point Temperature (°C)": "2m_dewpoint_temperature",
            "Surface Pressure (kPa)": "surface_pressure", "Total Precipitation (mm)": "total_precipitation"}

        param_mapping_op = {
            "t2m": "Ambient Temperature (°C)",
            "d2m": "Dew Point Temperature (°C)",
            "sp": "Surface Pressure (kPa)",
            "tp": "Total Precipitation (mm)"
        }
        start_date, end_date = date
        data = {
            'product_type': 'reanalysis',
            'format': 'netcdf',
            'variable': [param_mapping_ip[p]
                for p in params
            ],
            'year': [str(start_date.year)],
            'month': [str(start_date.month)],
            'day': [str(start_date.day)],
            'time': [
                '00:00', '01:00', '02:00', '03:00', '04:00', '05:00',
                '06:00', '07:00', '08:00', '09:00', '10:00', '11:00',
                '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
                '18:00', '19:00', '20:00', '21:00', '22:00', '23:00',
            ],
            'area': [
                selected_latitude, selected_longitude,
                selected_latitude, selected_longitude,
            ],
        }

        with st.spinner("Fetching weather data..."):
            full_year_data = None

        # Iterate through each day of the year and fetch data
        current_date = start_date
        while current_date <= end_date:
            data['year'] = [str(current_date.year)]
        data['month'] = [str(current_date.month)]
        data['day'] = [str(current_date.day)]

        conn = st.experimental_connection("", type = ClimateDataStoreConnection)
        day_data = conn.query(data)

        # Append the data to the full_year_data DataFrame
        if full_year_data is None:
            full_year_data = day_data
        else :
            full_year_data = full_year_data.append(day_data)

        # Move to the next day
        current_date += timedelta(days = 1)

        # Plot the data for each selected parameter
        for param in params:
            param_name = param_mapping_ip[param]
        st.write(f"Time series plot for {param} throughout the year")

        if param_name in full_year_data.columns:
            fig = px.line(x=full_year_data.index, y = full_year_data[param_name], labels = {
                    'x': 'Time',
                    'y': param},title = f"Time series plot of {param}")
            st.plotly_chart(fig, use_container_width = True)
        else :
            st.error(f"Data for {param} is not available for the selected location throughout the year.")


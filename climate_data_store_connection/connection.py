from streamlit.connections import ExperimentalBaseConnection
import cdsapi
import pandas as pd
import xarray as xr
import os
from datetime import datetime

class ClimateDataStoreConnection(ExperimentalBaseConnection[cdsapi.api.Client]):

    def _connect(self) -> cdsapi.api.Client:

        conn = cdsapi.Client()

        return conn
    
    def retrieve(self) -> cdsapi.api.Client.retrieve:

        return self._instance.retrieve
    
    def query(self, query_param):
        query_param['product_type'] = 'reanalysis'
        query_param['format'] = 'netcdf'
        # Create a unique file name to avoid overwriting existing data
        data_path = 'download_' + str(datetime.now()).replace(":", "-") + '.nc'
        ret = self.retrieve()
        ret('reanalysis-era5-single-levels', query_param, data_path)
        # Open the downloaded NetCDF file without any filtering or modification
        data = xr.open_dataset(data_path)
        # Remove the downloaded NetCDF file to free up space (if needed)
        os.remove(data_path)
        return data 
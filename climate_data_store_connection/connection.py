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
    
    def query(self, query_param,data_path):

        query_param['product_type'] = 'reanalysis'
        query_param['format'] = 'netcdf'

        # adding time in file name to avoid overlapping
        data_path = 'dd_'+str(datetime.now()).replace(":","-")+'.nc'
        ret = self.retrieve()
        ret('reanalysis-era5-single-levels',query_param,data_path)
        return data_path
        
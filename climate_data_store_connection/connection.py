from streamlit.connections import ExperimentalBaseConnection
import cdsapi
import shutil
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
    
    def query(self, query_param,down):

        query_param['product_type'] = 'reanalysis'
        query_param['format'] = 'netcdf'
        down = '/home/mohamed/Documents/CDS-API-Connect/CDS-API-App/data'

        # adding time in file name to avoid overlapping
        data_path = 'dd_'+str(datetime.now()).replace(":","-")+'.nc'
        local_path = os.path.join(down, data_path)
        ret = self.retrieve()
        ret('reanalysis-era5-single-levels',query_param,local_path)
        # final_path = os.path.join(down, data_path)
        # shutil.move(local_path, final_path)
        
        return local_path
        
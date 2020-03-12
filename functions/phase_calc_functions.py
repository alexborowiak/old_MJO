import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import dask.array
import cartopy.crs as ccrs
import pickle
import matplotlib.colors as colors
import datetime as dt
import pickle
from matplotlib.colors import BoundaryNorm
rb = plt.cm.RdBu
bm = plt.cm.Blues
best_blue = '#9bc2d5'
recherche_red = '#fbc4aa'
wondeful_white = '#f8f8f7'
import glob
import pdb

import warnings
warnings.filterwarnings('ignore')

import matplotlib.gridspec as gridspec



'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
'''~~~~~~~~~~~~~~~~~~~~~~ANOMALY CALCULATIONS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The following functions all work together to calculate the anomalies in a given phase of the MJO'''



# This function readis in the RMM form the Bureau's website and turns it into an 
# xarrau file. The useragent will need to be changed depending on the computer. Currently it is set to the VDI

def load_rmm():
    
    import urllib
    import io

    url = 'http://www.bom.gov.au/climate/mjo/graphics/rmm.74toRealtime.txt'
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'
    headers={'User-Agent':user_agent}
    request=urllib.request.Request(url,None,headers)
    response = urllib.request.urlopen(request)
    data = response.read()
    csv = io.StringIO(data.decode('utf-8'))

    rmm_df = pd.read_csv(csv, sep=r'\s+', header=None, skiprows=2,
        usecols=[0,1,2,3,4,5,6,7], names=['year', 'month', 'day','RMM1','RMM2', 'phase', 'amplitude', 'origin'])
    index = pd.to_datetime(rmm_df.loc[:,['year','month','day']])
    rmm_df.index = index

    rmm_xr = rmm_df.loc[:,['RMM1','RMM2', 'phase','amplitude']].to_xarray().rename({'index':'time'})
    
    return rmm_xr





'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''




def split_into_1to8(datafile, rmm_xr):
    
    
    
    '''~~~~~~~~~~~~~~~~~~ Inactive Phases'''
    rmm_inact_dates = rmm_xr.where(rmm_xr.amplitude < 1, drop = True).time.values
    datafile_inact = datafile.where(datafile.time.isin(rmm_inact_dates), drop = True)

    '''~~~~~~~~~~~~~~~~~~ Active Phases
    Summary: Looping through all the different RMM phases; getting the dates fro this phase; finding just the rainfall
    in this phase'''
    single_phase = [] # Storage for later concatinating in xarray
    rmm_act = rmm_xr.where(rmm_xr.amplitude >= 1, drop = True) # Only acitve when RMM > 1
    phases = np.arange(1,9) # 8 phases we are looping through
    for phase in phases:
        rmm_single_dates = rmm_act.where(rmm_act.phase == phase, drop = True).time.values # The dates of this phase
        datafile_single = datafile.where(datafile.time.isin(rmm_single_dates), drop = True) # The datafile data in this phase
        single_phase.append(datafile_single) # Appending

    phases = np.append(phases.astype('str'), 'inactive') # The ianctive also needs to be included
    single_phase.append(datafile_inact) 
    # phases = phases.astype(str)


    # Final File
    datafile_RMM_split = xr.concat(single_phase, pd.Index(phases, name = 'phase'))
    
    
    
    return  datafile_RMM_split






'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''



def  calculate_anomalies_1to8_mean(variable_split, variable):
    phase_mean = variable_split.groupby('phase').mean(dim = 'time')
    overall_mean = variable.mean(dim = 'time')
    anomalies = phase_mean/overall_mean
    
    return phase_mean, anomalies



'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''


def  calculate_anomalies_1to8_percentile(variable_split, variable, q):
    phase_mean = variable_split.groupby('phase').reduce(np.nanpercentile, q = q, dim = 'time')
    overall_mean = variable.reduce(np.nanpercentile, q = q, dim = 'time')
    anomalies = phase_mean/overall_mean
    
    return phase_mean, anomalies

'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''


def calculate_1to8_anomalies_for_variables(variable, anomaly_type = 'mean'):
    
    #Read in RMM
    rmm = load_rmm()
    
    # Split Via RMM
    variable_split = split_into_1to8(variable, rmm)
    
    # Calculate anomalies
    if anomaly_type == 'mean':
        variable_values, variable_anomalies = calculate_anomalies_1to8_mean(variable_split, variable)
    else:
        variable_values, variable_anomalies = calculate_anomalies_1to8_mean(variable_split, variable, anomaly_type) 
    
    
    return  variable_values, variable_anomalies



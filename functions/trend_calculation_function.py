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
import sys
from importlib import reload
sys.path.append('/home/563/ab2313/MJO/functions')
import mystats


def grid_trend(x,t):
    if np.all(np.isnan(x)):
        return float('nan')
    
    grad = np.polyfit(x,t,1)[0]
    return grad


def calculate_trend(percentile):
    

    # The axis number that year is
    axis_num = percentile.get_axis_num('year')
    
    '''Applying trends along each grid cell'''
    percenilte_trend_meta = np.apply_along_axis(grid_trend,axis_num, percentile.values, 
                                                t = percentile.year.values)

    '''Turning into an xarray dataset'''
    trend  = xr.Dataset(
        {'trend':(('phase','lat','lon'), percenilte_trend_meta)},

        {
        'phase':percentile.phase.values, 
         'lat':percentile.lat,
        'lon':percentile.lon}
    )
    
    
    
    return trend






def convert_to_percent_per_decade(percentile, trend):
    
    mean_gridcell = percentile.mean(dim = 'year')
    
    
    return (trend * 10 / mean_gridcell) * 100





def calculate_pvals(percentile, trend):
    year_num = percentile.get_axis_num('year')
    
    trend_pval_meta = np.apply_along_axis(mystats.mann_kendall, year_num, percentile)


    pvals  = xr.Dataset(
        {'pvals':(('phase','lat','lon'), trend_pval_meta)},

        {
        'phase':percentile.phase.values, 
         'lat':percentile.lat,
        'lon':percentile.lon}
    )
    
    
    return pvals




def significant_trend_cacl(data, pvals):
    sig = data.where(np.logical_and(pvals.pvals >= 0 ,pvals.pvals <= 0.05  ))
    

    return sig







def return_alltrendinfo(data,q):
    
    #Calculated the 90th percentile
    # The percentiles of each year. Maintains MJO splits
    percentile = data.groupby('time.year').reduce(np.nanpercentile, dim = 'time', q = q)
    
#     return percentile

#     Calculates the trend
    trend = calculate_trend(percentile)
    
    
    
    # Convertes to percent per decade
    trend_percent = convert_to_percent_per_decade(percentile, trend)
    
    # Calculates the significant values
    pvals =  calculate_pvals(percentile, trend)
    trend_sig = significant_trend_cacl(trend, pvals)
    trend_percent_sig = significant_trend_cacl(trend_percent, pvals)
    

    return percentile, trend, trend_sig, trend_percent, trend_percent_sig
    
    
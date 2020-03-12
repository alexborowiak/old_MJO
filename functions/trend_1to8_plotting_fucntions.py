

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

    
def plot_1to8_trends(data,variable = '', datasource = 'AWAP', vmax = 40, savefig = 0, savedir = '', step = 10, sig = 0, save_dir = ''):
            
       
    vmin = -vmax
    '''~~~~~~~~~~~~~~~~~'''
    if sig == 1:
        sig_title = '(Significant Points Only)'
    else:
        sig_title = ''
    fig  = plt.figure(figsize = (30, 12))
    gs = gridspec.GridSpec(4,3, hspace = 0.5, wspace = 0, height_ratios = [0.2, 1,1,1])
    title = f'{sig_title} {variable} Trend from {datasource}'
    fig.suptitle(title, fontsize = 35, y = 0.97)
    
    phases = np.append(np.arange(1,9),'inactive')

    '''~~~~~~~~~~~~~~~~~ ColorMap'''
#     cmap = plt.cm.RdBu
    n= vmax * 2 / step 
    cmap = plt.cm.get_cmap('RdBu', n)
    
 

    for i,phase in enumerate(phases):
       
        ax = fig.add_subplot(gs[i + 3], projection  = ccrs.PlateCarree())
  
        plot_data = data.sel(phase = str(phase))
         
        pdata = plot_data.plot(cmap  = cmap, vmin = vmin, vmax = vmax, add_colorbar = False)

        ax.outline_patch.set_visible(False)#Removing the spines of the plot. Cartopy requires different method
        ax.coastlines(resolution = '50m')
        ax.set_title('Phase ' + str(phase), size = 25)


    '''~~~~~ Colorbar'''
    axes = plt.subplot(gs[0,1:2])
    cbar = plt.colorbar(pdata,cax = axes, orientation = 'horizontal')
    cbar.ax.set_title('Trend (Percent Per Decade)', size = 25);
    int_ticks = np.arange(vmin,vmax + 10, 10)
    tick_labels = np.core.defchararray.add(int_ticks.astype('str')  , np.tile('%',len(int_ticks)));
    cbar.ax.set_xticklabels(tick_labels, fontsize = 20);
    
    
    if savefig:
        fig.savefig(save_dir + title + '.png', dpi = 400)
        print('!!!!!!!!  ' + title + '.png has been save to ' + save_dir)
        
##########################################################################################################################################################################################################################################################################


from matplotlib.colors import BoundaryNorm
import matplotlib.colors as mpc
import matplotlib.cm as cm



def plot_1to8_trends_contourf(data,variable = '', datasource = 'AWAP', vmax = 40, savefig = 0, savedir = ''):
            
       
    vmin = -vmax
    '''~~~~~~~~~~~~~~~~~'''
    fig  = plt.figure(figsize = (30, 12))
    gs = gridspec.GridSpec(4,3, hspace = 0.5, wspace = 0, height_ratios = [0.2, 1,1,1])
    title = f'Trend in {variable} from {datasource}'
    fig.suptitle(title, fontsize = 35, y = 0.97)
    
    phases = np.append(np.arange(1,9),'inactive')

    '''~~~~~~~~~~~~~~~~~ ColorMap'''
    n = 16
    cmap = plt.cm.get_cmap('RdBu', n)(np.arange(n))
    cmap = np.insert(cmap,int(len(cmap)/2), [1,1,1,1], axis = 0)
    cmap = np.insert(cmap,int(len(cmap)/2), [1,1,1,1], axis = 0)    
    cmap = np.insert(cmap,int(len(cmap)/2), [1,1,1,1], axis = 0)
    cmap = np.insert(cmap,int(len(cmap)/2), [1,1,1,1], axis = 0)
    cmap_custom_RdBu = mpc.LinearSegmentedColormap.from_list("RdWtBu", cmap, n ) # make it a new colourmap with new name 
#     cmap = cmap_custom_RdBu
    cmap = plt.cm.get_cmap('RdBu', n)
 

    for i,phase in enumerate(phases):
       
        ax = fig.add_subplot(gs[i + 3], projection  = ccrs.PlateCarree())
  
        plot_data = data.sel(phase = str(phase))
         
        pdata = ax.contourf(plot_data.lon,plot_data.lat, plot_data.values,15,cmap  = cmap, vmin = vmin, vmax = vmax)
        m = plt.cm.ScalarMappable(cmap = cmap)
        m.set_array(plot_data.values)
        m.set_clim(vmin,vmax)
        
        ax.outline_patch.set_visible(False)#Removing the spines of the plot. Cartopy requires different method
        ax.coastlines(resolution = '50m')
        ax.set_title('Phase ' + str(phase), size = 25)


    '''~~~~~ Colorbar'''
    axes = plt.subplot(gs[0,1:2])
    cbar = plt.colorbar(m,cax = axes, boundaries = np.linspace(vmin, vmax, 16), orientation = 'horizontal')
    cbar.ax.set_title('Trend (Percent Per Decade)', size = 25);
    tick_labels = np.core.defchararray.add(np.arange(vmin,vmax + 10, 10).astype('str')  , np.tile('%',9));
    cbar.ax.set_xticklabels(tick_labels, fontsize = 20);
    
    
    if savefig:
        fig.savefig(title + '.png', dpi = 400)
        
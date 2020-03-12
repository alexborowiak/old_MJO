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




'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   Splitting ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''




''' This file splits the MJO up into the 1 to 8 phases and also the inactive phase'''
def split_into_mjo_phases_1to8(datafile, rmm_xr):
    
    
    
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











'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   Anomaly Plots ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''

'''Basic plot of all the raw values'''

def plot_1to8(datafile):
    fig  = plt.figure(figsize = (16, 16))
    gs = gridspec.GridSpec(4,2, hspace = 0, wspace = 0)
    # gs.update(wspace=0.025, hspace=0.05)

    phases = np.arange(1,9)

    row = 0
    column = 0
    for phase in phases:
        data = datafile.sel(phase = str(phase)).mean(dim = 'time').drop('phase')
        ax = fig.add_subplot(gs[phase - 1], projection  = ccrs.PlateCarree())
        data.plot(ax = ax, add_colorbar = False, cmap = bm)
        ax.outline_patch.set_visible(False)#Removing the spines of the plot. Cartopy requires different method
        ax.coastlines(resolution = '50m')
        ax.set_title('Phase ' + str(phase), size = 15)

        column += 1

        if column == 4:
            column = 0
            row += 1
            
            
            
            
            
##########################################################################################################################################################################################################################################################################


'''Color Bar'''

from matplotlib.colors import BoundaryNorm
import matplotlib.colors as mpc
import matplotlib.cm as cm


n = 16
#symetrical blu rd colour map with white in centre
custom_RdBu = cm.get_cmap("RdBu",n)(np.arange(n)) # list of 20 colours
custom_RdBu[5] = [1,1,1,1] # for the nth colour change to white
custom_RdBu[6] = [1,1,1,1] # for the nth colour change to white
custom_RdBu[7] = [1,1,1,1] # for the nth colour change to white
custom_RdBu[8] = [1,1,1,1] # for the nth colour change to white
custom_RdBu[9] = [1,1,1,1] # for the nth colour change to white
cmap_custom_RdBu = mpc.LinearSegmentedColormap.from_list("RdWtBu", custom_RdBu, n) # make it a new colourmap with new name 

def difference_colorbar_horizontal(ax, comp_plot,vmin, vmax, orientation = 'horizontal'): # Note: can also be vertical now
    
    # These are the range of different locatins for ticks that I want
    tick_labels = np.array([0.33334, 0.5, 0.666666666,1, 1.5 , 2, 3 ]) 

    # The string version
    tick_strings = (np.array(['0.33', '0.5', '0.67','1', '1.5' , '2' , '3', ]).astype(float)).astype(str)
    
    # Finding the strings and labels in the range that I need
    tick_strings = tick_strings[np.where(np.logical_and(tick_labels <= vmax, tick_labels >= vmin))]
    tick_labels = tick_labels[np.where(np.logical_and(tick_labels <= vmax, tick_labels >= vmin))]
    
    # The actual plot
    cbar = plt.colorbar(comp_plot, cax = ax,orientation = orientation,drawedges = True, ticks = tick_labels)

    # Adding the strings as the tick labels
    if orientation == 'horizonal':
        cbar.ax.set_xticklabels(tick_strings)
        cbar.set_label('Change', fontsize = 15, labelpad = 10)  
    else:
        cbar.ax.set_yticklabels(tick_strings) 
        cbar.ax.set_title('Change', fontsize = 15, pad = 15) 

        
        
        
        
        
        
##########################################################################################################################################################################################################################################################################





def plot_1to8_anomalies_mean(data_split, data_total,
                        titlepiece = 'Mystery', datasource = 'AWAP', 
                        vmax = 40, savefig = 0, savedir = ''):
            
    '''~~~~~~~~~~~~~~~~~
    Dummy file to correct the error with colorf'''
    
    vmin = -vmax
    color_bar_file = xr.DataArray([[vmin, vmax],[vmin, vmax]], coords = [('lat',[-18,-19]), ('lon',[140,141])])
    color_bar_file

    '''~~~~~~~~~~~~~~~~~'''
    fig  = plt.figure(figsize = (30, 12))
    gs = gridspec.GridSpec(4,3, hspace = 0.5, wspace = 0, height_ratios = [0.2, 1,1,1])
    # gs.update(wspace=0.025, hspace=0.05)
    title = f'Percentage {titlepiece} Changes for Phases of the MJO in {datasource}'
    fig.suptitle(title, fontsize = 35, y = 0.97)
    phases = np.append(np.arange(1,9),'inactive')

    # cmap = cmap_test
    cmap = cmap_custom_RdBu
    bounds = np.arange(-30, 35, 5)
    bounds_2 = np.linspace(-30,30,160)

    norm = mpc.BoundaryNorm(bounds, cmap.N)

    
    '''Datafile mean'''

    data_total_mean = data_total.mean(dim = 'time')
    data_phase_mean  = data_split.groupby('phase').mean(dim = 'time')



    
    row = 0
    column = 0
    all_plot = []
    for i,phase in enumerate(phases):
       

        ax = fig.add_subplot(gs[i + 3], projection  = ccrs.PlateCarree())
    #     plot = data.plot(ax = ax,cmap = rb, add_colorbar = False)pcolormesh

    
        if phase == 'inactive': 
            # This is to fix the vmin, vmax issue. Doesn't seem to work in the colorbar. So just feeding in some
            # dummy data that doesn't actually appear in the plot
            plot = ax.contourf(color_bar_file.lat, color_bar_file.lon, color_bar_file.values, cmap  = cmap_custom_RdBu, norm = norm,
                           vmin = vmin, vmax = vmax, zorder = -100)
#             
            
            
        # THis is the mean of each phase
        data_phase_single_mean = data_phase_mean.sel(phase = str(phase)).drop('phase')
        # The mean of each phase minus the total mean, divided by the total mean
        plot_data = (data_phase_single_mean - data_total_mean)/ data_total_mean
        
        ax.contourf(plot_data.lon,plot_data.lat, plot_data.values,60,cmap  = cmap_custom_RdBu)
#                     norm = norm, vmin = vmin, vmax =vmax)
        ax.outline_patch.set_visible(False)#Removing the spines of the plot. Cartopy requires different method
        ax.coastlines(resolution = '50m')
        ax.set_title('Phase ' + str(phase), size = 25)

        column += 1

        if column == 4:
            column = 0
            row += 1


    '''~~~~~ Colorbar'''
    axes = plt.subplot(gs[0,1:2])
    # cbar = difference_colorbar_horizontal(axes, plot,vmin, vmax , orientation = 'horizontal')
    cbar = plt.colorbar(plot, cax=axes, orientation = 'horizontal')#,norm = norm)
    cbar.ax.set_title('Percent Difference From Mean', size = 25);
    tick_labels = np.core.defchararray.add(np.arange(-40,45, 10).astype('str')  , np.tile('%',9));
    cbar.ax.set_xticklabels(tick_labels, fontsize = 20);
    
    
    if savefig:
        fig.savefig(title + '.png', dpi = 400)
      
    
    
        
        ##########################################################################################################################################################################################################################################################################


def plot_1to8_anomalies_percentile(data_split, data_total, q = 50,
                        titlepiece = 'Mystery', datasource = 'AWAP', 
                        vmax = 40, savefig = 0, savedir = ''):
            
    '''~~~~~~~~~~~~~~~~~
    Dummy file to correct the error with colorf'''
    
    vmin = -vmax
    color_bar_file = xr.DataArray([[vmin, vmax],[vmin, vmax]], coords = [('lat',[-18,-19]), ('lon',[140,141])])
    color_bar_file

    '''~~~~~~~~~~~~~~~~~'''
    fig  = plt.figure(figsize = (30, 12))
    gs = gridspec.GridSpec(4,3, hspace = 0.5, wspace = 0, height_ratios = [0.2, 1,1,1])
    # gs.update(wspace=0.025, hspace=0.05)
    title = f'Percentage {titlepiece} Changes for Phases of the MJO in {datasource}'
    fig.suptitle(title, fontsize = 35, y = 0.97)
    phases = np.append(np.arange(1,9),'inactive')

    # cmap = cmap_test
    cmap = cmap_custom_RdBu
    bounds = np.arange(-30, 35, 5)
    bounds_2 = np.linspace(-30,30,160)

    norm = mpc.BoundaryNorm(bounds, cmap.N)

    
    '''Datafile mean'''

    data_total_mean = data_total.reduce(np.nanpercentile, q = q, dim = 'time')
    data_phase_mean  = data_split.groupby('phase').reduce(np.nanpercentile, q = q, dim = 'time')



    
    row = 0
    column = 0
    all_plot = []
    for i,phase in enumerate(phases):
       

        ax = fig.add_subplot(gs[i + 3], projection  = ccrs.PlateCarree())
    #     plot = data.plot(ax = ax,cmap = rb, add_colorbar = False)pcolormesh

    
        if phase == 'inactive': 
            # This is to fix the vmin, vmax issue. Doesn't seem to work in the colorbar. So just feeding in some
            # dummy data that doesn't actually appear in the plot
            plot = ax.contourf(color_bar_file.lat, color_bar_file.lon, color_bar_file.values, cmap  = cmap_custom_RdBu, norm = norm,
                           vmin = vmin, vmax = vmax, zorder = -100)
#             
            
            
        # THis is the mean of each phase
        data_phase_single_mean = data_phase_mean.sel(phase = str(phase)).drop('phase')
        # The mean of each phase minus the total mean, divided by the total mean
        plot_data = (data_phase_single_mean - data_total_mean)/ data_total_mean
        
        ax.contourf(plot_data.lon,plot_data.lat, plot_data.values,60,cmap  = cmap_custom_RdBu)
#                     norm = norm, vmin = vmin, vmax =vmax)
        ax.outline_patch.set_visible(False)#Removing the spines of the plot. Cartopy requires different method
        ax.coastlines(resolution = '50m')
        ax.set_title('Phase ' + str(phase), size = 25)

        column += 1

        if column == 4:
            column = 0
            row += 1


    '''~~~~~ Colorbar'''
    axes = plt.subplot(gs[0,1:2])
    # cbar = difference_colorbar_horizontal(axes, plot,vmin, vmax , orientation = 'horizontal')
    cbar = plt.colorbar(plot, cax=axes, orientation = 'horizontal')#,norm = norm)
    cbar.ax.set_title('Percent Difference From Mean', size = 25);
    tick_labels = np.core.defchararray.add(np.arange(-40,45, 10).astype('str')  , np.tile('%',9));
    cbar.ax.set_xticklabels(tick_labels, fontsize = 20);
    
    
    if savefig:
        fig.savefig(title + '.png', dpi = 400)
        
        
        
        
        

        
        
        

        
        
        
        
        
        
        
        
        
        
        

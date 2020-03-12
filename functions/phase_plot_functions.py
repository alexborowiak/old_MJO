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
'''~~~~~~~~~~~~~~~~~~~~~~RAW VALUE PLOTS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''

def upper_low_bound(vmin, vmax):
    
    low_mag = OrderOfMagnitude(vmin) * 10
    high_mag = OrderOfMagnitude(vmax) * 10
    
    
    upper_bound = np.ceil(vmax/high_mag) * high_mag
    lower_bound = np.floor(vmin/low_mag) * low_mag
    
    return lower_bound, upper_bound
    

def OrderOfMagnitude(number):
    import math
    mag = math.floor(math.log(number, 10))   
    if mag == 0:
        return 0.1
    else:
        return mag
     
    
def values_plots(datafile, title = '', cbar_title = '',cbar_num_steps = 10,  savefig = 0 , savedir = '',
                 cmap = plt.cm.Blues):
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    from matplotlib.colors import BoundaryNorm
    import matplotlib.colors as mpc

    vmax = datafile.reduce(np.nanpercentile, q= 90,dim = ['lon','lat','phase'])
    vmin = datafile.reduce(np.nanpercentile, q= 10,dim = ['lon','lat','phase'])
    
    lower_bound, upper_bound = upper_low_bound(vmin, vmax)
    
    if lower_bound == 1:
        lower_bound = 0

    fig = plt.figure(figsize = (24,12))
    gs = gridspec.GridSpec(4,3,hspace = 0.5, wspace = 0, height_ratios = [0.2, 1,1,1])
    fig.suptitle(title, fontsize = 35, y = 0.97)
    
    phases = np.append(np.arange(1,9),'inactive')
    

    bounds = np.linspace(lower_bound, upper_bound, cbar_num_steps )
    bounds = np.ceil(bounds)
  
    norm = BoundaryNorm(bounds, cmap.N)
    
    
    for i,phase in enumerate(phases):
       
        ax = fig.add_subplot(gs[i + 3], projection  = ccrs.PlateCarree())
    
        data = datafile.sel(phase = str(phase))
        
        pdata = data.plot(ax =ax,cmap = cmap, add_colorbar = False, vmin = lower_bound, vmax = upper_bound)

        #Removing the spines of the plot. Cartopy requires different method
        ax.outline_patch.set_visible(False)
        ax.coastlines(resolution = '50m')
        if phase == 'inactive':
            ax.set_title('Inactive Phase', size = 25)
        else:
            ax.set_title('Phase ' + str(phase), size = 25)
        
        '''~~~~~ Colorbar'''
    axes = plt.subplot(gs[0,1:2])
    cbar = plt.colorbar(pdata, cax=axes,boundaries = bounds, orientation = 'horizontal',extend = 'both')
    cbar.ax.set_title(cbar_title, size = 20);
    cbar.ax.set_xticklabels(bounds.astype(str), fontsize = 15)
    
    
    
    if savefig:
        fig.savefig(savedir + title + '.png', dpi = 400)
    
    
    
    
    
    
'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
'''~~~~~~~~~~~~~~~~~~~~~~ANOMALY PLOTS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''



def anomalie_cbar_1(vmax):
    import matplotlib as mpl
    
    if  vmax == 3:
        l1 = np.array([1.25,1.5,1.75,2,2.5,3])
    elif vmax == 2:
        l1 = np.array([1.2,1.4,1.6,1.8,2])
    elif vmax == 1.5:
        l1 = np.array([1.1,1.2,1.3,1.4,1.5])
    
    # The decimal values are the inverse of these values
    l2 = 1/l1 
    
    # Need to order them in the right direction
    l2 = np.flip(l2) 
    
    # Comining everything back together
    levels = np.concatenate((l2,np.array([1]),l1))
    
    # Creating a colorbar with the levels where you want them
    custom_RdBu = plt.cm.get_cmap("RdBu",len(levels))(np.arange(len(levels)))
    
    upper_mid = np.ceil(len(custom_RdBu)/2)
    lower_mid = np.floor(len(custom_RdBu)/2)
    white = [1,1,1,1]
    
    custom_RdBu[int(upper_mid)] = white
    custom_RdBu[int(lower_mid)] = white
    custom_RdBu[int(lower_mid) - 1] = white
    
#     middle = int(np.mean(len(custom_RdBu)/2))
#     for i in range(4):
#         custom_RdBu = np.insert(custom_RdBu,middle, [1,1,1,1], axis = 0)

    
    cmap_custom_RdBu = mpl.colors.LinearSegmentedColormap.from_list("RdWtBu", custom_RdBu,len(levels))
    
    return cmap_custom_RdBu, levels


'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''

def anomalie_cbar_2(cax, levels,vmax,pdata, cbar_title):
    
    tick_locations = levels
    # These are the range of different locatins for ticks that I want
#     tick_labels = np.array([0.33334, 0.5, 0.666666666,
#                             1, 1.5 , 2, 3 ])
#     tick_labels = np.array(tick_labels)
    # The string versin
    tick_strings = np.round(tick_locations,2).astype(str)
#     tick_strings = np.array([r'$ \dfrac{1}{3}$', r'$ \dfrac{1}{2}$', r'$ \dfrac{2}{3}$',
#                             '1', r'$\dfrac{3}{2}$' , '2' , '3' ])


    cbar = plt.colorbar(pdata, cax = cax,orientation = 'horizontal',
                        ticks = tick_locations)

    # Adding the strings as the tick labels
    
    cbar.ax.set_xticklabels(tick_strings, fontsize = 15) 
    cbar.ax.set_title(cbar_title,size = 20)
    
    
'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''    
    
def anomalies_plots(datafile,vmax = 3, title = '', cbar_title = '',cbar_num_steps = 10,  savefig = 0 , savedir = '',
                 cmap = plt.cm.Blues):
    
    assert vmax == 2 or vmax == 3 or vmax == 1.5
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    from matplotlib.colors import BoundaryNorm
    import matplotlib.colors as mpc


    fig = plt.figure(figsize = (24,12))
    gs = gridspec.GridSpec(4,3,hspace = 0.5, wspace = 0, height_ratios = [0.2, 1,1,1])
    fig.suptitle(title, fontsize = 35, y = 0.97)
    
    
    phases = np.append(np.arange(1,9),'inactive')

  
    custom_RdBu, levels = anomalie_cbar_1(vmax)
    vmin = 1/vmax

    for i,phase in enumerate(phases):
       
        ax = fig.add_subplot(gs[i + 3], projection  = ccrs.PlateCarree())
    
        data = datafile.sel(phase = str(phase))
        
#         data = data.fillna(1)
#         data = data.where(data > vmin, vmin)
#         data = data.where(data < vmax, vmax)
#         data = data.where(data != 1, np.nan)
        
        
        pdata = data.plot(ax = ax, cmap = custom_RdBu, 
                             vmin = vmin , vmax = vmax,
                             add_colorbar = False,
                             norm = BoundaryNorm(levels, len(levels)-1)) 

        #Removing the spines of the plot. Cartopy requires different method
        ax.outline_patch.set_visible(False)
        ax.coastlines(resolution = '50m')
        
        
        if phase == 'inactive':
            ax.set_title('Inactive Phase', size = 25)
        else:
            ax.set_title('Phase ' + str(phase), size = 25)
        
        '''~~~~~ Colorbar'''
    axes = plt.subplot(gs[0,1:2])
    anomalie_cbar_2(axes,levels,vmax, pdata, cbar_title)
    
    
    if savefig:
        fig.savefig(savedir + title + '.png', dpi = 400)
    

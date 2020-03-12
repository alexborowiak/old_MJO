
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import dask.array
import cartopy.crs as ccrs
import pickle
import matplotlib.colors as colors
import datetime as dt
rb = plt.cm.RdBu
bm = plt.cm.Blues
best_blue = '#9bc2d5'
recherche_red = '#fbc4aa'
wondeful_white = '#f8f8f7'


####################################################################################3##########################################3##########################################3##########################################3##########################################3##########################################3##########################################3##########################################3##########################################3##########################################3##########################################3##########################################3##########################################3##########################################3##########################################3##########################################3##########################################3


''' This is for plotting all trends'''

def trend_plot_single(data,cmap, vmax,vmin,title = '',save_fig = 0, dont_plot = 0):

    # Getting the right dimensions for both plots

    height = 10
    fig = plt.figure(figsize = (15,height))
    
    title_size = 15
    row_nums = 4
    fontsize = 15
    fig.suptitle(title, fontsize = 20)

    plot_num = 1
    ############################# Plots
    
    # Looping through all the phase: 'enhanced', 'suppressed','all'. 
    # These will be the rows
    for phase in data.mjo.values:
        



        sub_data = data.sel(mjo = phase)

        ax = fig.add_subplot(row_nums,1,plot_num, projection = ccrs.PlateCarree())
        plot = sub_data.plot(ax = ax,vmax = vmax,vmin = vmin, cmap = cmap, add_colorbar = False)
        plt.title(phase.capitalize())
        ax.set_extent([110,157, -7.5,-23])

        ax.coastlines(resolution = '50m')


        plot_num += 1   
        
    
    ### Adding a color bar
    
    
#     ticks= np.array([0.4,0.6,0.8,1,1.2,1.4,1.6,1.8,2])
#     tick_labels = [str(i) for i in ticks]
#     ticks = ticks - 0.05
#     boundaries = np.arange(0.1,vmax - step,step)
    
#     cax = fig.add_axes([.3, 0.92, 0.4,0.01]) # This is cax for a horizonal color bar
    cax = fig.add_axes([.7, 0.27,.01,0.4]) 
#     boundaries  = np.linspace(-vmax, vmax, 11)
    step = 5
    boundaries  = np.arange(-vmax, vmax + step, step)
    cbar = plt.colorbar(plot, orientation = 'vertical', cax = cax,
                       extend = 'both', boundaries = boundaries)
#     ticks = np.array(boundaries).astype(str)
#     ticks = [i + '%' for i in ticks]
#     cbar.ax.tick_params(labelsize = 10)
#     cbar.ax.set_yticklabels(ticks) 
    cbar.set_label('Percent Per \n Decade', fontsize = 12, labelpad = 28, rotation = 0)    
    

            
    
    
    
    #######
    fig.tight_layout(rect=[0, 0.03, 1, 0.93])

#####################
    #####
    if save_fig:
        fig.savefig(save_dir + title + '.png',bbox_inches = 'tight', dpi = 300)
        print('---' + title +  ' : has been saved')
        
        
        
    ####
    # This will not plot usefull if you just want to save
    if dont_plot:
        plt.close(fig)
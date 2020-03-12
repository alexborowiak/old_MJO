
'''This function takes a dat set then splits into the '''


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
import glob


############################################################################################################################################################################################################################################################################################################################################################################################################
def split_via_mjo(data, time_delta = 0):
    '''Set-up'''
    '''Reading in RMM'''

    path = '/g/data/w40/ab2313/RMM/RMM.pickle'
    pickle_in = open(path, 'rb')
    RMM = pickle.load(pickle_in)

    if time_delta:
        RMM = RMM.reset_index()
        RMM['Date'] = RMM['Date'] + pd.to_timedelta(str(time_delta) + 'h')
        RMM = RMM.set_index('Date')



    # The different regions and which phases are enhanced
    regions = np.array([slice(110, 120),slice(120.25, 140),slice(140.25, 156.25)])
    mjo_enhanced_list = np.array([[4,5],[4,5,6],[4,5,6,7]])

    enhanced_list = []
    suppressed_list = []
    inactive_list = []
    
    RMM = RMM.rename({'phase':'Phase','amplitude':'Amplitude'})
    
    
    ''''------Code
    1. Looping through the different regions
    2. Getting the enhanced phases for that region
    3. Getting the dates for enhanced, suppressed and inactive
    4. Gettting the data from the read-in file that mataches to those different regions
    5. Storing
    6. Combining all the regions back together and return'''
    
    
    '''1.'''
    # Three different regins to loop through: west, middle and east
    for reg_num in [0,1,2]:
        '''2.'''
        # Selecting just the values in that region
        region = regions[reg_num]
        data_region = data.sel(lon = region)

        # Selecting the phases that are enhanced and suppressed for that region
        mjo_enhanced = mjo_enhanced_list[reg_num] #enhanced
 
        '''3.'''
        # Getting just the dates for that phase: has to be in phases and have RMM >= 1
        enhanced_dates = np.array(RMM[np.logical_and(RMM['Phase'].isin(mjo_enhanced), 
                                                     RMM['Amplitude'] >= 1)].index)

        suppressed_dates = np.array(RMM[np.logical_and(~RMM['Phase'].isin(mjo_enhanced), 
                                                       RMM['Amplitude'] >= 1)].index)

        inactive_dates = np.array(RMM[RMM['Amplitude'] < 1].index)

        '''4.'''

        # Now getting an xarray file for the values just in that phase
        data_enhanced = data_region.where(data_region.time.isin(enhanced_dates))
        data_suppressed = data_region.where(data_region.time.isin(suppressed_dates))
        data_inactive  = data_region.where(data_region.time.isin(inactive_dates))
       
        
        '''5.'''
        # Appending to a list
        enhanced_list.append(data_enhanced)
        suppressed_list.append(data_suppressed)
        inactive_list.append(data_inactive)



    # Putting into xarray file
    enhanced_data_tot= xr.concat(enhanced_list, dim = 'lon')
    suppressed_data_tot = xr.concat(suppressed_list, dim = 'lon')
    inactive_data_tot = xr.concat(inactive_list, dim = 'lon')
    
    
#     enhanced_data_tot = (enhanced_list[0].combine_first(enhanced_list[1])).combine_first(enhanced_list[2])
#     suppressed_data_tot = (suppressed_list[0].combine_first(suppressed_list[1])).combine_first(suppressed_list[2])
#     inactive_data_tot = (inactive_list[0].combine_first(inactive_list[1])).combine_first(inactive_list[2])

    # Total Xarray File

    '''6.'''
    xr_file = xr.concat([enhanced_data_tot, suppressed_data_tot, inactive_data_tot, data]
                        , pd.Index(['enhanced','suppressed','inactive','all' ], name = 'mjo'))

    return xr_file




    
############################################################################################################################################################################################################################################################################################################################################################################################################

'''This is the same as the funciton above with two major differences.
1. This is built for files that have ensemble
2. The rmm is now taken in as an xarray file (rmm also have ensembles)'''



''''------Code
0. Looping through ensemble
1. Looping through the different regions
2. Getting the enhanced phases for that region
3. Getting the dates for enhanced, suppressed and inactive
4. Gettting the data from the read-in file that mataches to those different regions
5. Storing
6. Combining all the regions back together and return'''
    

def split_via_mjo_ensemble(data_total, rmm):
    enhanced_ens_stor = []
    suppressed_ens_stor = []
    inactive_ens_stor = []


    regions = np.array([slice(110, 120),slice(120.25, 140),slice(140.25, 156.25)])
    mjo_enhanced_list = np.array([[4,5],[4,5,6],[4,5,6,7]])

    
    '''0. Ensemble Loop'''
    for ensemble in data_total.ensemble.values:
        
        # Selecting single ensembles from our data files
        data = data_total.sel(ensemble = ensemble)
        rmm_single = rmm.sel(ensemble = ensemble)


        enhanced_list = []
        suppressed_list = []
        inactive_list = []

        '''0. Region Loop'''
        for reg_num in [0,1,2]:

            
            '''2. Getting the enhanced phases for that region'''
            mjo_enhanced = mjo_enhanced_list[reg_num]
            region = regions[reg_num]
            data_region = data.sel(lon = region)
            
            '''3. Getting the dates for enhanced, suppressed and inactive'''
            enhanced_dates = rmm.where(np.logical_and(rmm_single.phase.isin(mjo_enhanced),rmm_single.amplitude >= 1),
                                       drop = True).time

            suppressed_dates = rmm.where(np.logical_and(~rmm_single.phase.isin(mjo_enhanced),rmm_single.amplitude >= 1),
                                       drop = True).time

            inactive_dates = rmm.where(rmm_single.amplitude < 1,
                                       drop = True).time
            
            '''4. Gettting the data from the read-in file that mataches to those different regions'''
            data_enhanced = data_region.where(data_region.time.isin(enhanced_dates), drop = True)
            data_suppressed = data_region.where(data_region.time.isin(suppressed_dates), drop = True)
            data_inactive = data_region.where(data_region.time.isin(inactive_dates), drop = True)


            '''5. Storing'''
            # Appending to a list
            enhanced_list.append(data_enhanced)
            suppressed_list.append(data_suppressed)
            inactive_list.append(data_inactive)

        '''6. Concating back into a complete file'''    
        enhanced_data_tot= xr.concat(enhanced_list, dim = 'lon')
        suppressed_data_tot = xr.concat(suppressed_list, dim = 'lon')
        inactive_data_tot = xr.concat(inactive_list, dim = 'lon')   


        enhanced_ens_stor.append(enhanced_data_tot)
        suppressed_ens_stor.append(suppressed_data_tot)
        inactive_ens_stor.append(inactive_data_tot)



    enhanced_total = xr.concat(enhanced_ens_stor, pd.Index(np.arange(1,12), name = 'ensemble'))
    suppressed_total = xr.concat(suppressed_ens_stor, pd.Index(np.arange(1,12), name = 'ensemble'))
    inactive_total = xr.concat(inactive_ens_stor, pd.Index(np.arange(1,12), name = 'ensemble'))




    total = xr.concat([enhanced_total, suppressed_total, inactive_total, data_total], 
                     pd.Index(['enhanced','suppressed','inactive','all'], name = 'mjo'))
    
    return total




############################################################################################################################################################################################################################################################################################################################################################################################################
############################################################################################################################################################################################################################################################################################################################################################################################################

'''
The idea of this function is to return a data set that is full of values above a certain threshold

1. Getting the climatology
2. Looping through the months
3. Selecting a single month, then getting the values above the climatology for that month
4. Combing back into a single data set
'''
def return_monthly_extremes(data, q, months = [10,11,12,1,2,3]):
    
    
    '''1. '''
    climatology = data.groupby('time.month').reduce(np.nanpercentile, q =q, dim = 'time')
    
    '''2. '''
    
    
    for i,month in enumerate(months):
        '''3. '''
        data_month = data.where(data.time.dt.month == month, drop = True)
        climatology_month = climatology.sel(month = month)
        
        data_month_ex = data_month.where(data_month >= climatology_month)
        
        '''4. '''
        if i == 0:
            extreme_xr = data_month_ex
        else:
            extreme_xr = extreme_xr.combine_first(data_month_ex)
            
        print('month ' + str(month) + ' - completed' )
    
    return  extreme_xr
    
############################################################################################################################################################################################################################################################################################################################################################################################################
############################################################################################################################################################################################################################################################################################################################################################################################################
def count_anomalies(extremes, normal, per):
    
    extreme_count = extremes.groupby('time.month').count(dim = 'time')
    normal_count = normal.groupby('time.month').count(dim = 'time')
    
    
    anomaly = extreme_count/normal_count
    anomal = anomaly /per
    
    return anomly
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    




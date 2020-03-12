import xarray as xr
import cdsapi
import pandas as pd




c = cdsapi.Client()

years = [
            '1979','1980','1981',
            '1982','1983','1984',
            '1985','1986','1987',
            '1988','1989','1990',
            '1991','1992','1993',
            '1994','1995','1996',
            '1997','1998','1999',
            '2000','2001','2002',
            '2003','2004','2005',
            '2006','2007','2008',
            '2009','2010','2011',
            '2012','2013','2014',
            '2015','2016','2017',
            '2018'
        ]


year_stor = []


for year in years:


    ####################################
    c.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type':'reanalysis',
        'variable':'total_column_water',
        'year':year,
        'month':[
            '01','02','03',
            '10','11','12'
        ],
        'day':[
            '01','02','03',
            '04','05','06',
            '07','08','09',
            '10','11','12',
            '13','14','15',
            '16','17','18',
            '19','20','21',
            '22','23','24',
            '25','26','27',
            '28','29','30',
            '31'
        ],
        'time':[
            '00:00','01:00','02:00',
            '03:00','04:00','05:00',
            '06:00','07:00','08:00',
            '09:00','10:00','11:00',
            '12:00','13:00','14:00',
            '15:00','16:00','17:00',
            '18:00','19:00','20:00',
            '21:00','22:00','23:00'
        ],
        'format':'netcdf'
    },
        'year_meta.nc')
    ####################################

    c.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type':'reanalysis',
        'variable':'total_column_water',
        'year':str(int(year) + 1),
        'month':'01',
        'day':'01',
        'time':[
            '00:00','01:00','02:00',
            '03:00','04:00','05:00',
            '06:00','07:00','08:00'
        ],
        'format':'netcdf'
    },
    'additional_meta.nc')




    ####################################

    # The first dat set is the year in question

    # The second data set is the first 8 hours of the next year. This is because I am taking the 9am to
    # 9am average. This means I need the first 8 hours e.g 00:00 to 08:00.
    data = xr.open_dataset('year_meta.nc')
    data_2 = xr.open_dataset('additional_meta.nc')

    data = data.combine_first(data_2)

    #####
    #Only need the region for Australia, these below are the bounds that I have for AWAP
    data = data.sel(latitude = slice(-10, -23), longitude = slice(112, 156.25))

    # Subsetting the time and subtracting 9 hours so that I am getting the 9am to 9am mean
    end = data.time.values[-1] # This is only needed as I need to specify and end
    # Selecting the first 9am, this ensure that I don't go back into the previos year
    data = data.sel(time = slice(year + '-01-01T09:00:00.000000000',end))
    data['time'] = data.time.values - pd.to_timedelta('9h')

    # This gets the mean of all days
    data = data.resample('D', dim = 'time', how = 'mean')

    # Dropping anything that has gone outside the year in question
    data = data.where(data.time.dt.year == year, drop = True)

    # Storing the results so I can later combine_firest into an xarray file
    year_stor.append(data)



####################################3

for i in range(len(year_stor)):
    if i == 0:
        era5 = year_stor[i]
    else:
        era5.combine_first(year_stor[i])



era5.to_netcdf('/home/student.unimelb.edu.au/aborowiak/Desktop/Code/Scripts/big_files/era_5.nc')

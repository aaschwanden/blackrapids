#!/usr/bin/env python
#
#
# Copyright (C) 2013 Andy Aschwanden, University of Alaska Fairbanks

from argparse import ArgumentParser
import numpy as np
import pandas as pa
from pyproj import Proj
import datetime
    
def read_file(filename, tz_data='UTC', tz_local='US/Alaska', **kwargs):
    '''
    Read CSV (comma-separated) file into DataFrame. Try to remove empty columns.
    Calculate easting, northing, and elevation from (Target - Station).
    Calculate slope distance (Euklidian  distance).
    Any **kwargs are passed to pandas.read_csv to fine-tune the import.

    Arguments:

      *fname*:
        A string containing a path to a filename to a CSV (comma-separated value).

    Keyword Arguments:

      *tz_data*: [*UTC* | ``other valid time zone descriptions``]
        The time zone of the data.
        
      *tz_local*: [*US/Alaska* | ``other valid time zone descriptions``]
        The time zone in which you want to analyze the data.
        
    Returns:

      *df* : pandas.DataFrame

    Example:
    
    By default, the data time zone is 'UTC' and the local time zone is 'US/Alaska':
    
    df = read_file('mydata.csv')
    
    Assume you have data in file 'mydata.csv', and the time zone of the data
    is 'US/Eastern', but you want to analyze the data in your time zone 'UTC':

    df = read_file('mydata.csv', tz_data='US/Eastern', tz_local='UTC')
    '''

    df = pa.read_csv(filename, **kwargs)
    ## ts = pa.DatetimeIndex(df[attr], tz=tz_data)    
    ts = pa.DatetimeIndex(df['Time']) 
    
    # Assing time series as index
    ## df.index = ts.tz_convert(tz_local)
    df.index = ts
    del df['Time']
    return df



# Set up the argument parser
parser = ArgumentParser()
parser.description = '''A script to add lat/lon coordinates based on GPS marker.'''
parser.add_argument("FILE", nargs='*')
parser.add_argument("--latlon", dest="latlon", nargs=2, type=float,
                  help="latitude and longitude of target", default=None)
options = parser.parse_args()
inname = options.FILE[0]
outname = options.FILE[1]
lat0, lon0 = options.latlon

df = read_file(inname)
df = df.dropna()

p = Proj(init="EPSG:3338")

x0, y0 = p(lon0, lat0)

idx = df['easting'].first_valid_index()
x = x0 + (df['easting'] - df['easting'][idx])
idx = df['northing'].first_valid_index()
y = y0 + (df['northing'] - df['northing'][idx])
    
df['lon'], df['lat'] = p(x, y, inverse=True)
nt = len(df['easting'])

df['easting'] = x
df['northing'] = y

hours_since_start = []
for m,my_time in enumerate(df.index):
    diff = df.index[m] - pa.datetime(2013,6,24,0,0,0)
    hours_since_start.append(diff.total_seconds()/(3600.))
df['idx'] = hours_since_start

# there is a bug in pandas 0.11 (but fixed in 0.12) which screws up columns when doing:
## df.to_csv(outname, cols=['idx', 'lon', 'lat', 'elevation', 'easting', 'northing'], index_label='Time')
# so we do this instead:
df[['idx', 'lon', 'lat', 'elevation', 'easting', 'northing']].to_csv(outname, index_label='Time')




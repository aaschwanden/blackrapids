#!/usr/bin/env python
#
#
# Copyright (C) 2013 Andy Aschwanden, University of Alaska Fairbanks

from argparse import ArgumentParser
import numpy as np
import pandas as pa
from pyproj import Proj
import datetime
    


# Set up the argument parser
parser = ArgumentParser()
parser.description = '''A script to add lat/lon coordinates based on GPS marker.'''
parser.add_argument("FILE", nargs='*')
options = parser.parse_args()
inname = options.FILE[0]
outname = options.FILE[1]

df = pa.read_csv(inname)
ts = pa.DatetimeIndex(df['Time'])    
# Assing time series as index
df.index = ts

# a datetime before the shift used to calculate average displacement, in UTC
avg_date = '2013-06-27 01:48:29'
before_shift = '2013-06-27 03:04:17'
after_shift = '2013-06-27 03:19:07'

dt_total = (pa.to_datetime(before_shift) - pa.to_datetime(avg_date)).total_seconds()
dt_step = (pa.to_datetime(after_shift) - pa.to_datetime(before_shift)).total_seconds()

de = (df['Target Easting [m]'][before_shift] - df['Target Easting [m]'][avg_date]) / dt_total * dt_step
dn = (df['Target Northing [m]'][before_shift] - df['Target Northing [m]'][avg_date]) / dt_total * dt_step
dh = (df['Target Elevation [m]'][before_shift] - df['Target Elevation [m]'][avg_date]) / dt_total * dt_step

df['Target Easting [m]'][:before_shift]  = df['Target Easting [m]'][:before_shift] + (df['Target Easting [m]'][after_shift]-df['Target Easting [m]'][before_shift]) - de
df['Target Northing [m]'][:before_shift]  = df['Target Northing [m]'][:before_shift] + (df['Target Northing [m]'][after_shift]-df['Target Northing [m]'][before_shift]) - dn
df['Target Elevation [m]'][:before_shift]  = df['Target Elevation [m]'][:before_shift] + (df['Target Elevation [m]'][after_shift]-df['Target Elevation [m]'][before_shift]) - dh

df.to_csv(outname, index_label='Time')

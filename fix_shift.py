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
parser.add_argument("--avg_date",dest="avg_date",
                  help='''A datetime a few measurements before the shift, for averaging, in UTC''',
                  default='2013-06-27 01:48:29')
parser.add_argument("--before_date",dest="before_date",
                  help='''The datetime before the shift in UTC''',
                  default='2013-06-27 03:04:17')
parser.add_argument("--after_date",dest="after_date",
                  help='''The datetime after the shift in UTC''',
                  default='2013-06-27 03:19:07')
options = parser.parse_args()
inname = options.FILE[0]
outname = options.FILE[1]
avg_date = options.avg_date
before_date = options.before_date
after_date = options.after_date

df = pa.read_csv(inname)
ts = pa.DatetimeIndex(df['Time'])    
# Assing time series as index
df.index = ts
del df['Time']

dt_total = (pa.to_datetime(before_date) - pa.to_datetime(avg_date)).total_seconds()
dt_step = (pa.to_datetime(after_date) - pa.to_datetime(before_date)).total_seconds()

de = (df['Target Easting [m]'][before_date] - df['Target Easting [m]'][avg_date]) / dt_total * dt_step
dn = (df['Target Northing [m]'][before_date] - df['Target Northing [m]'][avg_date]) / dt_total * dt_step
dh = (df['Target Elevation [m]'][before_date] - df['Target Elevation [m]'][avg_date]) / dt_total * dt_step

df['Target Easting [m]'][:before_date]  = df['Target Easting [m]'][:before_date] + (df['Target Easting [m]'][after_date]-df['Target Easting [m]'][before_date]) - de
df['Target Northing [m]'][:before_date]  = df['Target Northing [m]'][:before_date] + (df['Target Northing [m]'][after_date]-df['Target Northing [m]'][before_date]) - dn
df['Target Elevation [m]'][:before_date]  = df['Target Elevation [m]'][:before_date] + (df['Target Elevation [m]'][after_date]-df['Target Elevation [m]'][before_date]) - dh

df.to_csv(outname, index_label='Time')

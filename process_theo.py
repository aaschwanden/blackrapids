#!/usr/bin/env python
#
#
# Copyright (C) 2013 Andy Aschwanden, University of Alaska Fairbanks

from argparse import ArgumentParser
import numpy as np
import pylab as plt
import matplotlib.gridspec as gridspec
from matplotlib import colors
import matplotlib
import pandas as pa


def create_dictionary(options):
    '''
    Return a dictionary with pandas.DataFrame from options.
    '''

    args = options.FILE
    reference_file = options.reference_file
    resample_rule = options.resample_rule
    # If a reference file was given via --reference_file reference.csv
    # then read reference file.
    if reference_file:
        print('Reading reference file %s' % reference_file)
        reference_df = read_file(reference_file)

    my_dict = {}
    for my_file in args:
        print('Reading file %s' % my_file)
        df = read_file(my_file)
        key = df['Point ID'][0]
        # If a reference file was given via --reference_file reference.csv
        # then first resample to new rate to create a common time axis, and
        # second subtract reference values.
        # TODO: check resampling options.
        if reference_file:
            reference_df_s = reference_df.resample(resample_rule, how='mean', fill_method='ffill', limit=0)
            df_s = df.resample(resample_rule, how='mean', fill_method='ffill', limit=0)
            # The theodolite is on the morraine, and thus moving. We need to subtract the reference
            # from the fixed target.
            my_dict[key] = df_s - reference_df_s
        else:
            my_dict[key] = df
        fname = key.lower() + '_ref.csv'
        # Time stamp is in local time zone!
        my_dict[key].to_csv(fname, cols=['easting', 'northing'], index_label='Time Stamp')

    return my_dict

    
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
    # Remove empty columns
    unused_variables = ('Vel Limit Diff [m]', 'Profile Name')
    for key in unused_variables:
        if hasattr(df, key):
            del df[key]

    # Create a time series from 'Time'
    ## ts = pa.DatetimeIndex(df['Time'], tz=tz_data)
    ## df.index = ts.tz_convert(tz_local)
    # Time zone support doesn't work when plotting with pylab.plot_date, it is ignored.
    # We thus shift the time zone by hand: UTC - Alaska = -8 hours
    # TODO: calculate time shift automatically from supplied time zones
    for attr in ('Unnamed: 0', 'Time Stamp', 'Time'):
        if hasattr(df, attr):
            ## ts = pa.DatetimeIndex(df[attr], tz=tz_data)    
            ts = pa.DatetimeIndex(df[attr]) + pa.DateOffset(hours=-8)
    # Assing time series as index
    df.index = ts

    # Calculate easting, northing, and elevation from (Target - Station)
    df['easting'] = (df['Target Easting [m]'] - df['Station Easting [m]'])
    df['northing'] = (df['Target Northing [m]'] - df['Station Northing [m]'])
    df['elevation'] = (df['Target Elevation [m]'] - df['Station Height [m]'])
    # Calculate Euklidian distance (called slope distance in Leica software)
    df['slope_distance'] = np.sqrt(df['easting']**2 + df['northing']**2 + df['elevation']**2)

    return df


def add_inner_title(ax, title, loc, size=None, **kwargs):
    '''
    Adds an inner title to a given axis, with location loc.

    from http://matplotlib.sourceforge.net/examples/axes_grid/demo_axes_grid2.html
    '''

    from matplotlib.offsetbox import AnchoredText
    from matplotlib.patheffects import withStroke
    if size is None:
        size = dict(size=plt.rcParams['legend.fontsize'])
    at = AnchoredText(title, loc=loc, prop=size,
                      pad=0., borderpad=0.5,
                      frameon=False, **kwargs)
    ax.add_artist(at)
    return at


def colorList():

    '''
    Returns a list with colors, e.g for line plots. etc.
    '''
    colors = ['#084594',  # dark blue
              '#FF7F00',  # orange
              '#984EA3',  # violet
              '#E41A1C',  # red
              '#4DAF4A',  # green
              '#377EB8',  # light blue
              '#FB9A99',  # light red
              '#FB9A99',  # light orange
              '#CAB2D6',  # light violet
              'brown',
              'pink',
              'grey',
              'black']
    return colors


def plot_ts(my_dict, fname, start_date=None, end_date=None):
    '''
    Plot time-series of easting and northing.

    Parameters:

      *my_dict*:
        A dictionary with (key, value) = ('Station', pandas.DataFrame).

      *fname*:
        A string containing a path to a filename to a CSV (comma-separated value).
        
    Keyword Arguments:

      *start_date*: [*None*, ``date string``]
        Define start date of plot as a date string like '6/27/2013 8:00'.
        
      *end_date*: [*None*, ``date string``]
        Define end date of plot as a date string like '6/29/2013 8:00'.
    '''

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111)
    for k, key in enumerate(my_dict.keys()):
        if start_date is None:
            start_date = my_dict[key].index[0]
        if end_date is None:
            end_date = my_dict[key].index[-1]
        my_item = my_dict[key].truncate(before=start_date, after=end_date)

        var = 'easting'
        my_dates = my_item.index.to_pydatetime()
        first_valid_index = my_item[var].first_valid_index()
        var_values = my_item[var] - my_item[var][first_valid_index]
        ax.plot_date(my_dates, var_values, my_markers[0], color=my_colors[k], label=key)
        var = 'northing'
        my_dates = my_item.index.to_pydatetime()
        first_valid_index = my_item[var].first_valid_index()
        var_values = my_item[var] - my_item[var][first_valid_index]
        ax.plot_date(my_dates, var_values, my_markers[1], color=my_colors[k])
    hourFormatter = matplotlib.dates.DateFormatter('%m-%d %H:%M')
    hours    = matplotlib.dates.HourLocator(interval=6)
    ax.xaxis.set_major_formatter(hourFormatter)
    ax.xaxis.set_major_locator(hours)
    ax.set_xlabel('date [AKST]')
    ax.legend(numpoints=1)
    ticklabels = ax.get_xticklabels()
    for tick in ticklabels:
        tick.set_rotation(30)
    plt.savefig(fname, dpi=dpi)


def plot_easting_northing_elevation(my_dict, fname, start_date=None, end_date=None):
    '''
    Plot with 3 subplots: easting, northing, and elevation.

    Parameters:

      *my_dict*:
        A dictionary with (key, value) = ('Station', pandas.DataFrame).

      *fname*:
        A string containing a path to a filename to a CSV (comma-separated value).
        
    Keyword Arguments:

      *start_date*: [*None*, ``date string``]
        Define start date of plot as a date string like '6/27/2013 8:00'.
        
      *end_date*: [*None*, ``date string``]
        Define end date of plot as a date string like '6/29/2013 8:00'.
    '''
    
    variables = ('easting', 'northing', 'elevation')
    n_vars = len(variables)
    fig = plt.figure(figsize=(16,12))
    gs = gridspec.GridSpec(n_vars, 1, hspace=0.1)

    for m,var in enumerate(variables):
        ax = fig.add_subplot(gs[m])
        for k, key in enumerate(my_dict.keys()):
            if start_date is None:
                start_date = my_dict[key].index[0]
            if end_date is None:
                end_date = my_dict[key].index[-1]
            my_item = my_dict[key].truncate(before=start_date, after=end_date)
            my_dates = my_item.index.to_pydatetime()
            first_valid_index = my_item[var].first_valid_index()
            var_values = my_item[var] - my_item[var][first_valid_index]
            ax.plot_date(my_dates, var_values, 'o',
                color=my_colors[k], label=key, tz=my_tz)
        ax.set_ylabel(var)
        hourFormatter = matplotlib.dates.DateFormatter('%m-%d %H:%M')
        hours    = matplotlib.dates.HourLocator(interval=6)
        ax.xaxis.set_major_formatter(hourFormatter)
        ax.xaxis.set_major_locator(hours)
        if (m < n_vars-1):
            plt.setp(ax, xticks=[])
        else:
            ax.set_xlabel('date [AKST]')
            leg = ax.legend(numpoints=1, loc=4)
        ticklabels = ax.get_xticklabels()
        for tick in ticklabels:
            tick.set_rotation(30)
        ax.grid(axis='x')
    plt.savefig(fname, dpi=dpi)

    
def plot_mapplane_ts(my_dict, fname, start_date=None, end_date=None):
    '''
    Scatter plot colored with time.

    Parameters:

      *my_dict*:
        A dictionary with (key, value) = ('Station', pandas.DataFrame).

      *fname*:
        A string containing a path to a filename to a CSV (comma-separated value).
        
    Keyword Arguments:

      *start_date*: [*None*, ``date string``]
        Define start date of plot as a date string like '6/27/2013 8:00'.
        
      *end_date*: [*None*, ``date string``]
        Define end date of plot as a date string like '6/29/2013 8:00'.
    '''

    n_plots = len(my_dict.keys())
    n_rows = 3
    if (n_plots % n_rows == 0):
        n_cols = n_plots / n_rows
    else:
        n_cols = n_plots / n_rows + 1

    fig = plt.figure(figsize=(18, 12))
    gs = gridspec.GridSpec(n_rows, n_cols, hspace=0.6, wspace=0.2)
    for k, key in enumerate(my_dict.keys()):
        if start_date is None:
            start_date = my_dict[key].index[0]
        if end_date is None:
            end_date = my_dict[key].index[-1]
        my_item = my_dict[key].truncate(before=start_date, after=end_date)
        start_time = my_item.index[0]
        seconds_since_start = []
        for m,my_time in enumerate(my_item.index):
            diff = my_item.index[m] - start_time
            seconds_since_start.append(diff.total_seconds())

        ax = plt.subplot(gs[k])
        date_ticks = np.array(seconds_since_start) / 3600
        cax = ax.scatter(my_item['easting'], my_item['northing'], s=200, c=date_ticks, marker='.')
        ax.set_xlabel('easting [m]')
        ax.set_ylabel('northing [m]')
        plt.title(key)
        cbar = fig.colorbar(cax)
        if n_plots > 6:
                cbar.set_label('hours')
        else:
                cbar.set_label('hours since %s' % start_time.ctime())

    plt.savefig(fname, dpi=dpi)


def plot_slope_distance(my_dict, fname, start_date=None, end_date=None):
    '''
    Plot slope distance.

    Parameters:

      *my_dict*:
        A dictionary with (key, value) = ('Station', pandas.DataFrame).

      *fname*:
        A string containing a path to a filename to a CSV (comma-separated value).
        
    Keyword Arguments:

      *start_date*: [*None*, ``date string``]
        Define start date of plot as a date string like '6/27/2013 8:00'.
        
      *end_date*: [*None*, ``date string``]
        Define end date of plot as a date string like '6/29/2013 8:00'.
    '''
    
    n_plots = len(project_dict)
    fig = plt.figure(figsize=(16,10))
    ax = fig.add_subplot(111)
    for k,key in enumerate(project_dict.keys()):
        if start_date is None:
            start_date = my_dict[key].index[0]
        if end_date is None:
            end_date = my_dict[key].index[-1]
        my_item = my_dict[key].truncate(before=start_date, after=end_date)
        slope_distance = my_item['slope_distance'] - my_item['slope_distance'][0]
        ax.plot_date(my_item.index.to_pydatetime(), slope_distance, 'o',
            color=my_colors[k], label=key)
    ax.legend(numpoints=1, loc=0)
    ax.set_xlabel('date [AKST]')
    ax.set_ylabel('slope distance [m]')
    hourFormatter = matplotlib.dates.DateFormatter('%m-%d %H:%M')
    hours    = matplotlib.dates.HourLocator(interval=6)
    ax.xaxis.set_major_formatter(hourFormatter)
    ax.xaxis.set_major_locator(hours)

    ticklabels = ax.get_xticklabels()
    for tick in ticklabels:
        tick.set_rotation(30)

    plt.savefig(fname, dpi=dpi)

# Set up the argument parser
parser = ArgumentParser()
parser.description = '''A script to read TM30 theodolite data from Olga.'''
parser.add_argument("FILE", nargs='*')
parser.add_argument("--reference_file",dest="reference_file",
                  help='''File with reference time-series from a fixed station. Default is None''',
                  default=None)
parser.add_argument("--resample_rule",dest="resample_rule",
                  help='''Resample to new frequency. Only has an effect if reference_file is given. See pandas documentation for valid rules. Default is '5Min.' ''',
                  default='5Min')

options = parser.parse_args()
# Set up options
dpi = 150
my_colors = colorList()
my_markers = ('.', 'x', 'o')
my_tz = 'US/Alaska'
    
# Create a dictionary containing pandas.DataFrame instances.
project_dict = create_dictionary(options)

plot_slope_distance(project_dict, 'slope_distance_full.png')
plot_slope_distance(project_dict, 'slope_distance_drainage.png',
                    start_date='6/27/2013', end_date='6/28/2013')
plot_easting_northing_elevation(project_dict, 'ts_ene_full.png')
plot_easting_northing_elevation(project_dict, 'ts_ene_drainage.png',
                                     start_date='6/27/2013', end_date='6/28/2013')
plot_mapplane_ts(project_dict, 'mapplane_full.png')
plot_mapplane_ts(project_dict, 'mapplane_drainage.png',
                 start_date='6/27/2013', end_date='6/28/2013')

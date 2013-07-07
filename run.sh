#!/bin/bash


# rough positions of the reflectors, take from hand-held GPS at
# various points in time:

# BO2			BR1	63.478283 -146.299783
# BRMID 		BR2	63.479333 -146.320000
# BO1		    	BR3	63.479816 -146.329233
# BRMAIN		BR4	63.480583 -146.342650
# BRIE			BR5 63.478366 -146.292933
# WALD		BR6 63.478583 -146.307616
# PARM		BR7 63.475066 -146.306983
# FIX			FIX  63.469583 -146.339750
#LOK-DOWN	LK1 63.469833 -146.295166
# LK2		    	LK2 63.469816 -146.301850
# LK3 			LK3 63.468766 -146.307733
# LK4			LK4 63.466250 -146.318283
# LK-SOUTH	LK5 63.464000 -146.316416
# THEO		       63.474116 -146.307683


# The FIX reflector was moved on 2013-06-26 between 19:04 and 19:19 AKST,
# run fix_shift.py to remove the shifted
./fix_shift.py fix.csv fix_shifted.csv
# Proccess all stations excecpt THEO with respect to FIX, this produces
# the reference files _ref.csv
./process_theo.py --reference_file fix_shifted.csv br?.csv lk?.csv
# Process THEO
./process_theo.py fix_shifted.csv

# Turn relative easting/northing into absolute coordinates using approximate
# stake positions. Both lat/lon and easting/northing (EPSG:3467) are saved.
./add_absolute_coordinates.py --latlon 63.478283 -146.299783 br1_ref.csv br1_abs.csv
./add_absolute_coordinates.py --latlon 63.479333 -146.320000 br2_ref.csv br2_abs.csv
./add_absolute_coordinates.py --latlon 63.479816 -146.329233 br3_ref.csv br3_abs.csv
./add_absolute_coordinates.py --latlon 63.480583 -146.342650 br4_ref.csv br4_abs.csv
./add_absolute_coordinates.py --latlon 63.478366 -146.292933 br5_ref.csv br5_abs.csv
./add_absolute_coordinates.py --latlon 63.478583 -146.307616 br6_ref.csv br6_abs.csv
./add_absolute_coordinates.py --latlon 63.475066 -146.306983 br7_ref.csv br7_abs.csv
./add_absolute_coordinates.py --latlon 63.469833 -146.295166 lk1_ref.csv lk1_abs.csv
./add_absolute_coordinates.py --latlon 63.469816 -146.301850 lk2_ref.csv lk2_abs.csv
./add_absolute_coordinates.py --latlon 63.468766 -146.307733 lk3_ref.csv lk3_abs.csv
./add_absolute_coordinates.py --latlon 63.466250 -146.318283 lk4_ref.csv lk4_abs.csv
./add_absolute_coordinates.py --latlon 63.464000 -146.316416 lk5_ref.csv lk5_abs.csv
./add_absolute_coordinates.py --latlon 63.474116 -146.307683 fix_ref.csv theo_abs.csv

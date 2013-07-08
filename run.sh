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


# Remove shift that occurred on 2013-06-26 between 19:04 and 19:19 AKST,
# run fix_shift.py to remove the shift, here in UTC
./fix_shift.py fix.csv fix_shifted.csv
./fix_shift.py --avg_date '2013-06-27 02:00:52' --before_date '2013-06-27 03:00:52' --after_date '2013-06-27 03:15:53' br1.csv br1_shifted.csv
./fix_shift.py --avg_date '2013-06-27 02:02:01' --before_date '2013-06-27 03:02:03' --after_date '2013-06-27 03:17:04' br2.csv br2_shifted.csv
./fix_shift.py --avg_date '2013-06-27 02:02:58' --before_date '2013-06-27 02:47:45' --after_date '2013-06-27 03:18:04' br3.csv br3_shifted.csv
./fix_shift.py --avg_date '2013-06-27 01:03:46' --before_date '2013-06-27 02:48:23' --after_date '2013-06-27 03:18:44' br4.csv br4_shifted.csv
./fix_shift.py --avg_date '2013-06-27 02:00:31' --before_date '2013-06-27 03:00:31' --after_date '2013-06-27 03:15:31' br5.csv br5_shifted.csv
./fix_shift.py --avg_date '2013-06-27 02:01:40' --before_date '2013-06-27 03:01:41' --after_date '2013-06-27 03:16:42' br6.csv br6_shifted.csv
./fix_shift.py --avg_date '2013-06-27 02:01:18' --before_date '2013-06-27 03:01:20' --after_date '2013-06-27 03:16:21' br7.csv br7_shifted.csv
./fix_shift.py --avg_date '2013-06-27 02:06:55' --before_date '2013-06-27 03:06:59' --after_date '2013-06-27 03:21:29' lk1.csv lk1_shifted.csv
./fix_shift.py --avg_date '2013-06-27 02:06:30' --before_date '2013-06-27 03:06:35' --after_date '2013-06-27 03:21:05' lk2.csv lk2_shifted.csv
./fix_shift.py --avg_date '2013-06-27 02:06:08' --before_date '2013-06-27 03:06:14' --after_date '2013-06-27 03:20:43' lk3.csv lk3_shifted.csv
./fix_shift.py --avg_date '2013-06-27 02:04:44' --before_date '2013-06-27 03:04:42' --after_date '2013-06-27 03:19:35' lk4.csv lk4_shifted.csv
./fix_shift.py --avg_date '2013-06-27 02:05:39' --before_date '2013-06-27 02:50:05' --after_date '2013-06-27 03:20:21' lk5.csv lk5_shifted.csv
# The GPS of station BR4 was moved on 2013-06-26 between 20:48:14 and 21:49:07 UTC,
# run fix_shift.py to remove the shift
./fix_shift.py --avg_date '2013-06-26 19:33:30' --before_date '2013-06-26 20:48:14' --after_date '2013-06-26 21:49:07' br4_shifted.csv br4_shifted2.csv
# Process THEO
./process_theo.py fix_shifted.csv
# Proccess all stations excecpt THEO with respect to FIX, this produces
# the reference files _ref.csv
./process_theo.py --reference_file fix_shifted.csv br[1-3,5-7]_shifted.csv br4_shifted2.csv lk?_shifted.csv

# Turn relative easting/northing into absolute coordinates using approximate
# stake positions. Both lat/lon and easting/northing (EPSG:3338) are saved.
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

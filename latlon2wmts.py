#!/usr/bin/python
# Convert latitude, longitude, zoom a cmdline params to WMTS tile numbers
# From: https://github.com/AlexandreLouisnard/python-coordinates-to-wmts-tiles-indexes/blob/master/coordinates2WmtsTilesNumbers.py

import math
import sys

def coordinates2WmtsTilesNumbers(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
  return (xtile, ytile)

if len(sys.argv) != 4:
  print ("Converts latitude/longitude coordinates in degrees to the WMTS tiles numbers at a given zoom level.")
  print ("Usage: coordinates2WmtsTilesNumbers latitude_degrees longitude_degrees zoom")
else:
  print ("Latitude: " + sys.argv[1])
  print ("Longitude: " + sys.argv[2])
  print ("Zoom: " + sys.argv[3])
  tile = coordinates2WmtsTilesNumbers(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]))
  print ("=> x tile: " + str(tile[0]))
  print ("=> y tile: " + str(tile[1]))

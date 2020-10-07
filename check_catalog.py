#!/usr/bin/env  python
# read directory, update filenames, sizes,

import os,sys
import json
import sqlite3
import datetime
import glob

MAP_VERSION = os.environ.get("MAP_VERSION",'v.999')
if MAP_VERSION == 'v.999':
   print('The environment is not set. Please run "source setenv"') 
   sys.exit(1)
MAP_DATE = os.environ.get("MAP_DATE",'v.999')
BLAST_VERSION = os.environ.get("BLAST_VERSION")
# Variables are being properly defined by environment variables
MR_SSD = os.environ.get("MR_SSD",'/root/mapgen')
#CATALOG = os.path.join(MR_SSD,'../resources','regions.json')
CATALOG = './regions.json'
DOWNLOAD_URL = 'https://archive.org/download'
#GENERATED_TILES = MR_SSD + '/output/stage2/'
GENERATED_TILES = '/library/www/html/internetarchive'
BASE_SATELLITE_SIZE = "976416768"
BASE_SATELLITE_URL = "https://archive.org/download/satellite_z0-z9_v3.mbtiles/satellite_z0-z9_v3.mbtiles"
BASE_PLANET_SIZE = "1870077952"
BASE_PLANET_URL = "https://archive.org/download/osm-planet_z0-z10_2019.mbtiles/osm-planet_z0-z10_2019.mbtiles"

outstr = ''
region_list = []
map_catalog = {}
with open(CATALOG,'r') as catalog_fp:
   try:
      data = json.loads(catalog_fp.read())
   except:
      print("json error reading regions.json")
      sys.exit(1)
   map_catalog['maps'] = {}
   for region in data['regions'].keys():
      map_id = 'osm-' + os.path.basename(data['regions'][region]['detail_url'])
      map_catalog['maps'].update({map_id : {}})
      for (key, value) in data['regions'][region].items():
         map_catalog['maps'][map_id].update( {key : value} )
         map_catalog['maps'][map_id]['region'] = region 
         map_catalog['maps'][map_id]['detail_url'] = os.path.join(DOWNLOAD_URL,map_id,map_id)
         map_catalog['maps'][map_id]['bittorrent_url'] = os.path.join(DOWNLOAD_URL,map_id,map_id + '.torent')

   outstr = json.dumps(map_catalog,indent=2,sort_keys=True) 
   print(outstr)
   sys.exit(0)

   for region in data['regions'].keys():
      map_id = 'osm-' + os.path.basename(data['regions']['detail_url'])
      mbtile = os.path.join(GENERATED_TILES,region+'_z11-z14_2019.mbtiles')
      if region == 'world':
         mbtile = os.environ.get('PLANET_MBTILES','')
         map_catalog['maps'][map_id]['osm_size'] = "54776152064"
      if mbtile == '':
         print('problem with planet mbtile')
         sys.exit(1)
      perma_ref = map_id
      identity = perma_ref + '_' + data['maps'][region]['date'] +'_'\
		 + MAP_VERSION 
      file_ref = identity + '.zip'
      # the folowing were to get started. Now permit independent region release
      #map_catalog['maps'][map_id]['perma_ref'] = perma_ref
      if BLAST_VERSION == 'True':
         map_catalog['maps'][map_id]['url'] = DOWNLOAD_URL+ '/' + identity + \
                                       '/' + identity + '.zip'
      sat_identity = perma_ref + '_sat_' + data['maps'][region]['date'] +'_'\
		 + MAP_VERSION 
      map_catalog['maps'][map_id]['sat_url'] = DOWNLOAD_URL+ '/' + sat_identity + \
                                       '/' + sat_identity
      tile_identity = 'osm-'+ os.path.basename(mbtile)
      map_catalog['maps'][map_id]['detail_url'] = DOWNLOAD_URL+ '/' + tile_identity + '/'\
             + tile_identity 
      map_catalog['maps'][map_id]['publish'] = "True"
      #map_catalog['maps'][map_id]['sat_is_regional'] = 'False' 
      try:
         conn = sqlite3.connect(mbtile)
         c = conn.cursor()
         sql = 'select value from metadata where name = "filesize"'
         c.execute(sql)
      except Exception as e:
         print("ERROR -no access to metadata in region:%s"%region)
         print("Path:%s"%mbtile)
         print("sql error: %s"%e)
         sys.exit(1)
         continue
      row = c.fetchone()
	   #print(row[0])
      if row:
         map_catalog['maps'][map_id]['osm_size'] = row[0]
      elif region != "world":
         print("No Size data for region:%s"%region)

      # There may be a regional SATELLITE .mbtiles
      if map_catalog['maps'][region]['sat_is_regional'] == 'True':
         mbtile = GENERATED_TILES + region+'_sat_.mbtiles'
         # don't try to connect if not present, creates empty db
         try:
            conn = sqlite3.connect(mbtile)
            c = conn.cursor()
            sql = 'select value from metadata where name = "filesize"'
            c.execute(sql)
            row = c.fetchone()
            #print(row[0])
            if row:
               map_catalog['maps'][map_id]['sat_size'] = str(row[0])
            else:
               map_catalog['maps'][map_id]['sat_size'] = BASE_SATELLITE_SIZE
         except:
            map_catalog['maps'][map_id]['sat_size'] = BASE_SATELLITE_SIZE
      else:
         map_catalog['maps'][map_id]['sat_size'] = BASE_SATELLITE_SIZE
         map_catalog['maps'][map_id]['sat_url'] = BASE_SATELLITE_URL

      # record combined satellite and OSM size
      total_size = float(data['maps'][region]['sat_size']) + \
                   float(data['maps'][region]['osm_size']) + float(BASE_PLANET_SIZE)
      map_catalog['maps'][map_id]['size'] = str(int(total_size))
      map_catalog['maps'][map_id]['date'] = MAP_DATE

   outstr = json.dumps(map_catalog,indent=2,sort_keys=True) 
   print(outstr)


now = datetime.datetime.now()
date_time = now.strftime("%y-%m-%d")
print(date_time)
output_filename = "./map_catalog.json.%s"%date_time
#with open(output_filename,'w') as catalog_fp:
#   catalog_fp.write(outstr)

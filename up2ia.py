#!/usr/bin/env  python3
# Upload the Regional osm-vector maps to InernetArchive

import os,sys
sys.path.append('/usr/local/lib/python2.7/dist-packages')
import json
import shutil
import subprocess
import internetarchive
import re
from datetime import datetime
from logging import getLogger

MAP_CATALOG = '/etc/iiab/map-catalog.json'
with open('/opt/iiab/maptools/map.list','r') as fp:
   MAP_LIST = fp.read()
map_js = json.loads(MAP_LIST)
MAP_LIST = map_js['list']
print('map.list limits processing to: %s\n'%MAP_LIST)

MR_HARD_DISK = '/library/www/html/internetarchive'
MAP_DATE = os.environ.get("MAP_DATE",'2019-09-30')
MAP_VERSION = 'v.2.0`'

log = getLogger(__name__)
log.setLevel("DEBUG")

with open(MAP_CATALOG,'r') as map_fp:
   try:
      data = json.loads(map_fp.read())
   except:
      print("maps.json parse error")
      sys.exit(1)
   for map in data['maps'].keys():
      if map in MAP_LIST:

         # pull the version string out of the url for use in identity
         version = data['maps'][map]['version']
         url = data['maps'][map]['detail_url']

         # Fetch the md5 to see if local file needs uploading
         target_zip = os.path.join(MR_HARD_DISK,map)
         with open(target_zip + '.md5','r') as md5_fp:
            instr = md5_fp.read()
            md5 = instr.split(' ')[0]
         if len(md5) == 0:
            print('md5 was zero length. ABORTING')
            sys.exit(1)

         # Gather together the metadata for archive.org
         md = {}
         md['title'] = "Vector tiles for IIAB: %s"%map
         #md['collection'] = "internetinabox"
         md["creator"] = "Internet in a Box" 
         md["subject"] = "rpi" 
         md["subject"] = "maps" 
         md["licenseurl"] = "http://creativecommons.org/licenses/by-sa/4.0/"
         md["zip_md5"] = md5
         md["mediatype"] = "software"
         md["description"] = "This set of vector tiles was filered from the planet at https://archive.org/details/osm-vector-mbtiles"

         identifier = map 
         # Check is this has already been uploaded
         item = internetarchive.get_item(identifier)
         print('Identifier: %s. Filename: %s'%(identifier,target_zip,))
         if item.metadata:
            if item.metadata['zip_md5'] == md5:
               # already uploaded
               print('local file md5:%s  metadata md5:%s'%(md5,item.metadata['zip_md5']))
               print('Skipping %s -- checksums match'%map)
               continue
            else:
               print('md5sums for %s do not match'%region)
               r = item.modify_metadata({"zip_md5":"%s"%md5})
         else:
            print('Archive.org does not have file with identifier: %s'%identifier) 
         # Debugging information
         print('Uploading %s'%map)
         print('MetaData: %s'%md)
         try:
            r = internetarchive.upload(identifier, files=[target_zip], metadata=md, verbose=True)
            print(r[0].status_code) 
            status = r[0].status_code
         except Exception as e:
            status = 'error'
            with open('./upload.log','a+') as ao_fp:
               ao_fp.write("Exception from internetarchive:%s"%e) 
         with open('./upload.log','a+') as ao_fp:
            now = datetime.now()
            date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
            ao_fp.write('Uploaded %s at %s Status:%s\n'%(identifier,date_time,status))

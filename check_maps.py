#!/usr/bin/env  python3
# scan through map-catalg and check arhive.org for detail_url


import os,sys
sys.path.append('/usr/local/lib/python2.7/dist-packages')
import json
import shutil
import subprocess
import internetarchive
import re
from datetime import datetime

def get_archive_metadata(identifier):
      return internetarchive.get_item(identifier)

def check(name):
   info =  get_archive_metadata(name)
   #print(str(info.item_metadata['files'][0]['md5']))
   #print(str(info.item_metadata))
   #os.exit(1)
   if not info: return False
   return True
   #print("\nArchive.org metadata:\n%s"%json.dumps(info.metadata,indent=2))

MAP_CATALOG = '/etc/iiab/map-catalog.json'
with open(MAP_CATALOG,'r') as fp:
   data = fp.read()
map_js = json.loads(data)
num = 0
for key  in map_js['maps'].keys():
   fname =map_js['maps'][key]['detail_url']
   #print(fname)
   if not check(os.path.basename(fname)):
      print('%s not in archive.org'%fname)
   else:
      num += 1
print("Except for missing noted above, we have validated %s mbtiles at archive.org"%num)


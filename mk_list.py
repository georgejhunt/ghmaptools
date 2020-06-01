#!/usr/bin/env  python
# create a list from which to delete regions (limits generation process)
# A region must be in the regions.list to be processed

import os,sys
import json
import shutil
import subprocess

MAP_CATALOG = '/etc/iiab/map-catalog.json'
outstr='{"list": [\n'
with open(MAP_CATALOG,'r') as region_fp:
   try:
      data = json.loads(region_fp.read())
   except:
      print("regions.json parse error")
      sys.exit(1)

   for region in data['maps'].keys():
      outstr += '  "' +region + '",\n'
   outstr = outstr[:-2]
   outstr += '\n]\n}\n'
print(outstr)

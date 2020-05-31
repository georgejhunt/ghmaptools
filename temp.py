#!/usr/bin/env  python3
# Test for existence of an item

import os,sys
import json
import shutil
import subprocess
import internetarchive

item = internetarchive.get_item('en-osm-omt_min_2017-07-03_v0.')
if item.metadata:
   print(repr(item.metadata))
   print(item.item_size)
else:
   print('no item')

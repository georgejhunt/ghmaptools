#!/usr/bin/env python
# this has turned obsolete as geofabriq uses line string bboxes 
# create spec for bounding boxes used in IIAB vector map subsets

from geojson import Feature, Point, FeatureCollection, Polygon
import geojson
import json
import os,sys

def human_readable(num):
    # return 3 significant digits and unit specifier
    num = float(num)
    units = [ '','K','M','G']
    for i in range(4):
        if num<10.0:
            return "%.2f%s"%(num,units[i])
        if num<100.0:
            return "%.1f%s"%(num,units[i])
        if num < 1000.0:
            return "%.0f%s"%(num,units[i])
        num /= 1000.0

input_dir = '../resources'
input_json = input_dir + '/regions.json'
compare_json = input_dir + '/regions.json.orig'
if len(sys.argv) > 1:
   input_json = sys.argv[1]   
def main():
   features = []
   with open(input_json,'r') as regions:
      reg_str = regions.read()
      info = json.loads(reg_str)
   #print(json.dumps(info,indent=2))
 
   with open(compare_json,'r') as regions:
      compare_str = regions.read()
      compare_info = json.loads(compare_str)
   for root in info.keys():
      for region in info[root]:
         try:
            print('region:%s New size:%s Old size:%s'%(region,human_readable(info['regions'][region]['size']),\
                  human_readable(compare_info['regions'][region]['size'])))
         except:
            pass
if __name__ == '__main__':
   main()

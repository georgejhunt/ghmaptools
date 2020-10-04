#!/usr/bin/env  python3
# Get a file from InternetArchive using bittorrent

import os,sys
sys.path.append('/usr/local/lib/python2.7/dist-packages')
import json
import internetarchive
import re
from datetime import datetime
from transmission_rpc import Client,Torrent
import transmission_rpc
import requests
import argparse

DOWNLOAD_URL = 'https://archive.org/download'
MAP_CATALOG_URL = 'http://d.iiab.io/content/OSM/vector-tiles/map-catalog.json'
bt_client = object
local_torrents = object
files_info = object

def exists(fname):
   r = requests.get(fname)
   return r.status_code == 200
   
def get_catalog_torrent_list():
   catalog = []
   r = requests.get(MAP_CATALOG_URL)
   if r.status_code == 200:
      catalog= json.loads(r.content)
      for map in catalog['maps'].keys():
         catalog.append(catalog['maps'][map]['bittorrent_url'])
   else:
      print(MAP_CATALOG_URL + ' not found')
   return catalog

def get_catalog():
   r = requests.get(MAP_CATALOG_URL)
   if r.status_code == 200:
      catalog= json.loads(r.content)
      return catalog['maps']
   return {}

def get_local_torrent_files():
   global bt_client
   global local_torrents
   global files_info
   local_bts = []
   bt_client = Client(username='ghunt', password='1jason2')
   local_torrents = bt_client.get_torrents()
   if not bt_client:
      print('Failed to connect to local bit-torrent daemon')
      sys.exit(1)
   files_info = bt_client.get_files()
   for item in files_info.keys():
      #print(str(item),str(files_info[item]))
      #print('index: %2s  status: %8s file: %s'%(item,local_torrents[item-1].status,files_info[item][0]['name'].split('/')[0] ))
      pass
   for index in range(len(local_torrents)):
      tor = local_torrents[index]
      #print('%s %s'%(tor.name,tor.progress))
   tors = bt_client.get_torrents()
   for tor in tors:
      tl = tor.files()
      # torrents  can include many files, for maps, only one
      #info = tl[0]
      local_bts.append(tor)
   return local_bts

def get_bitorrent_percent(tor):
   return tor.progress

def get_bitorrent_status(tor):
   return tor.status

def get_bitorrent_sizes(tor):
   files = tor.files()
   bytesCompleted = files[0]['completed']
   length = files[0]['size']
   return (bytesComplted, length)

def get_bitorrent_eta(tor):
   # returns datetime.timedelta
   return tor.eta

def parse_args():
    parser = argparse.ArgumentParser(description="Download OSM Bittorrent files.")
    parser.add_argument("-a","--all", help='Start downloading all Archive.org  maps.',action='store_true')
    parser.add_argument("-c","--catalog", help='List Map Catalog Index numbers and torrent info.',action='store_true')
    parser.add_argument("-g","--get", help='Download Map via Index number from catalog command.')
    parser.add_argument("-i","--idx", help='Download Map via Catalog key (MapID).')
    parser.add_argument("-t","--torrents", help='List status of local torrents.',action='store_true')
    return parser.parse_args()

############# Action ##############
args = parse_args()
catalog = get_catalog()
local_torrents = get_local_torrent_files()

map_key_list = []
for key in catalog.keys():
   map_key_list.append((catalog[key]['seq'],key))
map_key_list = sorted(map_key_list)
if args.catalog:
   for seq,key in map_key_list:
      archive_name = '%s/%s'%(key,key)
      found_file_num = -1
      for file_num in files_info:
         if files_info[file_num][0]['name'] == archive_name:
            found_file_num = file_num
      if found_file_num == -1:
         status = 'absent'
         file_name = catalog[key]['title']
         percent = 0.0
         num = 0
         units = ''
      else: 
         tor = None
         for torrent in local_torrents:
            if torrent.name == key:
               tor = torrent
         if tor:
            status = tor.status
            percent = tor.progress
            files = tor.files()
            bytesCompleted = files[0]['completed']
            length = files[0]['size']
            name = files[0]['name'].split('/')[0]
            num,units = transmission_rpc.utils.format_size(length)
         else:
            status = ''
            percent = ''
            num = 0
            units = ''
         file_name = catalog[key]['title']
      print('Index: %2s  %5.1f %3s %3.0d%%  status: %8s Region: %s'%(seq,num,units,percent,status,file_name ))
      #print(catalog[key]['title'],catalog[key]['seq'])
   sys.exit(1)

if args.get:
   try:
      num = int(args.get)
   except:
      print('\n%s is not a number. Please use the \'-l\' to list the numbers for use with get.\n'%args.get)
      sys.exit(1)
      
   get_url = catalog[map_key_list[num]].get('bittorrent_url','')
   print('getting %s'%get_url)
   sys.exit(1)
   
if args.torrents:
   for tor in local_torrents:
      files = tor.files()
      bytesCompleted = files[0]['completed']
      length = files[0]['size']
      name = files[0]['name'].split('/')[0]
      num,units = transmission_rpc.utils.format_size(length)
      print('%3.0f%% %5.1f %s %s'%(tor.progress,num,units,name))
   sys.exit(1)
   
if args.all:
   for key in catalog.keys():
      torent_index = -1
      for index in range(len(local_torrents)):
         fn = local_torrents[index].files()[0]['name']
         #print('local:%s  key: %s'%(fn,key))
         if fn.find(key) == -1: 
            torrent_index = index
      if torrent_index != -1:
         status = get_bitorrent_status(local_torrents[torrent_index])
         print(status)
         if status == 'stopped'or status == 'paused':
            local_torrents[torrent_index].start()
            print("Status:%s Retarting torrent for %s"%(status,catalog[key]['detail_url']))
         elif status == 'seeding':
            #print("torrent for %s is seeding"%key)
            pass
         elif status == 'downloading':
            #print("torrent for %s is dowloading"%key)
            pass
      else:
          print("Starting torrent for %s"%catalog[key]['detail_url'])
          #bt_client.add_torrent(catalog[key]['detail_url'],timeout=120)
   sys.exit(1)

   
   
   
sys.exit(1)

# If there are maps in the catalog that are not in local cache, start the download
for fn in tlist:
   #print(fn)
   bt_started = False
   if exists(fn):
      for index in range(len(local_torrents)):
         if local_torrents[index].files()[0]['name'] == fn:
            bt_started = True
            print("Bit torrent started for %s"%fn)
      if not bt_started:
         bt_client.add_torrent(fn,timeout=120)
         print("Starting torrent for %s"%fn)
      else:
         print('Already started download for %s'%fn)
         
   else:
      #print("no bit_torrent url for %s"%fn)
      pass
      
sys.exit(1)



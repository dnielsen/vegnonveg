#!/usr/bin/env python3

import codecs
import csv
import urllib.request
import json
import redis
import sys

from urllib.error import URLError

rental_flags = {
    'KEY': 1,
    'CREDITCARD':2,
    'PAYPASS': 4,
    'APPLEPAY': 8,
    'ANDROIDPAY': 16,
    'TRANSITCARD':32,
    'ACCOUNTNUMBER': 64,
    'PHONE': 128,
}

station_data_size = []

def encode_rental_methods(method_list):
    "Encodes the rental method list as an integer"
    code = 0x00
    for method in method_list:
        code |= rental_flags.get(method, 0)
    
    return code

def decode_rental_methods(code):
    
    rental_methods = []
    for method, flag in rental_flags.items():
        if code & flag == flag:
            rental_methods.append(method)
    
    return sorted(rental_methods, key=lambda x: rental_flags[x])

def station_status_feed_url(main_feed):
    "Find the station status feed url from the main feed results"
    
    subfeed_urls = main_feed['data']['en']['feeds']
    for subfeed in subfeed_urls:
        if subfeed['name'] == 'station_information':
            return subfeed['url']
    
    return None
    
def system_information_feed_url(main_feed):
    subfeed_urls = main_feed['data']['en']['feeds']
    for subfeed in subfeed_urls:
        if subfeed['name'] == 'system_information':
            return subfeed['url']
    
    return None


def fetch_url(url):
    "Fetches a gbfs feed url and parses the feed into JSON objects"
    try:    
        with urllib.request.urlopen(url) as resp:
            if resp.status != 200:
                raise Exception("Failed to load url: {} status = {}".format(url, resp.status))
        
            raw_feed = resp.read()
            feed = json.loads(raw_feed)
    
            return feed
        
    except URLError as urlerr:
        print("Failed to load url: {} ({})".format(url, str(urlerr)))
        return None
    
def fetch_csv(csvurl):
    "Fetches the list of known GBFS feeds from master csv list"
        
    with urllib.request.urlopen(csvurl) as resp:
        if resp.status != 200:
            raise Exception("Failed to load url {} status = {}".format(csvurl, resp.status))
        
        feedlist = []
        gbfs_csv_reader = csv.DictReader(codecs.iterdecode(resp, 'utf-8'))
        for row in gbfs_csv_reader:
            feedlist.append((row['Name'], row['Location'], row['Auto-Discovery URL']))
            
        return feedlist    
    
def load_system_info(r, system_info_url):
    "Loads the system information feed and returns the system id"
    system_info_feed = fetch_url(system_info_url)
    
    system_id = system_info_feed['data']['system_id'] 
    key = "{}:system_info".format(system_id)
    r.hmset(key, system_info_feed['data'])
    
    return system_id

def load_station_info(r, system_id, station_info_url):
    "Takes the station info url and parses the results into JSON objects"

    # parse feed into JSON
    info_feed = fetch_url(station_info_url)
    
    # fetch station data
    updated_at = info_feed['last_updated']
    stations = info_feed['data']['stations']
    
    # check for the existence of stations, some feeds don't have them
    if not stations:
        return
    
    # define keys for data load
    global_station_loc_key = "global:stations:location"
    station_set_key = "{}:stations".format(system_id)
    station_loc_key = "{}:stations:location".format(system_id)
    staging_key_station_set = "staging:{}:stations".format(system_id)
    
    # get the current set of stations for the system
    current_stations = r.smembers(station_set_key)
    #print(current_stations)
    
    # iteratively load stations into staging keys
    for station in stations:
                
        # encode rental methods for storage (optional field)
        if 'rental_methods' in station.keys():
            station['rental_methods'] = encode_rental_methods(station['rental_methods'])
        
        station['updated_at'] = updated_at
        
        station_key = "{}:station:{}".format(system_id, station['station_id'])
        
        # build a txn to update the station data
        p = r.pipeline(transaction=True)
        p.delete(station_key)
        p.hmset(station_key, station)
        p.sadd(station_set_key, station_key)
        p.execute_command("GEOADD", global_station_loc_key, station['lon'], station['lat'], station_key)
        p.execute_command("GEOADD", station_loc_key, station['lon'], station['lat'], station_key)
        p.execute()
        

        # remove station from list of old stations
        current_stations.discard(station_key)


    # remove any of the old stations
    for station in current_stations:
        station_key = "{}:station:{}".format(system_id, station)
        p = r.pipeline(transaction=True)
        p.delete(station)
        p.srem(station_key, station)
        p.zrem(global_station_loc_key, station_key)
        p.zrem(station_loc_key, station_key)
        p.execute()
            

def process_feed(r, feed_url):
    "Processes the mail feed and loads data into Redis"
    feed = fetch_url(feed_url) 
    if feed is None:
        raise Exception("Unable to load discovery feed: " + feed_url)       

    system_info_url = system_information_feed_url(feed)
    if system_info_url is None:
        raise Exception("Unable to find system information feed")
        
    station_info_url = station_status_feed_url(feed)
    if station_info_url is None:
        raise Exception("Unable to find station information feed")
      
    system_id = load_system_info(r, system_info_url)
    r.sadd("geobike:systems", system_id)
       
    load_station_info(r, system_id, station_info_url)
    
    # notify intersted clients that fresh data was loaded
    r.publish("geobike:station_changed", system_id)
    
def process_feed_list(r, master_csv):
    "Parse the master csv file of known GBFS feeds"
    
    for name, location, feed_url in fetch_csv(master_csv):
        print("Processing feed for {} in {}".format(name, location))
        try:
            process_feed(r, feed_url)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    
    # provide your redis configuration infromation here
    cfg = { 'host': 'localhost',
        'port': 6379,
        'password': None,
        'ssl': False
    }
    
    master_feed_list = "https://github.com/dnielsen/vegnonveg/blob/master/python/data/data.csv"

    r = redis.StrictRedis(**cfg, decode_responses=True)
    process_feed_list(r, master_feed_list)
    sys.exit(0)

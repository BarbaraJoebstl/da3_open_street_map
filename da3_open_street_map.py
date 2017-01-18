import xml.etree.ElementTree as ET
import pprint
import re
import os
import codecs
import json
from collections import defaultdict

#https://www.openstreetmap.org/export#map=13/52.5180/13.4076
OSM_FILE = 'berlin_map.osm'
SAMPLE_FILE = 'berlin_map_reduced.osm'

#check file size
#resource: http://stackoverflow.com/questions/2104080/how-to-check-file-size-in-python

def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)
    
size = file_size(OSM_FILE)
#print ('OSMSize', size)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

k = 14 # Parameter: take every k-th top level element
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag
    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

with open(SAMPLE_FILE, 'wb') as output:
    b = bytearray()
    b.extend('<?xml version="1.0" encoding="UTF-8"?>\n'.encode())
    b.extend('<osm>\n  '.encode())
    output.write(b)

    # Write every kth top level element
    print (OSM_FILE)
    for i, element in enumerate(get_element(OSM_FILE)):

        if not i % k:
            output.write(ET.tostring(element, encoding='utf-8'))
    b_end = bytearray()
    b_end.extend('</osm>'.encode())
    output.write(b_end)

#check size of sample file
sample_size = file_size(SAMPLE_FILE)
print ('SampleSize', sample_size)

#get benchmark data
"""
    Reference:
    https://classroom.udacity.com/nanodegrees/nd002/parts/0021345404/modules/316820862075462/lessons/768058569/concepts/8426285720923#
"""
def get_benchmark_data(filename):
    users = set()
    count_nodes = 0
    count_ways = 0
    count_relations = 0
    
    for _, element in ET.iterparse(filename):
        if element.tag == 'node':
            count_nodes += 1
            user = element.attrib['uid']
            if user in users:
                pass
            else:
                users.add(user)
        if element.tag == 'way':
            count_ways += 1
        if element.tag == 'relation':
            count_relations += 1
    return users, count_nodes, count_ways, count_relations

users, count_nodes, count_ways, count_relations = get_benchmark_data(OSM_FILE)

print ('UNIQUE USERS: ', len(users))
print ('NODES:', count_nodes)
print ('WAYS:', count_ways)
print ('RELATIONS', count_relations)

'''reference:
https://classroom.udacity.com/nanodegrees/nd002/parts/0021345404/modules/316820862075462/lessons/768058569/concepts/8755386150923#'''

#start with lower case letters, due to different ways of writing street names in german
expected = ['straße', 'platz', 'gasse', 'weg', 'allee', 'damm', 'ufer', 'graben', 'brücke', 
            'promenade', 'park', 'am', 'an', 'markt', 'steg', 'hof', 'zeile']

def audit_street_type(street_types, street_name):
    found = False
    for e in expected:
        if e in street_name.lower():
            found = True
            break
           
    if found:
        street_types[e].add(street_name)
    else:
        street_types[street_name.title()].add(street_name)    
                              
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

#audit the street names
def audit_street_names(osmfile):
    osm_file = open(osmfile, 'rt', encoding='utf-8')
    #set is a list without duplicates
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    print('Numbers of different street types in Berlin')
    pretty_print(street_types)

def pretty_print(d):
    for sorted_key in sorted(d, key=lambda k: len(d[k]), reverse=True):
        v = d[k]
        print (sorted_key.title(), ':', len(d[sorted_key]))
        
audit_street_names(OSM_FILE)

suburbs_with_postal_codes = {
                            'Mitte': [10115, 10117, 10119, 10178, 10179],
                             'Gesundbrunnen': [13347, 13353, 13355, 13357, 13359, 13409],
                             'Friedrichshain': [10243, 10245, 10247, 10249],
                             'Prenzlauer Berg': [10405, 10407, 10409, 10435, 10437, 10439, 10369],
                             'Kreuzberg': [10961, 10963, 10965, 10967, 10969, 10997, 10999],
                             'Tiergarten': [10551, 10553, 10785, 10787, 10559, 10555, 10557],
                             'Charlottenburg': [10585, 10587, 10589, 10623, 10625, 10627, 10629],
                             'Wilmersdorf': [10707, 10709, 10711, 10713, 10715, 10719, 10717],
                             'Tempelhof': [10777, 10779, 10781, 10783, 10789],
                             'Schöneberg': [10823, 10825, 10827, 10829, 10717, 10783],
                             'Neukölln': [12043, 12045, 12047, 12049, 12051, 12053, 12055, 12057, 12059],
                             'Steglitz': [12157, 12161, 12163, 12165, 12167, 12169],
                             'Lichterfelde': [12203, 12205, 12207, 12209],
                             'Wedding': [13347, 13349, 13351, 13353, 13355, 13357, 13359],
                             'Reinickendorf': [13403, 13405, 13407, 13409],
                             'Lichtenberg': [13055, 13053, 10365, 10367, 10317],
                             'Pankow': [13187, 13189],
                             'Zehlendorf': [14163, 14165, 14167, 14169],
                             'Wannsee': [14109],
                             'Wittenau': [13435, 13437, 13439],
                             'Weißensee': [13086, 13088, 13089],
                             'Mahrzahn': [12679, 12681, 12683, 12685, 12687, 12689],
                             'Köpenick': [12555, 12557, 12559, 12587, 12435],
                             'Adlershof': [12487, 12489],
                             'Lichtenrade': [12305, 12307, 12309],
                             'Marienfelde': [12277, 12279],
                             'Lankwitz': [12247, 12249]
                            }

#create a list with all postal codes
all_postal_codes = set()
for v in suburbs_with_postal_codes.values():
    for v_ in v:
        all_postal_codes.add(v_)
#create a list to output wrong postal codes    
wrong_postal_codes = set()

#check if postal code is correct and then check if it corresponds to correct suburbs
def audit_postal_code(postal_code):
    if int(postal_code) not in all_postal_codes:
        wrong_postal_codes.add(int(postal_code))
        
def is_postal_code(elem):
    return (elem.attrib['k'] == "addr:postcode")

def audit_postal_codes(osmfile):
    osm_file = open(osmfile, 'rb')
    #set is a list without duplicates
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "way" or elem.tag == "node":
            for tag in elem.iter("tag"):
                if is_postal_code(tag):
                    audit_postal_code(tag.attrib['v'])
    osm_file.close()

audit_postal_codes(OSM_FILE)
print (wrong_postal_codes)

all_suburbs = set()
for v in suburbs_with_postal_codes.keys():
    all_suburbs.add(v)
#create a list to output wrong postal codes    
wrong_suburbs = set()

def audit_suburbs(osmfile):
    osm_file = open(osmfile, 'rb')
    #set is a list without duplicates
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "way" or elem.tag == "node":
            for tag in elem.iter("tag"):
                if is_suburb(tag):
                    audit_suburb(tag.attrib['v'])
    osm_file.close()

def audit_suburb(suburb):
    if (suburb) not in all_suburbs:
        wrong_suburbs.add(suburb)    
    
def is_suburb(elem):
    return (elem.attrib['k'] == "addr:suburb")

audit_suburbs(SAMPLE_FILE)
print (wrong_suburbs)

#check if postal code and suburb are correct
check_suburbs_and_postal_codes = defaultdict(set)
    
def audit_postal_code_and_suburb(osmfile):
    osm_file = open(osmfile, 'rb')
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        current_suburb = None
        current_postal_code = None
        if elem.tag == "way" or elem.tag == "node":
            for tag in elem.iter("tag"):
                if is_suburb(tag):
                    current_suburb = tag.attrib['v']
                if is_postal_code(tag):
                    current_postal_code = tag.attrib['v']
        if current_postal_code and current_suburb:        
            check_suburbs_and_postal_codes[current_suburb] = int(current_postal_code)                             
    osm_file.close()

audit_postal_code_and_suburb(OSM_FILE) 
print (check_suburbs_and_postal_codes)

def check_check(a, b):
    #check if key, value also exist in key and value array
    for key in a:
        if key in b:
            first, second = a[key], b[key]
            if first in second:
                pass
            else:
                print(key, first, second)
        else:
            print ('no suburb named', key)
            
check_check(check_suburbs_and_postal_codes, suburbs_with_postal_codes)  

### 2. transform to json
''' 
reference:
https://classroom.udacity.com/nanodegrees/nd002/parts/0021345404/modules/316820862075462/lessons/768058569/concepts/8755386150923#'''

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
BICYCLE_WAYS = ["cycleway", "bicycle_road", "bicycle"]
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def shape_element(element):
    node = {}
    created_dict = {}
    address_dict = {}
    bicycle_way = False

    if element.tag == "node" or element.tag == "way" :      
        node["type"] = element.tag
        for name, value in element.items():
            if name in CREATED:
                created_dict[name] = value
            elif name == 'long':
                lon = float(value)
            elif name == 'lat':
                lat = float(value)
            else:
                node[name] = value

            if len(created_dict):
                node["created"] = created_dict
           
        
        for tag in element.iter("tag"):
            k = tag.attrib['k']
            v = tag.attrib['v']
            
            #get all bicycle ways, the german and the english values
            if k in BICYCLE_WAYS and value != "no":
                bicycle_way = True
            #get the address   
            if k == 'addr:suburb':
                address_dict['suburb'] = update_suburbs(v, mapping_suburbs)
            elif k == 'addr:postcode':
                address_dict['postal_code'] = v
            elif k == 'addr:street':
                address_dict['street'] = v
            elif k == 'addr:housenumber':
                address_dict['housenumber'] = v
            elif k == 'addr:country':
                pass
            elif k == 'addr:city':
                pass 
            elif problemchars.search(k):
                pass
            else: node[k] = v                 
                
        node_refs_list = []
        for nd in element.iter("nd"):
            node_refs_list.append(nd.attrib['ref'])
        if len(node_refs_list):
            node["node_refs"] = node_refs_list
        
        if bicycle_way is True: 
            node['bicycle_way'] = 'Yes'
        if len(address_dict):
            node['address'] = address_dict
        return node
    else:
        return None
        
#fix suburbs before exporting to mongoDB
mapping_suburbs = { "Alt-Treptow": "Köpenick",
                    "Moabit": "Tiergarten",
                    "Hansaviertel": "Tiergarten",
                    "Fennpfuhl": "Lichtenberg",
                    "Alt-Hohenschönhausen": "Lichtenberg",
                    "Rummelsburg": "Lichtenberg",
                    "Plänterwald": "Köpenick",
                    "Charlottenburg-Wilmersdorf": "Charlottenburg" }

def update_suburbs(suburb, mapping_suburbs):
    for key, value in mapping_suburbs.items():
        if suburb == key:
            suburb = value
    return suburb

def process_map(file_in):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            
            if el:
                data.append(el)
                fo.write(json.dumps(el) + "\n")
    return data

data = process_map('berlin_map.osm')

example = data[:5]
print (example)

import pymongo
from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client.berlin

def insert_osm_data(infile, db):
    db.berlin.drop()      
    #import data into a collection named "berlin"
    db.berlin.insert_many(infile)
    print (db.berlin.find_one())

insert_osm_data(data, db)

print (len(db.berlin.distinct("created")));

print (db.command("dbstats"))

print ('Size of Collection')
print (convert_bytes(62980096.0))

print (len(db.berlin.distinct("created.user")));

def pretty_print_list(d):
    for member in d:
        print (member['_id'], ':', member['count'])

# get top ten of contributing users
def count_entries_by_suburbs():
    pipeline = [{'$match': {'address.suburb': {'$exists': 1}}},
                {'$group' : { '_id' : '$address.suburb', 'count' : {'$sum' : 1}}},       
                {'$sort': {'count': -1}}]
    return pipeline

def aggregate(db, pipeline):
    return [doc for doc in db.berlin.aggregate(pipeline)]

pipeline = count_entries_by_suburbs()
result = aggregate(db, pipeline)
print ('Suburbs:')
pretty_print_list(result);

# get top ten of contributing users
def get_top_ten_users():
    pipeline = [{'$group' : { '_id' : '$created.user', 'count' : {'$sum' : 1}}},       
                {'$sort': {'count': -1}},
                { '$limit': 10}]
    return pipeline

def aggregate(db, pipeline):
    return [doc for doc in db.berlin.aggregate(pipeline)]

pipeline = get_top_ten_users()
result = aggregate(db, pipeline)
print ('Top 10 contributing users with counted entries:')
pretty_print_list(result);

def get_ways_and_nodes():
    pipeline =  [{'$group' : { '_id' : '$type', 'count' : {'$sum' : 1}}},       
                {'$sort': {'count': -1}}]
    return pipeline

pipeline = get_overview_of_types()
result = aggregate(db, pipeline)
print ('Different Types:')
pretty_print_list(result)  

def get_overview_amenities():
    pipeline = [{'$match':{'amenity':{'$exists':1}}},
                {'$group' : { '_id': '$amenity', 'count' : {'$sum':1}}},
               {'$sort': {'count': -1}},
               {'$limit': 10}]
    return pipeline
    
pipeline = get_overview_amenities()
result = aggregate(db, pipeline)
print ('Amenities:')
pretty_print_list(result)

def get_roads():
    pipeline = [{ '$group': {'_id': 'highway', 'count': {'$sum': 1}}}]
    return pipeline
    
pipeline = get_roads()
result = aggregate(db, pipeline)
print ('Roads:')
pretty_print_list(result)
print ('~~~~~~~~~~~~~~~~~~~~~~~')       
    
#find bycicle roads in berlin
def get_bicycle_roads():
    pipeline = [{ '$match': {'$or':
                    [{'bicycle': { '$in': ['official', 'designated', 'use_sidepath']}},
                    {'bicycle_road': 'yes'},
                    {'cycleway': {'$in': ['lane', 'opposite', 'shared', 'share_busway', 'track']}}]
                    }},
                {'$group' : { '_id': '$highway', 'count' : {'$sum':1}}},
                {'$sort': {'count': -1}}]          
    return pipeline

pipeline = get_bicycle_roads()
result = aggregate(db, pipeline)
print ('Bicycle Roads:')
pretty_print_list(result)
print ('~~~~~~~~~~~~~~~~~~~~~~~')   

def get_total_amount_of_cycleways():   
    pipeline = [{ '$match': {'$or':
                    [{'bicycle': { '$in': ['official', 'designated', 'use_sidepath']}},
                    {'bicycle_road': 'yes'},
                    {'cycleway': {'$in': ['lane', 'opposite', 'shared', 'share_busway', 'track']}}]
                    }},
                {'$group' : { '_id': None, 'count' : {'$sum':1}}}] 
    return pipeline
    
pipeline = get_total_amount_of_cycleways()
result = aggregate(db, pipeline)
print ('Bicycle Roads Total:')
pretty_print_list(result)
print ('~~~~~~~~~~~~~~~~~~~~~~~')   

def get_total_cycleways_with_cleaned_data():
    pipeline = [{ '$match': {'bicycle_way': 'Yes'} },
                {'$group' : { '_id': None, 'count' : {'$sum':1}}}] 
    return pipeline

pipeline = get_total_cycleways_with_cleaned_data()
result = aggregate(db, pipeline)
print ('Bicycle Roads Total - cleaned data:')
pretty_print_list(result)
print ('~~~~~~~~~~~~~~~~~~~~~~~') 

def get_overview_amenities():
    pipeline = [{'$match': {'amenity': {'$exists': 1}, 
                            'amenity': {'$in': ['restaurant', 'fast_food', 'food_court', 'biergarten', 'bar', 'bbq', 'cafe'] 
                           }}},
               {"$group":{"_id":"$cuisine", "count":{"$sum":1}}},
               {"$sort":{"count":-1}},
               {"$limit": 11}]

    return pipeline
    
pipeline = get_overview_amenities()
result = aggregate(db, pipeline)
print ('Restaurants by cuisine:')
pretty_print_list(result)

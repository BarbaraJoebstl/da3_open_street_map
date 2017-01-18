
***DA3 OPEN STREET MAP - DATA WRANGLING WITH MONGODB***

*Map Area: Berlin, Germany* - https://www.openstreetmap.org/#map=13/52.5180/13.4076
The area contains the central area of Berlin. As it is one of the biggest cities in Europe, we can expect a lot of additional information about this area from the osm project.

*Sample of nodes in an .osm file:*
<node id="302864488" visible="true" version="7" changeset="36059354" timestamp="2015-12-20T06:35:42Z" user="atpl_pilot" uid="881429" lat="52.5259586" lon="13.3894424">
  <tag k="addr:city" v="Berlin"/>
  <tag k="addr:country" v="DE"/>
  <tag k="addr:housenumber" v="45"/>
  <tag k="addr:postcode" v="10117"/>
  <tag k="addr:street" v="Oranienburger Straße"/>
  <tag k="addr:suburb" v="Mitte"/>
  <tag k="amenity" v="restaurant"/>
 </node>
 
 <way id="5090250" visible="true" timestamp="2009-01-19T19:07:25Z" version="8" changeset="816806" user="Blumpsy" uid="64226">
    <nd ref="333725776"/>
    <nd ref="823771"/>
    <tag k="highway" v="residential"/>
    <tag k="name" v="Clipstone Street"/>
    <tag k="oneway" v="yes"/>
  </way>

**File Size**
OSMSize 154.6 MB
SampleSize 11.3 MB

Size of cleand data in mongoDB: 60.1 MB

**Anticipated Problems**
 - The mixture between English and German words makes it a little bit more difficult to compare values. For example bicycle ways can be set as "cycleway", "bicycle_road" or "bicycle".
 - Postal codes are wrong or not in the correct range for Berlin. 
 - Postal codes and suburbs are not corresponding.
 - The German Umlaute may cause problems, when we are using regex to audit files.
 - The German language has a lot of valid declarations for street names, so we have to audit it more often than english street names in order to make shure everything is valid.
 - When counting restaurants, it also shows that there is a mixture of languages. Which is shown with the entries 'coffee_shop' and '*Kaffee&Kuchen*', which is the same.
 - Incomplete data. 

***Auditing***
*Problems encounterd while auditing street names:*
   In German language there a lot of different namings and writings for streets: For example a 'Straße' can be 'Auerstraße' or     'Antwerpener Straße' or 'Alfred-Jung-Straße' or 'Straße des 17. Juni'. This happens also to other street types, like              '*weg*', '*zeile*', '*platz*' and also for streets that are or used to be near rivers like: '*damm*', '*ufer*', '*graben*'.
   Because there a lot of bridges in Berlin, bridges belong to ways *brücke*. 
   A street name starting with 'Zur ', 'Am ' or 'An ' simply means 'at ', but is also a valid street name. 
   A further task would be to transform all Umlaute of the file at the beginning, to make sure not to get in trouble later.

    Numbers of different street types in Berlin
    Straße : 620
    Platz : 48
    Ufer : 28
    Allee : 18
    Damm : 12
    Weg : 9
    Am : 8
    Park : 6
    ...

**Audit postal codes and suburbs**
Audit Post codes and suburbs The postal code in Berlin ranges from 10115 to 14199.
In the following task we want to check if the postal code is valid for Berlin and if 
it matches with the suburb according to thist list : 
https://en.wikipedia.org/wiki/List_of_postal_codes_in_Germany#Berlin
 
    no suburb named Hansaviertel
    no suburb named Moabit
    no suburb named Fennpfuhl
    wrong Wilmersdorf 10789 [10707, 10709, 10711, 10713, 10715, 10719, 10717]
    ...

***Data cleaning***    
The wrong suburbs from above, where already found in the audit_suburbs(). These values are neighbourhoods and not suburbs.
There are some suburbs that don't match with our postal codes.
In a next step we could check the exact address and find out if the postal code or the suburb is wrong. Or both.

```python
mapping_suburbs = { "Alt-Treptow": "Köpenick",
                    "Moabit": "Tiergarten",
                    "Hansaviertel": "Tiergarten",
                    "Fennpfuhl": "Lichtenberg",
                    "Alt-Hohenschönhausen": "Lichtenberg",
                    "Rummelsburg": "Lichtenberg",
                    "Plänterwald": "Köpenick",
                    "Charlottenburg-Wilmersdorf": "Charlottenburg" }
```

***Data Exploration with MongoDB***

**Get statistics of our database**
```python
db.command("dbstats")
    {'avgObjSize': 321.80557337910517,
    'objects': 681059, 'views': 0, 'db': 'berlin',
    'numExtents': 0, 'ok': 1.0, 'collections': 1,
    'indexSize': 4096.0, 'storageSize': 4096.0,
    'dataSize': 219168582.0, 'indexes': 1 }
 ```   

**Count unique users**
```python
len(db.berlin.distinct("created.user"));
 ```  
    2277

```python    
def count_entries_by_suburbs():
    pipeline = [{'$match': {'address.suburb': {'$exists': 1}}},
                {'$group' : { '_id' : '$address.suburb', 'count' : {'$sum' : 1}}},       
                {'$sort': {'count': -1}}]
    return pipeline
```

```python  
    Entries for suburbs:
    Mitte : 7513
    Prenzlauer Berg : 6303
    Kreuzberg : 6100
    Friedrichshain : 5866
    Tiergarten : 4407
    Lichtenberg : 3032
    Schöneberg : 2943
    Wedding : 1293
    Gesundbrunnen : 1240
    ...
 ```   

**Get top 10 contributiong users**
```python 
def get_top_ten_users():
    pipeline = [{'$group' : { '_id' : '$created.user', 'count' : {'$sum' : 1}}},       
                {'$sort': {'count': -1}},
                { '$limit': 10}]
    return pipeline

    atpl_pilot : 246334
    MorbZ : 48504
    Bot45715 : 34936
    anbr : 34122
    toaster : 19297
    Polarbear : 13495
    Berliner Igel : 13286
    Shmias : 10802
    wicking : 8506
    Elwood : 8266
  ```

**Get top 10 amenities**
```python 
def get_overview_amenities():
    pipeline = [{'$match':{'amenity':{'$exists':1}}},
                {'$group' : { '_id': '$amenity', 'count' : {'$sum':1}}},
               {'$sort': {'count': -1}},
               {'$limit': 10}]
    return pipeline

    restaurant : 1709
    bench : 1542
    cafe : 1005
    parking : 960
    fast_food : 723
    bicycle_parking : 623
    recycling : 580
    waste_basket : 578
    kindergarten : 572
    vending_machine : 499
  ```    

**Get number of bycicle roads**
As we can see, there are 623 bycicle_parkings counted, which seems to be a lot. 
Because in Berlin there is currently a referndum  - https://volksentscheid-fahrrad.de/english/ - to make the city more bycicle friendly, we would like to take a closer look at the bycicle ways in the city.
Because of the mixture of german and english there are different nodes to mark cicleways.
 http://wiki.openstreetmap.org/wiki/Key:bicycle_road

```python 
def get_roads():
    pipeline = [{ '$group': {'_id': 'highway', 'count': {'$sum': 1}}}]
    return pipeline

#find bycicle roads in berlin
def get_total_amount_of_cycleways():   
    pipeline = [{ '$match': {'$or':
                    [{'bicycle': { '$in': ['official', 'designated', 'use_sidepath']}},
                    {'bicycle_road': 'yes'},
                    {'cycleway': {'$in': ['lane', 'opposite', 'shared', 'share_busway', 'track']}}]
                    }},
                {'$group' : { '_id': None, 'count' : {'$sum':1}}}] 
    return pipeline

 def get_total_cycleways_with_cleaned_data():
    pipeline = [{ '$match': {'bicycle_way': 'Yes'} },
                {'$group' : { '_id': None, 'count' : {'$sum':1}}}] 
    return pipeline   
```

    Roads:
    highway : 681059
    ~~~~~~~~~~~~~~~~~~~~~~~
    Bicycle Roads Total:
    None : 2211
    ~~~~~~~~~~~~~~~~~~~~~~~
    Bicycle Roads Total - cleaned data:
    None : 5652
    ~~~~~~~~~~~~~~~~~~~~~~~
    
Compared to the total number of highways, the number of bicycle roads in this map is extremly small
It would be also interresting to calculate the length of all bicycle ways and compare them to the normal street net. 
The Query with the cleaned data for bicycles shows over fifty percent more entries. It seems that we missed some values for the different bicycles keys in the query for the osm data.

**Restaurants**
Because Berlin is known for its masses of restaurants we want to take a closer look at the types of restaurants:

```python 
def get_overview_amenities():
    pipeline = [{'$match': {'amenity': {'$exists': 1}, 
                            'amenity': {'$in': ['restaurant', 'fast_food', 'food_court', 'biergarten', 'bar', 'bbq', 'cafe'] 
                           }}},
               {"$group":{"_id":"$cuisine", "count":{"$sum":1}}},
               {"$sort":{"count":-1}},
               {"$limit": 11}]

    return pipeline
```

    Restaurants by cuisine:
    None : 1885
    italian : 265
    german : 117
    asian : 114
    kebab : 95
    burger : 90
    vietnamese : 84
    regional : 83
    indian : 81
    coffee_shop : 70
    pizza : 69


***Additional suggestions for improving and analyzing the data***
*Length of bicycle ways and alles bio*
    - it would be to calculate the length of all bycicley ways compared to the 'normal' street length. 
    - It also would be interessting to calculate the the percentage of the surface types, because it is said that Berlin is a "green" city.
*Improve the dataset*
    - Gameification would be a good way to encourage people to contribute more and correct data. For example games that are using geodata, like Pokemon Go or Geocaching,
      could add functionality to the osm data. People could be attracted by leveling up or get other benefits for the game.  
    - Because nowadays google maps is very widely used and people can easily add amenities etc. via google, it would be great if that data could be merged into the OSM data.


#!/usr/bin/python

################################################################################
# MAP SCHOOLS
#
# Reads text file containing the name of a Vancouver secondary school
# on each line.  Plots the schools on a Google map.

import googlemaps
import gmplot
import os
from jinja2 import Environment, FileSystemLoader
from pprint import pprint

# Configuration.
schoolsFilename = 'schools.txt'
apiKeyFilename = '/bsx/keys/google-eihsu.bsx-1.txt'
searchCenter = (49.2638865,-123.1122975)  # Suite Genius
searchRadiusM = 50000  # Maximum Value
mapCenter = searchCenter
mapZoom = 12
mapEdgeWidth = 10
departureEpochTime = 1464127800 # 24 May 2016, 3:10pm in Vancouver

# Read license key for google maps.
with open(apiKeyFilename) as f:
  k = f.readline().rstrip()
  gmaps = googlemaps.Client(key=k)

# Read schools.
with open(schoolsFilename) as f:
  schoolNames = f.read().splitlines()

# FIXTHIS
schoolNames = schoolNames[0:4]

print "Read " + str(len(schoolNames)) + " school names."

schools = []

# Search for schools under Google Maps API.
for schoolName in schoolNames:
  if (schoolName == 'South Hill Education Centre'):
    geoResp = gmaps.places_nearby(searchCenter,
                               radius=searchRadiusM,
                               name=schoolName)
  else:
    geoResp = gmaps.places_nearby(searchCenter, keyword='school',
                               radius=searchRadiusM,
                               name=schoolName, 
                               type='school')

  # Process results if any.
  results = geoResp['results']
  if (len(results) < 1):
    print "No results for '" + schoolName + "'."
  else:
    res = results[0]

    # Transit distance/time.
    transResp = gmaps.directions(res['name'] + ', Vancouver BC Canada',
                                 'Suite Genius Mt. Pleasant, Vancouver BC Canada',
                                 mode='transit',
                                 traffic_model='best_guess',
                                 departure_time=departureEpochTime)
    if (len(transResp) > 0):
      tRes = transResp[0]['legs'][0]
      transitDistance = tRes['distance']['text']
      transitTime = tRes['duration']['text']
    else:
      transitDistance = 'unknown'
      transitTime = 'unknown'

    # Driving distance/time.
    # STARTHERE (update transit, too.)  Search is giving bad results, try to use actual place_id.
    driveResp = gmaps.directions(res['name'] + ', Vancouver, BC Canada',
                                 'Suite Genius Mt. Pleasant, Vancouver BC Canada',
                                 mode='driving',
                                 traffic_model='best_guess',
                                 departure_time=departureEpochTime)
    if (len(driveResp) > 0):
      dRes = driveResp[0]['legs'][0]
      drivingDistance = dRes['distance']['text']
      drivingTime = dRes['duration']['text']
    else:
      drivingDistance = 'unknown'
      drivingTime = 'unknown'

    print res['name']
    print transitDistance
    print transitTime
    print drivingDistance
    print drivingTime

    # Write out records for consumption by template.
    schools.append({
      'coords':          res['geometry']['location'],
      'id':              res['id'],
      'name':            res['name'],
      'place_id':        res['place_id'],
      'reference':       res['reference'],
      'transitDistance': transitDistance,
      'transitTime':     transitTime,
      'drivingDistance': drivingDistance,
      'drivingTime':     drivingTime,
    })


# Render map from template via jinja.
pwd = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader('./templates'),
                     trim_blocks=True)
template = env.get_template('schools-map.html.template')

with open('schools-map.html', 'w') as f:
  f.write(template.render(schools=schools))

#!/usr/bin/python

################################################################################
# MAP SCHOOLS
#
# Reads text file containing the name of a Vancouver secondary school
# on each line.  Plots the schools on a Google map.

import googlemaps
from pprint import pprint

# Configuration.
schoolsFilename = 'schools.txt'
apiKeyFilename = '/bsx/keys/google-eihsu.bsx-1.txt'
searchCenter = (49.2638865,-123.1122975)  # Suite Genius
searchRadiusKm = 50000  # Maximum Value

# Read license key for google maps.
with open(apiKeyFilename) as f:
  k = f.readline().rstrip()
  gmaps = googlemaps.Client(key=k)

# Read schools.
with open(schoolsFilename) as f:
  schoolNames = f.read().splitlines()

schoolNames = schoolNames[0:4]

print "Read " + str(len(schoolNames)) + " school names."

schools = []

# Look up schools.
for schoolName in schoolNames:
  resp = gmaps.places_nearby(searchCenter, keyword='school',
                             radius=searchRadiusKm,
                             name=schoolName, 
                             type='school')

  # Process results if any.
  results = resp['results']
  if (len(results) < 1):
    print "No results for '" + schoolName + "'."
  else:
    res = results[0]
    schools.append({
      'coords':    res['geometry']['location'],
      'id':        res['id'],
      'name':      res['name'],
      'place_id':  res['place_id'],
      'reference': res['reference']
    })


pprint(schools)

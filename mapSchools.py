#!/usr/bin/python

################################################################################
# MAP SCHOOLS
#
# Reads text file containing the name of a Vancouver secondary school
# on each line.  Plots the schools on a Google map.
import sys
import googlemaps
import os
from jinja2 import Environment, FileSystemLoader
from pprint import pprint

# Configuration.
schoolsFilename = 'schools.txt'
apiKeyFilename = '/bsx/keys/google-eihsu.bsx-2018.txt'
searchCenter = (49.278474, -123.126393)  # Mangos
searchRadiusM = 50000  # Maximum Value
mapCenter = searchCenter
mapZoom = 12
mapEdgeWidth = 10
departureEpochTime = 1547161800  # 10 JAN 2019, 3:10pm in Vancouver

# Read license key for google maps.
with open(apiKeyFilename) as f:
  k = f.readline().rstrip()
  gmaps = googlemaps.Client(key=k)

# Read schools.
with open(schoolsFilename) as f:
  schoolNames = f.read().splitlines()

print "Read " + str(len(schoolNames)) + " school names; processing..."
schools = []

# Search for schools under Google Maps API.
for schoolName in schoolNames:
  print "Processing {}".format(schoolName)
  if (schoolName == 'King George Secondary School'):
    geoResp = gmaps.places_nearby(searchCenter,
                                  radius=searchRadiusM,
                                  name="King George Secondary School Tennis Courts")
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
                                 'Mangos Lounge, Vancouver BC Canada',
                                 mode='transit',
                                 traffic_model='best_guess',
                                 departure_time=departureEpochTime)
    if (len(transResp) > 0):
      tRes = transResp[0]['legs'][0]
      transitDistance = tRes['distance']
      transitTime = tRes['duration']
    else:
      transitDistance = {'text': 'unknown', 'value': '-1'}
      transitTime = {'text': 'unknown', 'value': '-1'}

    # Driving distance/time.
    driveResp = gmaps.directions(res['name'] + ', Vancouver, BC Canada',
                                 'Mangos Lounge, Vancouver BC Canada',
                                 mode='driving',
                                 traffic_model='best_guess',
                                 departure_time=departureEpochTime)
    if (len(driveResp) > 0):
      dRes = driveResp[0]['legs'][0]
      drivingDistance = dRes['distance']
      drivingTime = dRes['duration']
    else:
      drivingDistance = {'text': 'unknown', 'value': '-1'}
      drivingTime = {'text': 'unknown', 'value': '-1'}

    print res['name'].replace("'", "\\\'"),
 
    print transitDistance
    print transitTime
    print drivingDistance
    print drivingTime

    # Write out records for consumption by template.
    schools.append({
      'coords':            res['geometry']['location'],
      'id':                res['id'],
      'name':              res['name'].replace("'","\\\'"),
      'place_id':          res['place_id'],
      'reference':         res['reference'],
      'transitDistance':   transitDistance['text'],
      'transitDistanceKm': round(float(transitDistance['value']) / 1000.0, 1),
      'transitTime':       transitTime['text'],
      'transitTimeM':      int(round(float(transitTime['value']) / 60.0, 0)),
      'drivingDistance':   drivingDistance['text'],
      'drivingDistanceKm': round(float(drivingDistance['value']) / 1000.0, 1),
      'drivingTime':       drivingTime['text'],
      'drivingTimeM':      int(round(float(drivingTime['value']) / 60.0, 0))
    })

# Render map html from template via jinja.
pwd = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader('./templates'),
                     trim_blocks=True)
template = env.get_template('schools-map.html.template')

with open('schools-map.html', 'w') as f:
  f.write(template.render(schools=schools, key=k))

# Write out text report.
def summaryStr( lst ):
  "Given list of floats, compile a string summarizing min, max, an avg of its elements."
  return str(min(lst)) + " / " + str(max(lst)) + " / " + str(round(sum(lst) / len(lst), 1))


with open('schools-distances.txt', 'w') as f:
  f.write("# Travel from schools to Suite Genius, at 3:10pm on a weekday.\n")
  f.write("# Distances in kilometers, times in minutes.\n")
  transTimes = []
  transDists = []
  driveTimes = []
  driveDists = []
  for s in schools:
    transTimes.append(s['transitTimeM'])
    transDists.append(s['transitDistanceKm'])
    driveTimes.append(s['drivingTimeM'])
    driveDists.append(s['drivingDistanceKm'])
    f.write("School:                  " + s['name'] + "\n")
    f.write("Transit/Drive Time:      ")
    f.write(str(s['transitTimeM']) +  " / " + str(s['drivingTimeM']) + "\n")
    f.write("Transit/Drive Distance:  ")
    f.write(str(s['transitDistanceKm']) + " / " + str(s['drivingDistanceKm']) + "\n")
    f.write("\n")

  f.write("Transit Time Min/Max/Avg:  " + summaryStr(transTimes) + "\n")
  f.write("Drive Time Min/Max/Avg:    " + summaryStr(driveTimes) + "\n")
  f.write("\n")
  f.write("Transit Distance Min/Max/Avg:  " + summaryStr(transDists) + "\n")
  f.write("Drive Distance Min/Max/Avg:    " + summaryStr(driveDists) + "\n")

print "Done."
print "Wrote 'schools-map.html' and 'school-distances.txt'."

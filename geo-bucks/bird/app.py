from flask import Flask, render_template, request, jsonify
import requests, os
from datetime import date
from datetime import datetime, timedelta
from time import gmtime, strftime

app = Flask(__name__)

api_cache = {}

r_ip= 'http://172.22.150.49'
chrys_ip = 'http://172.22.150.44'
kc_ip = 'http://172.22.150.10'

register = {
    'port' : '21500',
    'ip' : kc_ip,
    'name': 'bird',
    'creator': 'Rochelle Tham',
    'tile': "Birds Recently Sighted in Current Location's State",
    'dependencies' : [                          # geographical IM
      {
        'port' : '23000',             
        'ip' : kc_ip,
        'dependencies' : []
      }
    ]
}
# run on cs240 server
requests.put('http://cs240-adm-01.cs.illinois.edu:5000/microservice', json=register)
# requests.put('http://127.0.0.1:5000/microservice', json = register)


#check on this 
@app.route('/microservice', methods=['DELETE'])
def del_IM():
  requests.delete('http://cs240-adm-01.cs.illinois.edu:5000/microservice', json = { 
    'port' : '21500',
    'ip' :  kc_ip
  }) 


#example coordinate that doesn't have weather info: 34.1125,23
# cs240 coord: 40.1125,-88.2284

# Route for "/MIX" (middleware):
@app.route('/')
def POST_birds():
  # used for the ebird API call
  geo_data = request.get_json()
  if (geo_data is None):
    return jsonify({"Geo IM didn't return valid location data.": {}}),200
  if ('state' not in geo_data):
    return jsonify({"Geo IM didn't return valid state data.": {}}),200

  regionCode = geo_data['state']

  # ebird code
  url = f"https://api.ebird.org/v2/data/obs/{regionCode}/recent"

  payload={}
  headers = {
    'X-eBirdApiToken': 'i1ttikpucloc'
  }

  key = regionCode

  # cache check
  #today's date to be used in the API request
  today = datetime.today()
  mdy = today.strftime("%m/%d/%Y").split("/")
  # get the month, day, and year 
  m = mdy[0]
  d = mdy[1]
  y = mdy[2]

  if (key in api_cache): 
    if (api_cache[key]['Date'] == f"{m}, {d}, {y}"):
      print(f"Returning saved json. {api_cache[key]['Date']} = {m}, {d}, {y}")
      return api_cache[key]['info'], 200

  api_cache[key] = {}                   # didn't have a cached json for this state

  response = requests.request("GET", url, headers=headers, data=payload)
  data = response.json()
  if data == None or data == '':
    print('returned empty data json')
    return {}, 404
  print(response.headers)
  bird_list = []

  print("DATA HERE", data)
  # error checking
  if (len(data) == 0):
    return jsonify({"Couldn't get any bird data": {}}),200
  if ('errors' in data):
    return jsonify({"Bird API failed to provide bird data": {}}),200


  for i in range(len(data[0])):
    bird_list.append(f"{data[i]['comName']} ({data[i]['sciName']})")
   
  # making the api_cache[key]['Date'] same format as "m, d, y" string
  date = response.headers.get('Date').split(" ")
  datetime_month = datetime.strptime(date[2], "%b")
  month = datetime_month.month 
  api_cache[key]['Date'] = f"{month}, {date[1]}, {date[3]}"
  api_cache[key]['info'] = jsonify({"Birds Found in the State" : bird_list})

  return api_cache[key]['info'], 200
  

@app.after_request
def cache_control_header(response):
  print("after request")
  response.cache_control.max_age = 3600
  response.headers["Age"] = 60
  print(response.headers)
  return response




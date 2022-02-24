from flask import Flask, render_template, request, jsonify
import requests
import os
from datetime import date
from datetime import datetime, timedelta
from time import gmtime, strftime

app = Flask(__name__)

r_ip= 'http://172.22.150.49'
chrys_ip = 'http://172.22.150.44'
kc_ip = 'http://172.22.150.10'

register = {
    'port' : '14000',
    'ip' : kc_ip,
    'name': 'Pollution',
    'creator': 'Kruthi Challa',
    'tile': 'Pollution Data of Specified Coordinates',
    'dependencies' : [
      {
      'port' : '23000',
      'ip' : kc_ip,
      'dependencies' : []
      }
    ]
}
requests.put('http://cs240-adm-01.cs.illinois.edu:5000/microservice', json=register)

#requests.put('http://127.0.0.1:5000/microservice', json = register)

api_cache = {}

#diff coordinates: 17.4344, 78.3866

# example:
# api_cache = {
#   (0,0): 
#     {
#       'date': 'Fri, 03 Dec 2021 04:55:49 GMT',
#       'age': 0,
#       'max-age': 0,
#       'info': ""          # the saved json from previous api call
#     }
# }

# cs240 coord: 40.1125,-88.2284

@app.route('/microservice', methods=['DELETE'])
def del_IM():
  requests.delete('http://cs240-adm-01.cs.illinois.edu:5000/microservice', json = { 
    'port' : '18000',
    'ip' :  kc_ip
  })
 

# Route for "/MIX" (middleware):
@app.route('/')
def POST_pollution():
  geo_data = request.get_json()

  print(geo_data)

  if (geo_data is None):
    return jsonify({"Geo IM didn't return valid location data.": {}}),200
  if ('city' not in geo_data):
    return jsonify({"Geo IM didn't return valid city data.": {}}),200
  city = geo_data['city']
  print(city)

  key = city


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

  
  pollution_url = "https://api.ambeedata.com/latest/by-city"
  querystring = {"city":city, "limit" :1}
  headers = {
      'x-api-key': "f61848672a9f85c7df8fce68f66f2c7f9bd2cf7641340b5ceb3ff4896dcaec84",
      'Content-type': "application/json"
      }
  print("***calling pollution api***")
  response = requests.request("GET", pollution_url, headers=headers, params=querystring)

  print("response:", response)

  pollution_data = response.json()
  print("pollution_data", pollution_data)

  if (pollution_data["message"] != "success"):
    return jsonify({"Sorry there is no pollution data for this city!": {}}), 200
  #print("stations:", stations)
  #OZONE = pollution_data["stations"]["OZONE"]
  stations = pollution_data["stations"]
  
  pollution_dict = {}

  for i in range(len(stations)):
    pollution_dict[i] = stations[i]

  print(pollution_dict)

  headers = response.headers
  #print("POLLUTION HEADERS: ", headers)
  date = response.headers.get('Date')
  #print("date", date)

  # making the api_cache[key]['Date'] same format as "m, d, y" string
  date = response.headers.get('Date').split(" ")
  datetime_month = datetime.strptime(date[2], "%b")
  month = datetime_month.month 
  api_cache[key]['Date'] = f"{month}, {date[1]}, {date[3]}"
  print("pollutiondict : ", pollution_dict)
  api_cache[key]['info'] = pollution_dict
    
  # return api_cache[key]['info'], 200
  return pollution_dict,200
  
@app.after_request
def cache_control_header(response):
  print("after request")
  response.cache_control.max_age = 3000
  response.headers["Age"] = 1
  # print(response.headers)
  return response


from flask import Flask, render_template, request, jsonify
import requests, os, time
from datetime import date
from datetime import datetime, timedelta
from time import gmtime, strftime

app = Flask(__name__)

r_ip= 'http://172.22.150.49'
chrys_ip = 'http://172.22.150.44'
kc_ip = 'http://172.22.150.10'

register = {
    'port' : '21550',
    'ip' : kc_ip,
    'name': 'holiday',
    'creator': 'Rochelle Tham',
    'tile': "Current Location's National Holiday",
    'dependencies' : [                          # geographical IM
      {
        'port' : '23000',             
        'ip' : kc_ip,
        'dependencies' : []
      }
    ]
}

requests.put('http://cs240-adm-01.cs.illinois.edu:5000/microservice', json=register)

# requests.put('http://127.0.0.1:5000/microservice', json = register)

api_cache = {}

#check on this 
@app.route('/microservice', methods=['DELETE'])
def del_IM():
  requests.delete('http://cs240-adm-01.cs.illinois.edu:5000/microservice', json = { 
    'port' : '21550',
    'ip' :  kc_ip
})


#example coordinate that doesn't have weather info: 34.1125,23
# cs240 coord: 40.1125,-88.2284



# Route for "/MIX" (middleware):
@app.route('/')
def POST_arcgis():
  geo_data = request.get_json()
  # country used for the holiday API call 
  if (geo_data is None):
    return jsonify({"Geo IM didn't return valid location data.": {}}),200
  if ('country' not in geo_data):
    return jsonify({"Geo IM didn't return valid country data.": {}}),200
  country = geo_data['country']

  #today's date to be used in the API request
  today = datetime.today()
  mdy = today.strftime("%m/%d/%Y").split("/")
  # get the month, day, and year 
  m = mdy[0]
  d = mdy[1]
  y = mdy[2]
  
  # cache check
  key = (country, m, d, y)               # key that will be used in our api_cache
  if (key in api_cache): 
    if ('Date' in api_cache[key]):
      if (api_cache[key]['Date'] == f"{m}, {d}, {y}"):
        print(f"Returning saved json. {api_cache[key]['Date']} = {m}, {d}, {y}")
        print("LINE 64", jsonify({"Today's holiday": api_cache[key]['info']}))
        return jsonify({"Today's holiday": api_cache[key]['info']}), 200

  api_cache[key] = {}                   # didn't have a cached json for this country/y/m/d
  
  # call the holiday API
  response = requests.get(f"https://holidays.abstractapi.com/v1/?api_key=359bc9ee5b7b4a1f8bce208a4efc3e3e&country={country}&year={y}&month={m}&day={d}")
  response_json = response.json()
  print(response_json)

  if ('error' in response_json):
    return jsonify({"Holiday API couldn't return valid response for this country": {}}), 200
  # handle error
  if (response.status_code == 400):
    return jsonify({"Holiday API couldn't return valid response for this coordinate.": {}}), 200
  
  # saving to cache
  print(response.headers)
  # making the api_cache[key]['Date'] same format as "m, d, y" string
  date = response.headers.get('Date').split(" ")
  datetime_month = datetime.strptime(date[2], "%b")
  month = datetime_month.month 
  api_cache[key]['Date'] = f"{month}, {date[1]}, {date[3]}"

  if len(response_json) == 0:
    api_cache[key]['info'] = "There is no national holiday today in this location."
    print(api_cache)
    return jsonify({'holiday info': "There is no national holiday today in this location."}), 200

  api_cache[key]['info'] = response_json
  return jsonify({"Today's holiday": api_cache[key]['info']}), 200
  
@app.after_request
def cache_control_header(response):
  print("after request")
  response.cache_control.max_age = 3600
  response.headers["Age"] = 60
  print(response.headers)
  return response

import json
from flask import Flask, render_template, request, jsonify
import requests

import os, time, re
from datetime import datetime, timedelta, date
from time import gmtime, strftime

def convert_to_datetime(input):     #2021-10-29T17:00:00
  year = int(input[:4])
  month = int(input[5:7])
  day = int(input[8:10])
  return datetime(year, month, day, int(input[11:13]), int(input[14:16]), int(input[17:19]))

app = Flask(__name__)


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
api_cache = {}

r_ip= 'http://172.22.150.49'
chrys_ip = 'http://172.22.150.44'
kc_ip = 'http://172.22.150.10'


register = {
    'port' : '22000',
    'ip' : kc_ip,
    'name': 'weather',
    'creator': 'Rochelle Tham',
    'tile': "Today's Forecast",
    'dependencies' : []
}


#example coordinate that doesn't have weather info: 34.1125,23
# cs240 coord: 40.1125,-88.2284

#class server 
requests.put('http://cs240-adm-01.cs.illinois.edu:5000/microservice', json=register)
# requests.put('http://127.0.0.1:5000/microservice', json = register)

#check on this 
@app.route('/microservice', methods=['DELETE'])
def del_IM():
  requests.delete('http://cs240-adm-01.cs.illinois.edu:5000/microservice', json = { 
    'port' : '22000',
    'ip' :  kc_ip
  }) 
  

# Route for "/MIX" (middleware):  
# @app.route('/<location>')
@app.route('/')
def POST_weather():
  req_data = request.get_json()
  lat = req_data["latitude"]
  long = req_data["longitude"]
  location = f"{lat},{long}"
  key = location
  if (key in api_cache): 
    if (len(api_cache[key]) == 0):       # the api couldn't return a valid response
      print("the api couldn't return a valid response, returning {}")
      return api_cache[key],200               # returns {}
    api_cache[key]['age'] = calc_age(api_cache[key]['date'])
    if ('age' in api_cache[key] and 'max-age' in api_cache[key]):
      if (api_cache[key]['age'] <= api_cache[key]['max-age']):
        print("returning saved json.", f"age: {api_cache[key]['age']}", f"max age: {api_cache[key]['max-age']}")
        return api_cache[key]['info'], 200
  print(location)
  api_cache[key] = {}
  
  # weather API call, get weather info.
  start_weather_api = requests.get(f"https://api.weather.gov/points/{location}")
  # start_weather_api = requests.get(f"https://api.weather.gov/points/{lat},{long}") # 40.1125,-88.2284
  start_weather_json = start_weather_api.json()

  # ensure that the given location is valid.
  if (type(start_weather_json) == dict and "status" in start_weather_json.keys()):
    print("Could not retrieve weather data for this location")
    return {}, 200
  
  # gets the url for forecast on hourly basis, includes weekday and more details
  forecast_url = start_weather_json["properties"]["forecast"]
  if (forecast_url is None):
    print("API doesn't have an hourly forecast for this coordinate.")
    return jsonify({"API doesn't have an hourly forecast for this coordinate.": {}}), 200

  weather_API = requests.get(forecast_url)

  # getting the max age
  print("WEATHER:", weather_API.headers)
  cache_control = weather_API.headers.get('Cache-Control').split(",")

  temp_max_age = cache_control[1].strip(" max-age=")
  # in case the cache doesn't have the max-age
  if ('ust-revalidat' == temp_max_age):
    api_cache[key]["max-age"] = 3600
  else:
    api_cache[key]["max-age"] = int(temp_max_age)
  
  weather_data = weather_API.json()

  # ensure that the new forecast json has data in it
  if (type(weather_data) == dict and "status" in weather_data.keys()):
    return {}, 200

  # getting current date and time. 
  curr_time = datetime.now()
  # used when comparing current time and weather time stamps
  delta = float('inf')  

  # iterate through all the weather time stamps
  for i in range(len(weather_data["properties"]["periods"])):
    weather_day_and_time = weather_data["properties"]["periods"][i]["startTime"]

    # converts the weather time stamp to a datetime object
    weather_time_stamp = convert_to_datetime(weather_day_and_time)
   
    # use total_seconds() to avoid negative values
    time_stamp_diff =  (weather_time_stamp - curr_time).total_seconds()
    
    if (abs(time_stamp_diff) <= delta):           # update the minimum delta between forecast time and current time
      delta = time_stamp_diff
      period_index = i
      
  # change the chosen weather timestamp string to a datetime object
  forecast_time = convert_to_datetime(weather_data["properties"]["periods"][period_index]["startTime"])
  wind_speed = weather_data["properties"]["periods"][period_index]["windSpeed"]
  forecast = weather_data["properties"]["periods"][period_index]["detailedForecast"]
  print("HERE", forecast)

  print("cache: ", api_cache)
  # setting custom response headers when returning to middleware
  # age and max age headers
  api_cache[key]['date'] = weather_API.headers.get('Date')
  api_cache[key]['age'] = calc_age(weather_API.headers.get('Date'))
  api_cache[key]["info"] = jsonify(
                                {"forecast description": f"{forecast}",
                                "wind speed": f"{wind_speed}"})
  print("HEREEEEE", api_cache[key]['age'], api_cache[key]["max-age"])
  return api_cache[key]["info"], 200

@app.after_request
def cache_control_header(response):
  print("after request")
  print(response.headers)
  response.cache_control.max_age = 3600
  response.headers["Age"] = 60
  print(response.headers)
  return response



# example: responseDate  = 'Sun, 28 Nov 2021 23:09:58 GMT'
# Mon, 29 Nov 2021 01:48:35 GMT
def calc_age(responseDate):
  curr = datetime.now()
  # change current time to gmtime
  curr_gmt = time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime())
  
  #convert current time string back to datetime object
  curr_datetime = datetime.strptime(curr_gmt,"%a, %d %b %Y %I:%M:%S %p %Z")
  
  # 1. change date GMT format to datetime object.
  response_datetime = datetime.strptime(responseDate,"%a, %d %b %Y %H:%M:%S %Z")

  # 2. find difference between [ now - request time]
  age = (curr_datetime - response_datetime).total_seconds()
  if (age < 0):
    age = 0
  age = int(age)
  return age

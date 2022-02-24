from flask import Flask, render_template, request, jsonify
import requests

import re
import os, time

from datetime import datetime, timedelta, date
from time import gmtime, strftime

# config = {
#     "DEBUG": True,          # some Flask specific configs
#     "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
#     "CACHE_DEFAULT_TIMEOUT": 300
# }

app = Flask(__name__)

# tell Flask to use the above defined config
# app.config.from_mapping(config)
# cache = Cache(app)

# saves the IM's response jsons
# adjust it so that we have response jsons for each location
#store the coord location, the time when request call was made, IM response, max age 
cache_dict = {
  "sunset": "",
  "restaurant" : "",
  "weather": "",
  "geo": "", 
  "bird": "", 
  "holiday": "",
  "news": "",
  "pollution": ""
}

# saves the IM response
res_dict = {
  "sunset": "",
  "restaurant" : "",
  "weather": "",
  "geo": "", 
  "bird": "", 
  "holiday": "",
  "news": "",
  "pollution": ""
}
# server urls
ss_server_url = os.getenv('SUNSET_SUNRISE_MICROSERVICE_URL')
restaurant_url= os.getenv('RESTAURANT_MICROSERVICE_URL')
weather_server_url = os.getenv('WEATHER_MICROSERVICE_URL')
geo_server_url = os.getenv('GEO_MICROSERVICE_URL')
bird_server_url = os.getenv('BIRD_MICROSERVICE_URL')
holiday_server_url = os.getenv('HOLIDAY_MICROSERVICE_URL')
news_server_url = os.getenv('NEWS_MICROSERVICE_URL')
pollution_server_url = os.getenv('POLLUTION_MICROSERVICE_URL')


app.config['JSON_SORT_KEYS'] = False
@app.before_request
def check_cache():
  print("before request")


# Route for "/" (frontend):
@app.route('/')
def index():
  return render_template("index.html")
  
@app.route('/MIX', methods=["POST"])
def POST_IMS():
  print("during request")
  location = request.form["location"]
  location = location.replace(" ", "")
  print(location)
  server_dict = {
    "sunset": f'{ss_server_url}/{location}/',
    "restaurant" : f'{restaurant_url}/{location}/',
    "weather": f'{weather_server_url}/{location}/',
    "geo": f'{geo_server_url}/{location}/', 
    "bird": f'{bird_server_url}/{location}/', 
    "holiday": f'{holiday_server_url}/{location}/',
    "news": f'{news_server_url}/{location}/',
    "pollution": f'{pollution_server_url}/{location}/'
  }

  # for loop --> if the current entry is empty --> we just call the IM
  # if not empty --> we return the entry
  for key in cache_dict:
    if (len(cache_dict[key]) == 0):
      # call the IM that has no json saved
      print("we want to call the IM")
      response = requests.get(server_dict[key])        # server dict has all the server urls
      res_dict[key] = response                         # save IM response to res_dict
      cache_dict[key] = response.json()                # save IM response jsons to cache_dict
    else:
      # we already have a previous json stored, no need to call the IM
      continue  
  print("IN MAIN FUNCT", res_dict)
  return cache_dict, 200


''' 
function: check_age 
functionality: checks if response age > max-age, then we delete corr. json from cache dict. 
               Otherwise, we keep the response in the cache dict. Updates the age. 
Parmeters:
  key: name of IM 
  response: IM's response, also accessed by res_dict[key]
'''
def check_age(key, response):
  curr = datetime.now()
  # change current time to gmtime
  curr_gmt = time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime())
  
  #convert current time string back to datetime object
  curr_datetime = datetime.strptime(curr_gmt,"%a, %d %b %Y %I:%M:%S %p %Z")
  
  responseDate = response.headers['Date']
  # 1. change date GMT format to datetime object.
  response_datetime = datetime.strptime(responseDate,"%a, %d %b %Y %H:%M:%S %Z")

  # 2. find difference between [ now - request time]
  age = curr_datetime - response_datetime

  # 3. if [ now - request time] > max-age, then reset age back to 0 and then run request again. 
  # Otherwise don't call the IM and just return json in cache
  if ('Cache-Control' not in response.headers):
    response.headers["Cache-Control"] = 'public, max-age=253, s-maxage=3600'
    # response.cache_control.max_age = 3000
  cache_control = response.headers['Cache-Control'].split(",")
  max_age = cache_control[1].strip(" max-age=")

  print("AGE", age)
  # age = int(age.strftime("H%M%S"))

  age = int(age.total_seconds())
  print("age: ",age)

  if ('age' not in response.headers):
    response.headers['age'] = age
  if (age > int(max_age)):
    response.headers['age'] = 0     # we call the IM   
    print("after setting age to 0")
    cache_dict[key] = ""
    res_dict[key] = ""
    print("cleared the dictionaries")
  else: # don't call the IM and just return json in the cache
    response.headers['age'] = age   # we access the cache
    print("updated the age")
  

@app.after_request
def cache_control_header(response):
  print("after request")
  response.cache_control.max_age = 10
  print(response.headers)
  print("so far res dict includes:", res_dict)
  for key in res_dict:
    # in the case that we have no responses stored, no need to check age
    if type(res_dict[key]) == str and len(res_dict[key]) == 0:    
      continue     
    print(type(res_dict[key]))
    print(res_dict[key])
    check_age(key, res_dict[key])
  print("at end of after request", response)
  return response        # caching doesn't work when we do "return response"
 
  

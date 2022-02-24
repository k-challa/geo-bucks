#Restaurant Microservice by Chrysilla
import json
import time
import requests
import os, time, re
from datetime import datetime, timedelta, date
from time import gmtime, strftime


from flask import Flask, render_template, request, jsonify
from werkzeug.wrappers import response
app = Flask(__name__)

r_ip= 'http://172.22.150.49'
chrys_ip = 'http://172.22.150.44'
kc_ip = 'http://172.22.150.10'

register = {
    'port' : '26000',
    # 'ip' : chrys_ip,
    'ip': chrys_ip,
    'name': 'Restaurant',
    'creator': 'Chrysilla',
    'tile': 'Restaurant''s near me',
    'dependencies' : []

}
#register IM 

r=requests.put('http://cs240-adm-01.cs.illinois.edu:5000/microservice', json=register)
print(r)
#requests.put('http://127.0.0.1:5000/microservice', json = register)

#Delete IM 
@app.route('/microservice', methods=['DELETE'])
def del_IM():
  requests.delete('http://cs240-adm-01.cs.illinois.edu:5000/microservice', header = {'Content-Type' : 'application/json'}, json = { 
    'port' : '26000',
    'ip' :  chrys_ip})
  return "Success",200

 
# example:
# places_api_cache = {
#   (0,0): 
#     {
#       'date': 'Fri, 03 Dec 2021 04:55:49 GMT',
#       'age': 0,
#       'max-age': 0,
#       'info': ""          # the saved json from previous api call
#     }
# }
api_cache = {}
def search_places_by_coordinate(location):
        endpoint_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius=500&type=restaurant&key=AIzaSyBcvlcjdc1V8AV4nxYexpZVyzhwtc6PEZU"
        places = []
        
        search_places_response = requests.get(endpoint_url)#, params = params)
        p_data=search_places_response.json()
        #error checking
        if (p_data is None):
            print("p_data is none")
            return []
        #print(p_data)
        places.extend(p_data['results'])
        #search_places_response.cache_control.max_age = 84000
        #print("search places headers: ",search_places_response.headers)
        return places
#

def get_place_details(place_id):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            'placeid': place_id,
            'fields': 'name,formatted_address,international_phone_number,website,rating,review',
            'key': "AIzaSyBcvlcjdc1V8AV4nxYexpZVyzhwtc6PEZU"
        }
        get_place_response = requests.get(endpoint_url, params = params)
        place_details_data = get_place_response.json()

        #error checking
        if (place_details_data is None):
            print("place_details is none")
            return {}
        #print(place_details_data)
        #print("place details headers: ",get_place_response.headers)
        place_details = place_details_data['result']
        #print(place_details)
        return place_details
#  
# Route for Restaurant IM
@app.route('/')
#@app.route('/<location>/', methods=['GET'])
def POST_restaurant():#location):
    req_data = request.get_json()
    print("req_data",req_data)
    lat = req_data["latitude"]
    long = req_data["longitude"]
    location = f"{lat},{long}"
    key=location
    if (key in api_cache):
        
        if (len(api_cache[key]) == 0):   
            # the api couldn't return a valid response
            print("the api couldn't return a valid response, returning {}")
            return api_cache[key],200 #  returns {}
        if (api_cache[key]['date']!='' or (len(api_cache[key]['date'])!=0)):
            age= (datetime.now()-api_cache[key]['date']).total_seconds()
            age = int(age)
            if (age < 0):
                age = 0
        api_cache[key]['age']=age
        if (api_cache[key]['age'] <= api_cache[key]['max-age']):
            #print("returning saved json.", f"age: {api_cache[key]['age']}", f"max age: {api_cache[key]['max-age']}")
            print("cached response")
            return api_cache[key]['info'], 200

    p={}
    #location = request.form["location"]
    #location = location.replace(" ", "")
    places1 = search_places_by_coordinate(location)

    #error checking
    if (len(places1) == 0):
        print("places1 has length 0")
        return jsonify({"API failed to return reviews":{}}), 200
    # print("places",places1)
    
    c=0
    for place in places1[0:5]:
      c+=1
      places={}
    #   print("\n",place['place_id'])
      details = get_place_details(place['place_id'])

      #error handling
      if (len(details) == 0):
          print("API failed to return reviews")
          return jsonify({"API failed to return reviews":{}}), 200

      #print(f'Restaurant {c}',details)
      try:
          website = details['website']
        #   print("website",website)
      except KeyError:
          website = "NA"
 
      try:
          name = details['name']
        #   print("name",name)
      except KeyError:
          name = "NA"
 
      try:
          address = details['formatted_address']
      except KeyError:
          address = "NA"
 
      try:
          phone_number = details['international_phone_number']
      except KeyError:
          phone_number = "NA"
 
      try:
          reviews = details['reviews']
      except KeyError:
          reviews = []
      try:
          rating = place['rating']
      except KeyError:
          rating ="NA"
      try:
          price_level=place['price_level']
      except KeyError:
          price_level ="NA"

      places["Name:"]= name
      places["Website:"]=website
      places["Address:"]=address
      places["Phone Number:"]=phone_number
      places["rating"]=rating
      places["price_level"]=price_level
      count=0
      r={}
      rev={}
      
      for review in reviews:
          count+=1
          r["author_name"] = review['author_name']
          r["rating"] = review['rating']
          r["text"] = review['text']
          r["time"] = review['relative_time_description']
      rev[f'review ']=r
      places["reviews"]=rev
      p[f'Restaurant {c}']=places
    # setting custom response headers when returning to middleware
    # age and max age headers
    
    #print(datetime.now())
    d={'date':datetime.now(),'max-age':21000,'info':jsonify(p),'age':0}
    if key not in api_cache:
        api_cache.update({key: d})
    #api_cache[key]['date'] = datetime.now()
    #api_cache[key]['age'] = 21000
    #api_cache[key]["info"] = jsonify(p)
    #print(api_cache[key]['age'], api_cache[key]["max-age"])
    #print(api_cache)
    print(p)
    print("RESPONSE", jsonify(p))
    return jsonify(p),200

'''def calc_age(responseDate):
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
'''
@app.after_request
def cache_control_header(response):
  print("after request")
  response.cache_control.max_age = 7200
  response.headers["Age"] = 1
  print(response.headers)
  return response
  

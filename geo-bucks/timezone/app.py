# Timezone Microservice/ Chrysilla
import requests
from flask import Flask, render_template, request, jsonify
from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta
app = Flask(__name__)

r_ip= 'http://172.22.150.49'
chrys_ip = 'http://172.22.150.44'
kc_ip = 'http://172.22.150.10'

register = {
    'port' : '21000',
    'ip' : kc_ip,
    # 'ip' : chrys_ip,
    'name': 'Timezone',  
    'creator': 'Chrysilla',
    'tile': 'Timezone and Current Time',
    'dependencies' : []

}
#Register IM

requests.put('http://cs240-adm-01.cs.illinois.edu:5000/microservice', json=register)

@app.route('/microservice', methods=['DELETE'])
def del_IM():
  requests.delete('http://cs240-adm-01.cs.illinois.edu:5000/microservice', json = { 
    'port' : '21000',
    'ip' :  kc_ip
  }) 

#requests.put('http://127.0.0.1:5000/microservice', json = register)
#Cache
api_cache={}
#Timezone IM
#@app.route('/')#
#@app.route('/<lat>/<lng>/')
@app.route('/')
def POST_timezone():
  req_data = request.get_json()
  lat = req_data["latitude"]
  lng = req_data["longitude"]
  location = f"{lat},{lng}"
  key=location
  if (key in api_cache): 
    if (len(api_cache[key]) == 0):   
      # the api couldn't return a valid response
      print("the api couldn't return a valid response, returning {}")
      return api_cache[key] #  returns {}
    if (api_cache[key]['date']!='' or (len(api_cache[key]['date'])!=0)):
      age= (datetime.now()-api_cache[key]['date']).total_seconds()
      age = int(age)
      if (age < 0):
        age = 0
      api_cache[key]['age']=age
      if (api_cache[key]['age'] <= api_cache[key]['max-age']):
        #print("returning saved json.", f"age: {api_cache[key]['age']}", f"max age: {api_cache[key]['max-age']}")
        return api_cache[key]['info'], 200
  #calling timezone api
  print("***calling timezone api***")
  response = requests.get(f'http://api.timezonedb.com/v2.1/get-time-zone?key=PO8PNB3ZUPQV&format=json&by=position&lat={lat}&lng={lng}')
  tmz_data=response.json()
  if tmz_data["status"]=='FAILED':
    return {},404
  #tmz_data=response.json()
  #print(tmz_data)
  #getting offset in hours
  d={}
  #d["You're in "]=tmz_data['countryName']
  d[f"Timezone name "]=tmz_data['zoneName']
  tmz_offset=tmz_data['gmtOffset']/3600 
  dt=tmz_data['formatted']
  
  y=dt.split(" ")
  date=y[0]
  d["Today is "]= date
  d["The time is"]=y[1]
  d["Timezone abbreviation"]=tmz_data["abbreviation"]
  d["GMT Offset"]=tmz_offset
  d["latitude"]=lat
  d["longitude"]=lng
  # setting custom response headers when returning to middleware
    # age and max age headers
    
    #print(datetime.now())
  cache_dict={'date':datetime.now(),'max-age':1,'info':jsonify(d),'age':0}
  if key not in api_cache:
    api_cache.update({key: cache_dict})
    #api_cache[key]['date'] = datetime.now()
    #api_cache[key]['age'] = 21000
    #api_cache[key]["info"] = jsonify(p)
    print(api_cache[key]['age'], api_cache[key]["max-age"])
    print(api_cache)
    print(d)
  return jsonify(d),200

@app.after_request
def cache_control_header(response):
  print("after request")
  response.cache_control.max_age = 3600
  response.headers["Age"] = 1
  print(response.headers)
  return response

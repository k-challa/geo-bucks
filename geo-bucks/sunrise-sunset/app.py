#Sunrise Sunset Microservice Chrysilla
import requests
from flask import Flask, render_template, request, jsonify
from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta
import os
app = Flask(__name__)
api_cache={}

r_ip= 'http://172.22.150.49'
chrys_ip = 'http://172.22.150.44'
kc_ip = 'http://172.22.150.10'

register = {
    'port' : '24000',
    'ip' : kc_ip,
    # 'ip' : chrys_ip,
    'name': 'Sunrise-Sunset Time',
    'creator': 'Chrysilla',
    'tile': 'Sunrise Sunset Times',

    'dependencies' : [
        {
            'port' : '21000',
            'ip' : kc_ip,
            # 'ip' : chrys_ip,
            'dependencies' : []
            
        }
        
    ]
}

#Register IM

requests.put('http://cs240-adm-01.cs.illinois.edu:5000/microservice', json=register)

#requests.put('http://127.0.0.1:5000/microservice', json = register)


@app.route('/microservice', methods=['DELETE'])
def del_IM():
  requests.delete('http://cs240-adm-01.cs.illinois.edu:5000/microservice', json = { 
    'port' : '24000',
    'ip' :  kc_ip})


# Route Sunrise Sunset Microservice:
@app.route('/')
#@app.route('/<lat>/<lng>/')
def POST_sunset_sunrise():#lat,lng):
  
  d=request.get_json()#get timezone offset from timezone API not sure about this
  req_data = request.get_json()
  print("response",req_data)
  lat = req_data["latitude"]
  lng = req_data["longitude"]
  location = f"{lat},{lng}"
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
        return api_cache[key]['info'], 200
  #print(d)
  
  #timezone_server_url = os.getenv('TIMEZONE_MICROSERVICE_URL')
  #tz_r = requests.get(f'{timezone_server_url}/{lat}/{lng}/')
  #d=tz_r.json()
  if d == {}:
    return {},404
  #calling sunrise sunset api
  print("***calling sunrise sunset api***")
  response = requests.get(f'https://api.sunrise-sunset.org/json?lat={lat}&lng={lng}&date={d["Today is "]}')
  #print(response.headers)
  ss_data=response.json()
  #print(ss_data)
  if ss_data["status"]=='FAILED':
    return {},404
  #print(ss_data)
  #retriving sunrise info from json
  sunrise=ss_data["results"]["sunrise"]
  #converting string obj to datetime obj
  sunrise = datetime.strptime(sunrise, '%H:%M:%S %p')
  #changing the time by the offset to correct timezone
  sunrise = sunrise + timedelta(hours=d["GMT Offset"])
  #converting datetime obj to string obj
  sunrise = sunrise.strftime("%I:%M")
  print(f"sunrise {sunrise} AM")
  res={}
  res["Sunrise"] = f" {sunrise} AM"
  #retriving sunset info from json
  sunset =ss_data["results"]["sunset"]
  #print(sunset)
  #converting string obj to datetime obj
  sunset = datetime.strptime(sunset, '%H:%M:%S %p')
  #changing the time by the offset to correct timezone
  sunset = sunset + timedelta(hours=d["GMT Offset"])
  #converting datetime obj to string obj
  sunset = sunset.strftime("%H:%M")
  print(f"sunset {sunset} PM")
  res["Sunset"] = f"{sunset} PM"
  # setting custom response headers when returning to middleware
    
    #print(datetime.now())
  cache_dict={'date':datetime.now(),'max-age':3600,'info':jsonify(res),'age':0}
  if key not in api_cache:
    api_cache.update({key: cache_dict})
    #api_cache[key]['date'] = datetime.now()
    #api_cache[key]['age'] = 21000
    #api_cache[key]["info"] = jsonify(p)
    #print(api_cache[key]['age'], api_cache[key]["max-age"])
    print(api_cache)
  print(res)
  return jsonify(res), 200

@app.after_request
def cache_control_header(response):
  print("after request")
  response.cache_control.max_age = 3600
  response.headers["Age"] = 1
  print(response.headers)
  return response


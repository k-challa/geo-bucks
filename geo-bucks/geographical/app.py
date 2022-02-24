from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

r_ip= 'http://172.22.150.49'
chrys_ip = 'http://172.22.150.44'
kc_ip = 'http://172.22.150.10'

redirect = {
    'port' : '23000',
    'ip' : kc_ip,
    'name': 'Geographical',
    'creator': 'Kruthi',
    'tile': "Geographical Info",
    'dependencies':[]
}
#connects to cs240 server 
requests.put('http://cs240-adm-01.cs.illinois.edu:5000/microservice', json=redirect)
# requests.put('http://127.0.0.1:5000/microservice', json = redirect)

@app.route('/microservice', methods=['DELETE'])
def del_IM():
  requests.delete('http://cs240-adm-01.cs.illinois.edu:5000/microservice', json = { 
    'port' : '23000',
    'ip' :  kc_ip
  }) 

# Route for "/MIX" (middleware):
@app.route('/')
def POST_address():
  req_data = request.get_json()
  lat = req_data["latitude"]
  long = req_data["longitude"]
  location = f"{lat},{long}"
  print(location)
  parameters = {
      "key" : "LhmYcNXFbuoAxPYGvWWksTCGptF7KQIU", 
      "location" : location
  }

  response = requests.get('http://open.mapquestapi.com/geocoding/v1/reverse', params = parameters)
  print("geographical:", response.headers)
  data = response.json()['results']
  #city = info['results']
  print(data)

  if (len(data[0]['locations']) ==0):
    print("Could not find location for this coordinate.")
    return jsonify({"Could not find location for this coordinate.": {}})
  
  city = data[0]['locations'][0]['adminArea5']
  state = data[0]['locations'][0]['adminArea3']
  country = data[0]['locations'][0]['adminArea1']
  print(city)
  print(state)
  print(country)

  geo_dat = {"city": city, "state" : state, "country": country}

#check if city/state info is not existent, then remove from dictionary
  for key in geo_dat.copy():
      #print(key, '->', x[key])
      if len(geo_dat[key]) == 0:
          del geo_dat[key]
  
  return jsonify(geo_dat)


@app.after_request
def cache_control_header(response):
  print("after request")
  response.cache_control.max_age = 3000
  response.headers["Age"] = 1
  print(response.headers)
  return response


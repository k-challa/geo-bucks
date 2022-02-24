from flask import Flask, render_template, request, jsonify
import requests
import os
from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

app = Flask(__name__)

r_ip= 'http://172.22.150.49'
chrys_ip = 'http://172.22.150.44'
kc_ip = 'http://172.22.150.10'

register = {
    'port' : '19000',
    'ip' : kc_ip,
    'name': 'News',
    'creator': 'Kruthi Challa',
    'tile': 'Top Headlines of Country',

    'dependencies' : [
        {
            'port' : '23000',
            'ip' : kc_ip,
            'dependencies' : []
        }
    ]
}
# cs240 coord: 40.1125,-88.2284
requests.put('http://cs240-adm-01.cs.illinois.edu:5000/microservice', json=register)

requests.put('http://cs240-adm-01.cs.illinois.edu:5000/microservice', json=register)
# requests.put('http://127.0.0.1:5000/microservice', json = register)

#cached data for news API
news_api_cache = {}

@app.route('/microservice', methods=['DELETE'])
def del_IM():
  requests.delete('http://cs240-adm-01.cs.illinois.edu:5000/microservice', 
  header = {'Content-Type' : 'application/json'}, json = { 
    'port' : '19000',
    'ip' :  kc_ip})

# Route for "/MIX" (middleware):
@app.route('/')
def GET_country():
  
  #getting json from middleware
  #geo_data = request.get_json()

  # geo_server_url = os.getenv('GEO_MICROSERVICE_URL')
  # geo_r = requests.get(f'{geo_server_url}/{location}/')
  # geo = geo_r.json()

  geo_data = request.get_json()
  if (geo_data is None):
    return jsonify({"Geo IM didn't return valid location data.": {}}),200
  if ('country' not in geo_data):
    return jsonify({"Geo IM didn't return valid country data.": {}}),200

  country = geo_data['country']


  key = country
  curr_time = datetime.now()
  # print("time: ", (news_api_cache[key]['date']).total_seconds())

  if (key in news_api_cache): 
    if (len(news_api_cache[key]) == 0):   
      # the api couldn't return a valid response
      print("The API couldn't return a valid response, returning {}")
      return news_api_cache[key], 200 #  returns {}
    if (news_api_cache[key]['date'] != ' ' or (len(news_api_cache[key]['date']) != 0)):
      age = (curr_time - news_api_cache[key]['date']).total_seconds()
      age = int(age)
      if (age < 0):
        age = 0
      news_api_cache[key]['age'] = age
      if (news_api_cache[key]['age'] <= news_api_cache[key]['max-age']):
        #print("returning saved json.", f"age: {api_cache[key]['age']}", f"max age: {api_cache[key]['max-age']}")
        return news_api_cache[key]['info'], 200


  headlines_url = (f'http://newsapi.org/v2/top-headlines?country={country}&language=en&pageSize=10&apiKey=ecc291e19db44571afe8ff46e41cd31e') 
  #print("country", country)
  print("***calling news api***")

  response = requests.get(headlines_url)
  newsheadlines = response.json()
  print("status", newsheadlines["status"])

  if (newsheadlines["status"] != "ok"):
    return jsonify({"Sorry there are no top headlines in this country!": {}}), 200
  
  headers = response.headers
  #print("NEWS HEADERS: ", headers)
  
  articles = newsheadlines['articles']

  if (len(articles) == 0):
    return jsonify({"Sorry there are no top headlines in this country!": {}}), 200

  headlines_dict = {}

  for i in range(len(articles)):
    headlines_dict[i] = articles[i]['title']

  cache_dict = {'date':datetime.now(),'max-age':3600,'info':headlines_dict,'age':0}
  if key not in news_api_cache:
    news_api_cache.update({key: cache_dict})
    #api_cache[key]['date'] = datetime.now()
    #api_cache[key]['age'] = 21000
    #api_cache[key]["info"] = jsonify(p)
    #print(api_cache[key]['age'], api_cache[key]["max-age"])
    print(news_api_cache)

  return headlines_dict, 200

@app.after_request
def cache_control_header(response):
  print("after request")
  response.cache_control.max_age = 3600
  response.headers["Age"] = 1
  print(response.headers)
  return response



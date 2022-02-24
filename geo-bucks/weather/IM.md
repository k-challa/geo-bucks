# Weather IM by Rochelle Tham
This IM will provide basic weather information about the given location.     

## API Web Service used: National Weather Service (NWS) API
The National Weather Service provides open data for forecasts, alerts, observations, and other weather data.   

## Useful Links
Documentation can be find here: https://www.weather.gov/documentation/services-web-api    

## How the the API is Called
User must provide a location's latitude and longitude to get the location's weather data.    
When given the location's latitude and longitude, the following steps are used to retrive the weather data:
1. Insert the GPS coordinates into {location} parameter of url: https://api.weather.gov/points/{location}
2. Request weather json from the url stored in dictionary key: "forecast" 


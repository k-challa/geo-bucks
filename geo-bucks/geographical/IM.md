## Geographical IM by Kruthi Challa

This IM provides basic geographical information about the user-inputted location such as the city, state and country it's located in. 

### API used: Mapquest Geocoding API - Reverse Geocode

Reverse geocoding is the process of taking a latitude and longitude pair and providing the associated address, or nearest address point.

Example: 41.947239,-87.655636 returns 1060 W. Addison St., Chicago, IL 60613 

### Useful Links

Documentation can be found here: https://developer.mapquest.com/documentation/open/geocoding-api/reverse/get/

### How the API is called
1. Parameters `location` and API KEY must be provided when making a request to the API along with the URL. Location is the user-provided latitude and longitude. For example:

```
parameters = {
      "key" : YOUR_API_KEY, 
      "location" : location
}
response = requests.get('http://open.mapquestapi.com/geocoding/v1/reverse', params = parameters)
```
2. Retrieve city, state and country data from JSON output. 



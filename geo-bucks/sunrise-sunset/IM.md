# Timezone Sunset Sunrise Times IM by Chrysilla 
This IM will provide basic information about the current time,timezone name, sunrise and sunset for the given location.The sunset sunrise API returns a time in UTC. Inorder to display the accurate sunrise sunset times, the offset is usee which was retrived by timezone API call for the given location. 

## API Web Services used: 
1) TimezoneDB API:
The TimezoneDB API provides information such countries name, time zones, abbreviation, GMT offset, and Daylight Saving Time (DST) for any location. 
Sunset Sunrise API:
Provides users information about day length, twilight, sunrise and sunset times for any location of the world.

## Useful Links
Documentation can be found here for Timezone API: https://timezonedb.com/api  
Documentation can be found here for Sunset Sunrise API:https://sunrise-sunset.org/api

## How the the APIs are Called
1) Timezone
A location's latitude and longitude along with the API key must be provided to the timezonedb API.
The following steps are used to retrive the timezone data:

1. Insert the API key into {key} parameter
2. Set format parameter as json
3. Insert GPS coordinates into {lat},{lng} parameters into the API url as: http://api.timezonedb.com/v2.1/get-time-zone?key={key}&format=json&by=position&lat={lat}&lng={lng}
4. Retrive time zone name, abbreviation, GMT offset, current date time from json returned. 

2)Sunset Sunrise
A location's latitude and longitude along with the date must be provided to the sunrise sunset API.
The following steps are used to retrive the timezone data:

1. Insert GPS coordinates into {lat},{lng} and date into {date} parameters the API url as:https://api.sunrise-sunset.org/json?lat={lat}&lng={lng}&date={date}
2. Retrive sunrise time and sunset time from json returned.
3. The sunset sunrise API returns time in UTC. In order to display the sunrise sunset times in the locations timezone, the offset which was retrived by timezone API call for the given location  is used. 






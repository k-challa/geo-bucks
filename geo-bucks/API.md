# Project MIX: API Documentation
By Kruthi, Chrysilla, and Rochelle
## An high-level overview of how your implementation of MIX is designed
In our MIX implementation, our middleware takes the user inputted location data (latitude and longitude), which is then given to the different IM’s to use when calling the API’s. Each IM is run on a different port number and therefore different server urls. The middleware then returns a json of all the IM’s json data.  

## Technical details on the request and response APIs between your middleware and the IMs
The middleware initially retrieves the user-inputted location using a GET request and stores the response in the `location` attribute. Each IM sends a request to the respective microservice URL via a GET request and uses the `location` to retrieve information specific to that IM. This response is then stored in a json. The json responses from each IM are all combined into one json which is returned by the middleware.


## Technical details on the response API between the frontend and the middleware
The middleware will call the rendered template of index.html using `app.route(‘/’)`. Afterwards, the middleware will return a POST request which includes a combined json of all the IM’s json returns. 

## Technical details on how IMs are added and removed from MIX
To *add* an IM to the middleware, we would:
Include the IM’s server url
Call `requests.get` on the IM’s server url
To *remove* the IM from the middleware, we would not call `requests.get` on the IM’s server url and we need to make sure that the returned json of the middleware doesn’t include the IM’s json.     
We have the following dictionaries:
    * cache_dict: keeps the IM's response jsons
    * res_dict: keeps the IM's responses
    * server_dict: keeps the IM server urls
The *keys* for the dictionaries are the names of each IM. For example, "holiday" refers to the holiday IM. 


## Technical details on any dependencies needed to run MIX (ex: python commands to run,other services, docker, etc)
In order to run MIX, all IM’s and the middleware must be run using python’s `flask run`. 

## Handling Exceptions
If the IM is unable to return a json, then the IM will return an empty json. We decided to do this to avoid having a clutter of repeated error messages. 

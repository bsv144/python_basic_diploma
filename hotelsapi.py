import requests
from typing import List, Tuple

class hotels:
   def __init__(self, api_key : str) -> None:
      self.__api_key = api_key
      self.__headers = headers = {
         'x-rapidapi-host': "hotels4.p.rapidapi.com",
         'x-rapidapi-key': self.__api_key
      }

   def get_destinationid(self, destination : str) -> Tuple:
      '''
      Метод получает из API информацию по запрашиваемому месту
      '''
      url = "https://hotels4.p.rapidapi.com/locations/search"
      
      querystring = {"query":destination,"locale":"ru_RU"}
      response = requests.request("GET", url, headers=self.__headers, params=querystring)
      city_info = list(filter(lambda el: el['type'] == 'CITY' , response.json()['suggestions'][0]['entities']))
      return city_info[0]['destinationId'], city_info[0]['name']
   
   def get_hotels(self, destinationId : str, pageNumber : int) -> str:
      url = "https://hotels4.p.rapidapi.com/properties/list"
      querystring = {
         "destinationId" : destinationId,
         "pageNumber" : pageNumber,
         "pageSize":"2",
         "checkIn":"2021-10-03",
         "checkOut":"2020-10-15",
         "adults1":"1",
         "sortOrder":"PRICE",
         "locale":"ru_RU",
         "currency":"RUB"
      }
      response = requests.request("GET", url, headers=self.__headers, params=querystring)
      return response.json()
    

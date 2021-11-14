import requests
from typing import List, Tuple, Union
import json
from datetime import date, timedelta
import math


class Hotels:
    def __init__(self, api_key: str) -> None:
        self.__api_key = api_key
        self.__headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': self.__api_key
        }

    def get_destinationid(self, destination: str) -> Union[Tuple, None]:
        """
            Метод получает из API информацию по запрашиваемому месту
         """
        url = "https://hotels4.p.rapidapi.com/locations/v2/search"
        querystring = {"query": destination, "locale": "ru_RU"}
        response = requests.request("GET", url, headers=self.__headers, params=querystring)
        response.encoding = 'utf-8'
        city_info = list(filter(lambda el: el['type'] == 'CITY', response.json()['suggestions'][0]['entities']))
        return city_info[0]['destinationId'], city_info[0]['name']

    def get_hotels(self, destinationId: str, pageNumber: int = 1, pageSize: int = 25, sortOrder: str = 'PRICE',
                   priceMin: float = -1, priceMax: float = -1) -> Union[str, None]:
        """
        Метод фозвращает список отелей
        :param priceMax: Максимальна цена
        :param priceMin: Минимальная цена
        :param sortOrder: Порядок сортировки результата (возможные варианты BEST_SELLER|STAR_RATING_HIGHEST_FIRST|
        STAR_RATING_LOWEST_FIRST|DISTANCE_FROM_LANDMARK|GUEST_RATING|PRICE_HIGHEST_FIRST|PRICE)
        :param pageSize: Кол-во результатов выводимых в одном запросе (Max 25)
        :param destinationId: ID  населенного пункта возвращаемого функцией get_destinationid
        :param pageNumber: Номер запроса возвращающий данные в размере pageSize
        :return:
        """
        url = "https://hotels4.p.rapidapi.com/properties/list"
        pageSize = 25 if pageSize > 25 else pageSize
        querystring = {
            "destinationId": destinationId,
            "pageNumber": pageNumber,
            "pageSize": pageSize,
            "checkIn": date.today(),
            "checkOut": date.today() + timedelta(days=1),
            "adults1": "1",
            "sortOrder": sortOrder,
            "locale": "ru_RU",
            "currency": "RUB"
        }
        if 0 < priceMin < priceMax and priceMax > 0:
            querystring['priceMin'] = priceMin
            querystring['priceMax'] = priceMax
        response = requests.request("GET", url, headers=self.__headers, params=querystring)
        return response.json()

    def get_hotels_photos(self, _hotelId: int) -> Union[List, None]:
        """
        Метод выводит список словфотографий отелей
        :param _hotelId: ID отеля из метода get_hotels
        :return:
        """
        url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
        querystring = {"id": _hotelId}
        response = requests.request("GET", url, headers=self.__headers, params=querystring)
        photosJson = response.json()
        return photosJson["hotelImages"]

    def get_hotels_price_sort(self, _city: str, _outCount: int, _sort: str = 'PRICE') -> Union[List, None]:
        result = list()
        city = self.get_destinationid(_city)
        if city is None:
            return None
        for page_index in range(1, math.ceil(_outCount / 25) + 1):
            page_size = _outCount if (_outCount - 25) < 0 else 25
            out = self.get_hotels(destinationId=city[0], pageNumber=page_index, pageSize=page_size, sortOrder=_sort)
            result.extend(out['data']['body']['searchResults']['results'])
        return result

    def get_hotels_bestdeal(self, _city: str, _outCount: int, _priceMin: float, _priceMax: float,
                            _distanceMin: float, _distanceMax: float,
                            _sort: str = 'DISTANCE_FROM_LANDMARK') -> Union[List, None]:
        result = list()
        city = self.get_destinationid(_city)
        if city is None:
            return None
        page_index = 1
        page_size = 25

        # Запрашиваем по API страницы с данными, пока не выполнятся условия поиска либо пока не вернятся пустой список
        while True:
            out_json = self.get_hotels(destinationId=city[0], pageNumber=page_index, pageSize=page_size,
                                       sortOrder=_sort,
                                       priceMin=_priceMin, priceMax=_priceMax)
            # Если больше нет данных по отелям возвращаем список с ранее собранной информацией
            if len(out_json['data']['body']['searchResults']['results']) == 0:
                return result

            for hotel in out_json['data']['body']['searchResults']['results']:
                distance = float((hotel['landmarks'][0]['distance']).split()[0].replace(',', '.'))
                if _distanceMin <= distance <= _distanceMax:
                    result.append(hotel)
                if len(result) == _outCount:
                    return result

            page_index += 1


if __name__ == "__main__":
    with open('secret.json', 'r') as fconfig:
        secure_config = json.load(fconfig)

    API_KEY = secure_config['API_KEY']
    hotels = Hotels(API_KEY)

    city = hotels.get_destinationid('Москва')
    out_json = hotels.get_hotels(destinationId=city[0], pageNumber=2000, pageSize=25,
                                 sortOrder='DISTANCE_FROM_LANDMARK',
                                 priceMin=500, priceMax=1500)
    print(out_json)
    print(len(out_json['data']['body']['searchResults']['results']))

    """
    out = hotels.get_hotels_price_sort(_city='Москва', _outCount=10, _sort='PRICE_HIGHEST_FIRST')
    for hotel in out:
        # Расстояние до центра города
        landmark = list([hotel['landmarks'][index]['distance'] for index in range(len(hotel['landmarks']))
                         if hotel['landmarks'][index]['label'] == 'Центр города'])[0]
        price = f"{hotel['ratePlan']['price']['current']} {hotel['ratePlan']['price']['info']} " \
                f"{hotel['ratePlan']['price']['summary']}"
        address = hotel['address']['streetAddress']
        name = hotel['name']
        print(f"Название: {name}\nАдрес: {address}\nДо центра: {landmark}\nЦена: {price}")
        hotels.get_hotels_photos(_hotelId=hotel['id'])
    """

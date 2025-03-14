import os

from requests import get, RequestException
from .parsers import KinopoiskParser
import json

KINOPOISK_TOKEN = os.getenv("KINOPOISK_TOKEN")


class KinopoiskAPI:
    __kp_parser = KinopoiskParser()
    TOKEN = KINOPOISK_TOKEN
    MAX_FILM_ID = 10000000
    MIN_FILM_ID = 250

    def search_request(self, query, page=1, limit=10):
        try:
            headers = {'X-API-KEY': self.TOKEN}
            url = f'https://api.kinopoisk.dev/v1.4/movie/search?page={page}&limit={limit}&query={query}'
            response = get(url, headers=headers).json()
        except RequestException as e:
            raise RequestException(f'Ошибка {e} при обращении к API кинопоиска')

        return response

    def request_film_by_id(self, id):
        try:
            int(id)
            headers = {'X-API-KEY': self.TOKEN}
            url = f'https://api.kinopoisk.dev/v1.4/movie/{str(id)}'
            response = get(url, headers=headers).json()
        except RequestException as e:
            raise RequestException(f'Ошибка {e} при обращении к API кинопоиска')
        except ValueError:
            raise RequestException('id должно быть int значением')

        return response

    def get_search_results(self, query, page=1, limit=10):
        response = self.search_request(query, page, limit)
        return self.__kp_parser.parse_search_response(response)

    def get_film_by_id(self, id):
        if self.MIN_FILM_ID < id < self.MAX_FILM_ID:
            response = self.request_film_by_id(id)
            return self.__kp_parser.parse_by_id_response(response)
        raise ValueError(f'id должно находится в диапазоне между {self.MIN_FILM_ID} и {self.MAX_FILM_ID}')


if __name__ == '__main__':
    kp_api = KinopoiskAPI()
    # data = kp_api.get_search_results(
    #         query='Мстители Финал',
    #         page=1,
    #         limit=1
    #        )
    # print(json.dumps(data, indent=4, ensure_ascii=False))

    data = kp_api.get_film_by_id(999999)
    print(json.dumps(data, indent=4, ensure_ascii=False))

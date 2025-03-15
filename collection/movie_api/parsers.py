import unicodedata

from abc import ABC


class BaseParser(ABC):
    """Абстрактный класс парсера.

    Заключает договор о том, что у всех парсеров будет метод,
    parse_api_response.

    Содержит внутренние защищенные методы для использования в наследниках:
    * _clean_response - очистка запроса от непечатных символов
    """

    def _clean_response(self, response, untouchable_keys=None):
        if not untouchable_keys:
            untouchable_keys = []

        def __clean_response_recoursive(entry):
            if isinstance(entry, str):
                return unicodedata.normalize('NFKC', entry)
            if isinstance(entry, (bytes, int)):
                return entry

            if isinstance(entry, dict):
                new_dict = {}
                for key, value in entry.items():
                    if key not in untouchable_keys:
                        new_dict[key] = __clean_response_recoursive(value)
                    else:
                        new_dict[key] = value
                return new_dict

            if isinstance(entry, list):
                return [__clean_response_recoursive(value)
                        for value in entry]

        result = __clean_response_recoursive(response)
        return result

    @staticmethod
    def _camel_case_name(name):
        pivot = 0
        new_name = ''
        while pivot < len(name):
            if name[pivot] == '_':
                pivot += 1
                new_name += name[pivot].upper()
            else:
                new_name += name[pivot]
            pivot += 1

        return new_name

    def _camel_case_names(self, data_dict):
        new_dict = {}
        for key in data_dict:
            new_dict[self._camel_case_name(key)] = data_dict[key]
        return new_dict


class KinopoiskParser(BaseParser):
    """Класс для парсинга ответа от API Кинопоиска"""
    DEFAULT = {
        'default_fields': {
            'filmId': 'kinopoisk_id',
            'nameRu': 'title',
            'year': 'year',
            'description': 'description',
            'posterUrlPreview': 'img_url'
        },
        'untouchable_keys': ['posterUrlPreview']
    }

    SEARCH_SOURCE = 'films'

    @classmethod
    def set_configuration(cls, configuration):
        cls.DEFAULT = configuration

    def __parse_unusual_fields(self, data_dict, film):
        pass

    def parse_search_response(self, response, clean=True):

        fields = self.DEFAULT.get('default_fields')
        films = response.get(self.SEARCH_SOURCE) 
        print(films)
        if clean:
            films = self._clean_response(
                films,
                untouchable_keys=(self.DEFAULT.get('untouchable_keys'))
            )

        if not films:
            return []

        parsed = []
        for film in films:
            try:
                parsed_film = {}
                for api_key, parsed_key in fields.items():
                    parsed_film[parsed_key] = film[api_key]
                self.__parse_unusual_fields(parsed_film, film)

                parsed.append(parsed_film)

            except KeyError:
                raise KeyError(
                    'В ответе нет ключа указанного в конфигурации.'
                    'Передайте или проверьте переданную конфигурацию.')
            # except AttributeError:
            #     continue

        return parsed

    def parse_by_id_response(self, response, clean=True):
        fields = self.DEFAULT.get('default_fields')
        film = response

        if not film:
            return {}

        if clean:
            film = self._clean_response(
                film,
                untouchable_keys=(self.DEFAULT.get('untouchable_keys'))
            )

        try:
            parsed_film = {}
            for api_key, parsed_key in fields.items():
                parsed_film[parsed_key] = film[api_key]
                self.__parse_unusual_fields(parsed_film, film)

        except KeyError:
            raise KeyError(
                'В ответе нет ключа указанного в конфигурации.'
                'Передайте или проверьте переданную конфигурацию.')

        return parsed_film


def snakecase(s):
    """Преобразует строку из camelCase в snake_case."""
    return ''.join(['_' + c.lower() if c.isupper() else c for c in s]).lstrip('_')


def parse_keys_to_snake_case(data_dict):
    return {snakecase(key): value for key, value in data_dict.items()}
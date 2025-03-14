from functools import wraps

from requests import RequestException

from django.http import JsonResponse

from .constants import errors


class CollectionError(Exception):
    pass


class FilmException(Exception):
    pass


class CollectionNotFoundError(CollectionError):
    def __init__(self, *args, **kwargs):
        id = kwargs.get('collection_id', 'неизвестный id')
        message = f'{errors.COLLECTION_NOT_EXISTS}. id: {id}'
        super().__init__(message)


class CollectionPermissionDeniedError(CollectionError):
    def __init__(self, *args):
        message = errors.COLLECTION_PERMIT_DENIIED
        super().__init__(message)


class CollectionAlreadyExistsError(CollectionError):
    def __init__(self, *args):
        message = errors.SAME_NAME_COLLECTION
        super().__init__(message)


class EmptyCollectionNameError(CollectionError):
    def __init__(self, *args):
        message = errors.EMPTY_COLLECTIONS_NAME
        super().__init__(message)


class FilmNotFoundError(FilmException):
    def __init__(self, *args, **kwargs):
        id = kwargs.get('film_id', 'неизвестный id')
        message = f'{errors.FILM_NOT_FOUND}. id: {id}'
        super().__init__(message)


class FilmAlreadyExistsError(FilmException):
    def __init__(self, *args):
        message = errors.FILM_ALREADY_EXISTS
        super().__init__(message)


class SystemCollectionEditError(CollectionError):
    def __init__(self):
        message = errors.CANT_EDIT_COLLECTION
        super().__init__(message)


class DataBaseError(Exception):
    def __init__(self, *args):
        message = errors.DATABASE_ERROR
        super().__init__(message)


class InvalidDataError(ValueError):
    def __init__(self, *args, **kwargs):
        data = kwargs.get('data')
        message = errors.INVALID_DATA_ERROR + str(type(data) if data else '')
        super().__init__(message)


def API_EXCEPTION_RESPONSE(exception):
    return {
        'success': False,
        'message': f'Ошибка ответа API: {exception}'
    }


def FILM_EXCEPTION_RESPONSE(exception):
    return {
        'success': False,
        'message': f'Ошибка работы с фильмом: {exception}'
    }


def COLLECTION_EXCEPTION_RESPONSE(exception):
    return {
        'success': False,
        'message': f'Ошибка работы с коллекцией: {exception}'
    }


def DATABASE_EXCEPTION_RESPONSE(exception):
    return {
        'success': False,
        'message': f'Ошибка работы с базой данных: {exception}'
    }


def INVALID_DATA_EXCEPTION_RESPONSE(exception):
    return {
        'success': False,
        'message': f'Неверный формат данных: {exception}'
    }


def handle_error(exception):
    """
    Обрабатывает исключения и возвращает JsonResponse с соответствующим сообщением и кодом.
    """
    if isinstance(exception, FilmException):
        response = FILM_EXCEPTION_RESPONSE(exception)
    elif isinstance(exception, CollectionError):
        response = COLLECTION_EXCEPTION_RESPONSE(exception)
    elif isinstance(exception, InvalidDataError):
        response = INVALID_DATA_EXCEPTION_RESPONSE(exception)
    elif isinstance(exception, DataBaseError):
        response = DATABASE_EXCEPTION_RESPONSE(exception)
    elif isinstance(exception, RequestException):
        response = API_EXCEPTION_RESPONSE(exception)
    else:
        response = {'error': 'Unknown error occurred', 'details': str(exception)}

    return JsonResponse(response)


def handle_error_decorator(view_func):
    """
    Декоратор для обработки ошибок в представлениях.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except (FilmException, CollectionError,
                InvalidDataError, DataBaseError,
                RequestException) as e:
            return handle_error(e)
        except Exception as e:
            # Логируем или обрабатываем неучтенные исключения (если нужно)
            return JsonResponse({'error': 'Unknown error occurred', 'details': str(e)})

    return wrapper


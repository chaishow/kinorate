import logging

from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.db.models import Q

from .models import Film, Collection, Rate

from .constants import defaults

from .exceptions import (
    DataBaseError,
    SystemCollectionEditError,
    EmptyCollectionNameError,
    FilmNotFoundError,
    CollectionAlreadyExistsError,
    InvalidDataError,
    CollectionNotFoundError,
    CollectionPermissionDeniedError,
    FilmAlreadyExistsError
)

logger = logging.getLogger('collection')


def get_collection_by_id(profile, collection_id):
    try:
        collection = Collection.objects.filter(id=collection_id).first()

        if not collection:
            logger.info(f'Запрошена несуществующая коллекция'
                        f'id: {collection_id}')
            raise CollectionNotFoundError

        if collection.profile != profile:
            raise CollectionPermissionDeniedError

    except ValueError as e:
        logger.debug(f'Неверный тип collection_id'
                     f'{collection_id}, {type(collection_id)}'
                     f'Текст ошибки {e}')
        raise InvalidDataError(data=collection_id)

    return collection


def get_collection_by_name(profile, collection_name):
    try:
        collection = Collection.objects.filter(
            name=collection_name,
            profile=profile
            ).first()
    except Collection.DoesNotExist:
        logger.info(f'Запрошена несуществующая коллекция name,'
                    f'profile: {collection_name, profile}')
        raise CollectionNotFoundError
    except ValueError as e:
        logger.debug(f'Неверный тип collection_id'
                     f'{collection_name}, {type(collection_name)}'
                     f'Текст ошибки {e}')
        raise InvalidDataError(data=collection_name)

    return collection


def is_system_collection(collection):
    return collection.is_system


def get_profile_system_collections(profile, field=''):
    collections = Collection.objects.filter(
        Q(name=defaults.DEFAULT_RATED_COLLECTION_NAME, profile=profile)
        | Q(name=defaults.DEFAULT_COLLECTION_NAME, profile=profile)
    )
    if field:
        return collections.values_list(field, flat=True)
    return collections


def create_collection(profile, name, film_ids=None):
    film_ids = set(film_ids) if film_ids else set()
    if not name:
        raise EmptyCollectionNameError
    if not all([isinstance(film_id, int) for film_id in film_ids]):
        raise InvalidDataError
    if Collection.objects.filter(profile=profile, name=name).exists():
        raise CollectionAlreadyExistsError

    try:
        with transaction.atomic():
            collection = Collection.objects.create(profile=profile, name=name)
            films = Film.objects.filter(id__in=film_ids)
            collection.films.add(*films)
    except IntegrityError as e:
        logger.error(f'Ошибка в базе данных {e}')
        raise DataBaseError

    return collection


def delete_collection(profile, collection_id):
    collection = Collection.objects.filter(id=collection_id, profile=profile).first()
    if not collection:
        raise CollectionNotFoundError

    if is_system_collection(collection):
        raise CollectionPermissionDeniedError
    try:
        collection.delete()
    except IntegrityError as e:
        logger.error(f'Ошибка в базе данных {e}')
        raise DataBaseError


def update_collection(collection_id, profile, **kwargs):
    collection = Collection.objects.filter(id=collection_id, profile=profile).first()
    if not collection:
        raise CollectionNotFoundError

    if is_system_collection(collection):
        raise CollectionPermissionDeniedError

    try:
        for key, value in kwargs.items():
            setattr(collection, key, value)
        collection.save()
    except AttributeError as e:
        logger.error(f'{e}, key: {key}, value: {value}')
    except ValidationError as e:
        logger.error(f'{e}, key: {key}, value: {value}')
        raise InvalidDataError


def edit_collection_contains(profile, film_id, collection_id=None,
                             collection_name=None, action='add',
                             system_collection_accessed=False):

    if collection_id is None and collection_name is None:
        raise ValueError('Передайте имя или id коллекции')

    if not isinstance(film_id, int):
        raise InvalidDataError

    if collection_id:
        collection = get_collection_by_id(
            profile=profile,
            collection_id=collection_id
        )

    elif collection_name:
        collection = get_collection_by_name(
            profile=profile,
            collection_name=collection_name
        )

    if not system_collection_accessed and is_system_collection(collection):
        raise SystemCollectionEditError

    try:
        if action == 'add':
            film = Film.objects.get(id=film_id)
            if collection.films.filter(id=film_id).exists():
                raise FilmAlreadyExistsError
            collection.films.add(film)
        elif action == 'delete':
            film = collection.films.get(id=film_id)
            collection.films.remove(film)
        else:
            raise ValueError(f'Некорректное действие {action}.'
                             f'Допустимые значения: add, delete')
    except Film.DoesNotExist:
        raise FilmNotFoundError(film_id=film_id)


def add_to_collection(profile, film_id,
                      collection_id=None,
                      collection_name=None,
                      system_collection_accessed=False):

    edit_collection_contains(
        profile=profile,
        film_id=film_id,
        collection_id=collection_id,
        collection_name=collection_name,
        action='add',
        system_collection_accessed=system_collection_accessed
    )


def delete_from_collection(profile, film_id,
                           collection_id=None,
                           collection_name=None,
                           system_collection_accessed=False):

    edit_collection_contains(
        profile=profile,
        film_id=film_id,
        collection_id=collection_id,
        collection_name=collection_name,
        action='delete',
        system_collection_accessed=system_collection_accessed
    )


def get_collection_films(profile, collection_name=None, collection_id=None):
    if collection_id is None and collection_name is None:
        raise ValueError('Передайте имя или id коллекции')

    if collection_id:
        collection = Collection.objects.filter(id=collection_id, profile=profile).first()
    elif collection_name:
        collection = Collection.objects.filter(name=collection_name, profile=profile).first()

    if not collection:
        raise CollectionNotFoundError

    return collection.films.all()


def get_or_create_film_from_data(data):
    if 'title' not in data or 'year' not in data:
        raise InvalidDataError

    try:
        film, created = Film.get_or_create_from_data(data)
    except TypeError as e:
        logger.error(f"Неподдерживаемый тип данных: {e}")
        raise InvalidDataError
    except ValueError as e:
        logger.error(f'Некорректныe данныe: {e}')
        raise InvalidDataError
    except IntegrityError as e:
        logger.error(f'Ошибка базы данных: {e}')
        raise DataBaseError

    return film, created


def dump_and_return_search_results(data):
    result = []
    for entry in data:
        film, created = get_or_create_film_from_data(entry)
        result.append(film)

    return result


def get_available_films(profile):
    profile_system_collections_ids = get_profile_system_collections(profile, field='id')

    available_films = Film.objects.filter(collections__in=profile_system_collections_ids)

    return available_films


def get_films_rating(profile, collection):
    films_rating = []
    for film in collection.films.all():
        rate = Rate.objects.filter(film=film, profile=profile).first()
        entry = {
                'film': film,
                'rate': rate
        }
        films_rating.append(entry)

    return films_rating


def move_from_unrated_to_rated(profile, film_id):
    unrated = get_collection_by_name(
        profile=profile,
        name=defaults.DEFAULT_COLLECTION_NAME
    )

    rated = get_collection_by_name(
        profile=profile,
        name=defaults.DEFAULT_RATED_COLLECTION_NAME
    )

    film = unrated.films.filter(id=film_id).first()
    if not film:
        return

    with transaction.atomic():
        unrated.films.remove(film)
        rated.films.add(film)


def add_or_update_rate(profile, film_id, rate):
    if not (1 <= rate <= 10) or not isinstance(rate, int):
        raise InvalidDataError

    film = get_available_films(profile).filter(id=film_id).first()
    if not film:
        raise FilmNotFoundError

    with transaction.atomic():
        rate, created = Rate.objects.update_or_create(
            profile=profile,
            film=film,
            defaults={'rate': rate}
        )

        if created:
            move_from_unrated_to_rated(profile, film_id)

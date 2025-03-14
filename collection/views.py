import json

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required

from .movie_api import KinopoiskAPI

from . import service

from .exceptions import handle_error_decorator

from .constants import defaults

kp_api = KinopoiskAPI()


@login_required
@handle_error_decorator
def search_view(request):
    query = request.GET.get('query')
    page = request.GET.get('page')
    context = {
        'films': [],
        'was_search': False
    }

    if query:
        context['was_search'] = True
        page = page or 1
        api_response = kp_api.get_search_results(
            query=query,
            page=page,
            limit=30
        )

        context['films'] = service.dump_and_return_search_results(
            data=api_response
        )

    return render(request, 'collection/search.html', context)


@login_required
@handle_error_decorator
def add_from_search(request):
    film_id = json.loads(request.body).get('id')
    profile = request.user.profile

    service.add_to_collection(
        profile=profile,
        film_id=film_id,
        collection_name=defaults.DEFAULT_COLLECTION_NAME,
        system_collection_accessed=True
    )

    return JsonResponse({'success': True})


@login_required
@handle_error_decorator
def collection_view(request, collection_id):
    profile = request.user.profile

    if request.method == 'PATCH':
        name = json.loads(request.body).get('name')

        service.update_collection(
            profile=profile,
            collection_id=collection_id,
            name=name
        )

        return JsonResponse({'success': True})

    if request.method == 'DELETE':
        service.delete_collection(
            profile=profile,
            collection_id=collection_id
        )

        return JsonResponse({'success': True})

    collection = get_object_or_404(profile.collections, id=collection_id)
    films_rating = service.get_films_rating(
        profile=profile,
        collection=collection
    )

    available_films = service.get_available_films(
        profile=profile
    ).exclude(collections=collection)

    context = {
        'films_rating': films_rating,
        'available_films': available_films,
        'collection': collection
    }

    return render(request, 'collection/collection.html', context)


@login_required
@handle_error_decorator
def collections_view(request):
    profile = request.user.profile

    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        film_ids = data.get('film_ids')

        service.create_collection(
            profile=profile,
            name=name,
            film_ids=film_ids
        )

        return JsonResponse({'success': True})

    context = {
        'collections': profile.collections.all(),
        'available_films': service.get_available_films(profile)
    }

    return render(request, 'collection/collections.html', context)


@login_required
@handle_error_decorator
def edit_movie_list(request, collection_id, film_id):
    profile = request.user.profile
    if request.method == 'DELETE':
        service.delete_from_collection(
            profile=profile,
            film_id=film_id,
            collection_id=collection_id
        )

    if request.method == 'POST':
        service.add_to_collection(
            profile=profile,
            film_id=film_id,
            collection_id=collection_id
        )

    return JsonResponse({'success': True})


@login_required
@handle_error_decorator
def add_rate(request, film_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        rate = data.get('rating')
        profile = request.user.profile

        service.add_or_update_rate(
            profile=profile,
            film_id=film_id,
            rate=rate
        )

        return JsonResponse({'success': True})

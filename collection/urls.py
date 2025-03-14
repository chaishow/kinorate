from django.urls import path
from . import views

app_name = 'collection'

urlpatterns = [
    path('collections/', views.collections_view, name='collections_view'),
    path('collection/<int:collection_id>/', views.collection_view, name='collection_view'),
    path('collection/<int:collection_id>/<int:film_id>/', views.edit_movie_list, name='edit_movie_list'),
    path('film/<int:film_id>/rate/', views.add_rate, name='add_rate'),
    path('search/', views.search_view, name='search_view'),
    path('search/add_movie/', views.add_from_search, name='add_from_search')
]
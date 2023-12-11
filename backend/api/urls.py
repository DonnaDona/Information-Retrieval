from .views import MovieSearchViewSet, MovieViewSet
from django.urls import path

urlpatterns = [
    path('search/', MovieSearchViewSet.as_view({'get': 'list'})),
    path('recommend/', MovieViewSet.as_view({'get': 'list'})),
]
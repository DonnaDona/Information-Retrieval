from .views import MovieViewSet, test
from django.urls import path

urlpatterns = [
    path('search/', MovieViewSet.as_view({'get': 'list'})),
    path('test/', test)
]
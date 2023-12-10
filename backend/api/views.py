from rest_framework.views import APIView

from core.models import Movie, DataSource
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from django.http import HttpResponse
from django.conf import settings

from .serializers import MovieSerializer, DataSourceSerializer

from .services import perform_search


# create a viewset for the Movie model
# movies can be retrieved only as a list through a request that as a "q" query parameter, which will be used to filter
# the movies by title

class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

    def get_queryset(self):
        request = self.request
        # retrieve the 'q' query parameter
        q = request.query_params.get('q', None)

        # if the parameter is not provided, return an error
        if q is None:
            return Response({"error": "missing query parameter 'q'"})
        
        page_size = settings.REST_FRAMEWORK['PAGE_SIZE']
        page = request.query_params.get('page', 1)
        end = page * page_size

        docnos = perform_search(q, end)
        queryset = Movie.retrieve_sorted(docnos)
        return queryset


def test(request):
    return HttpResponse("Hello, world. You're at the api test page.")

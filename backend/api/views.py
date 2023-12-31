import pandas as pd
from rest_framework.views import APIView

from core.models import Movie, DataSource
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from django.http import HttpResponse
from django.conf import settings

from .serializers import MovieSerializer, DataSourceSerializer

from .services import perform_search, retrieve_recommended


# create a viewset for the Movie model
# movies can be retrieved only as a list through a request that as a "q" query parameter, which will be used to filter
# the movies by title

class MovieSearchViewSet(viewsets.ReadOnlyModelViewSet):
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
        page = int(request.query_params.get('page', 1))
        next_end = (page + 1) * page_size  # always show a next page

        docnos = perform_search(q, next_end)
        queryset = Movie.retrieve_sorted(docnos)
        return queryset


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    pagination_class = None

    def get_queryset(self):
        request = self.request
        q = request.query_params.get('q', None)
        if q is None:
            return Response({"error": "missing query parameter 'q'"})

        docnos = retrieve_recommended(q)

        qs = Movie.retrieve_sorted(docnos)

        return qs

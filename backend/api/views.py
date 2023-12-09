from rest_framework.views import APIView

from core.models import Movie, DataSource
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from django.http import HttpResponse

from api.serializers import MovieSerializer, DataSourceSerializer

from retrieval.services import perform_search


# create a viewset for the Movie model
# movies can be retrieved only as a list through a request that as a "q" query parameter, which will be used to filter
# the movies by title

class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

    def list(self, request, **kwargs):
        # retrieve the 'q' query parameter
        q = request.query_params.get('q', None)
        # if the parameter is not provided, return an error
        if q is None:
            return Response({"error": "missing query parameter 'q'"})
        
        docnos = perform_search(q)

        queryset = self.get_queryset().filter(id__in=docnos)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


def test(request):
    return HttpResponse("Hello, world. You're at the api test page.")
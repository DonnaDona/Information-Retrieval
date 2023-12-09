import math

from rest_framework import serializers

from core.models import Movie, DataSource


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = ['url', 'page_title', 'score', 'critic_score']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        for key, value in ret.items():
            # if value is a float and it is NaN, put None
            if isinstance(value, float) and math.isnan(value):
                ret[key] = None
        return ret


class MovieSerializer(serializers.ModelSerializer):
    data_sources = DataSourceSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'release', 'duration', 'genres', 'directors', 'actors', 'plot',
                  'image_url', 'data_sources']
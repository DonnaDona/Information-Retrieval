import math

from core.models import Movie, DataSource
from rest_framework import serializers


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = ['name', 'url', 'page_title', 'score', 'critic_score']

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
        fields = ['id', 'title', 'description', 'release', 'duration', 'genres', 'image_url', 'data_sources']

    def to_representation(self, instance):
        if instance.duration == -1:
            instance.duration = None

        ret = super().to_representation(instance)

        # transform the data_sources from a list to a dictionary
        data_sources = ret.pop('data_sources')
        ret['data_sources'] = {}
        for data_source in data_sources:
            ret['data_sources'][data_source.pop('name').lower()] = data_source
        return ret

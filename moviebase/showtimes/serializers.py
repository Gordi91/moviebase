import datetime

from rest_framework import serializers

from movielist.models import Movie
from showtimes.models import Cinema, Screening

# TODO
# def hyperlinkedRelatedFieldPlusDays(model, view_name, days):
#     return serializers.HyperlinkedRelatedField(
#         many=True,
#         view_name=view_name,
#         queryset=Movie.objects.filter(screening__date__lte=(datetime.datetime.now()+datetime.timedelta(days=days)))
#     )


class CinemaSerializer(serializers.ModelSerializer):
    movies = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='movie-detail',
        # queryset=Movie.objects.filter(screening__date__lte=(datetime.datetime.now() + datetime.timedelta(days=30)))
    )

    # hyperlinkedRelatedFieldPlusDays(Movie, 'movie-detail', 30)

    class Meta:
        model = Cinema
        fields = ("id", "name", "city", "movies")


class ScreeningSerializer(serializers.ModelSerializer):
    movie = serializers.SlugRelatedField(
        many=False,
        slug_field='title',
        queryset=Movie.objects.all()
    )
    cinema = serializers.SlugRelatedField(
        many=False,
        slug_field='name',
        queryset=Cinema.objects.all()
    )

    class Meta:
        model = Screening
        fields = ("id", "movie", "cinema", "date")

import django_filters
from .models import Location
from django.db.models import Avg

class LocationFilter(django_filters.FilterSet):
    min_rating = django_filters.NumberFilter(method='filter_min_rating')

    class Meta:
        model = Location
        fields = ['category']

    def filter_min_rating(self, queryset, value):
        return queryset.annotate(
            avg_rating=Avg('reviews__rating')
        ).filter(avg_rating__gte=value)

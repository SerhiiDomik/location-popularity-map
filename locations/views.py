import pandas as pd
from io import BytesIO

from django.core.cache import cache
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Prefetch
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Location,
    Review,
    ReviewReaction,
    LocationSubscription
)
from .serializers import (
    ReviewSerializer,
    ReviewReactionSerializer,
    LocationListSerializer,
    LocationDetailSerializer,
    LocationSubscriptionSerializer,
)
from .filters import LocationFilter

CACHE_TIMEOUT_SHORT = 300
CACHE_TIMEOUT_LONG = 3600


class LocationViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = LocationFilter
    search_fields = ['name', 'description']
    queryset = (Location.objects
        .annotate(average_rating=Avg('reviews__rating'))
        .prefetch_related(Prefetch('reviews', queryset=Review.objects.prefetch_related('reactions')))
    )

    def get_serializer_class(self):
        return LocationListSerializer if self.action == 'list' else LocationDetailSerializer

    def _get_cache(self, key):
        return cache.get(key)

    def _set_cache(self, key, value, timeout=CACHE_TIMEOUT_SHORT):
        cache.set(key, value, timeout)

    def list(self, request, *args, **kwargs):
        key = f"locations:list:{request.get_full_path()}"
        cached = self._get_cache(key)
        if cached:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        self._set_cache(key, response.data)
        return response

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs['pk']
        key = f"locations:detail:{pk}"
        cached = self._get_cache(key)
        if cached:
            return Response(cached)
        response = super().retrieve(request, *args, **kwargs)
        self._set_cache(key, response.data)
        return response

    @action(detail=False, methods=['get'], url_path='export')
    def export_locations(self, request):
        key = 'locations:export_csv'
        cached = self._get_cache(key)
        if cached:
            return cached

        data = LocationListSerializer(self.queryset, many=True).data
        df = pd.DataFrame(data)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="locations.csv"'
        response.write('\ufeff')
        df.to_csv(response, index=False, sep=';')

        self._set_cache(key, response, CACHE_TIMEOUT_LONG)
        return response


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(location_id=self.kwargs['location_pk']).prefetch_related('reactions')

    def list(self, request, *args, **kwargs):
        key = f"reviews:list:{self.kwargs['location_pk']}"
        cached = cache.get(key)
        if cached:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set(key, response.data, CACHE_TIMEOUT_SHORT)
        return response

    def perform_create(self, serializer):
        review = serializer.save(user=self.request.user, location_id=self.kwargs['location_pk'])

        subscriptions = review.location.subscriptions.exclude(user=self.request.user)
        emails = [sub.user.email for sub in subscriptions if sub.user.email]

        if emails:
            send_mail(
                subject=f"New review for {review.location.name}",
                message=f"User {review.user.username} left a new review:\n\n{review.comment}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=emails,
                fail_silently=True,
            )



class ReviewReactionViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewReactionSerializer

    def get_queryset(self):
        return ReviewReaction.objects.filter(review_id=self.kwargs['review_pk'])

    def list(self, request, *args, **kwargs):
        key = f"reactions:list:{self.kwargs['review_pk']}"
        cached = cache.get(key)
        if cached:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set(key, response.data, CACHE_TIMEOUT_SHORT)
        return response

    def perform_create(self, serializer):
        ReviewReaction.objects.update_or_create(
            user=self.request.user,
            review_id=self.kwargs['review_pk'],
            defaults={'reaction': serializer.validated_data['reaction']}
        )
        cache.delete(f"reactions:list:{self.kwargs['review_pk']}")


class LocationSubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = LocationSubscriptionSerializer

    def get_queryset(self):
        location_pk = self.kwargs['location_pk']
        return LocationSubscription.objects.filter(
            user=self.request.user,
            location_id=location_pk
        )

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            location_id=self.kwargs['location_pk']
        )

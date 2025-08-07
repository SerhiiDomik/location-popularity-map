from rest_framework import viewsets, permissions, filters
from django.db.models import Avg, Prefetch, Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import Location, Review, ReviewReaction, ReactionType
from .serializers import (
    ReviewSerializer,
    ReviewReactionSerializer,
    LocationListSerializer,
    LocationDetailSerializer
)

from .filters import LocationFilter


class LocationViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = LocationFilter
    search_fields = ['name', 'description']

    queryset = Location.objects.annotate(
        average_rating=Avg('reviews__rating')
    ).prefetch_related(
        Prefetch('reviews', queryset=Review.objects.prefetch_related('reactions'))
    )

    def get_serializer_class(self):
        if self.action == 'list':
            return LocationListSerializer

        return LocationDetailSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(
            location_id=self.kwargs['location_pk']
        ).prefetch_related('reactions')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, location_id=self.kwargs['location_pk'])


class ReviewReactionViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewReactionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return ReviewReaction.objects.filter(review_id=self.kwargs['review_pk'])

    def perform_create(self, serializer):
        ReviewReaction.objects.update_or_create(
            user=self.request.user,
            review_id=self.kwargs['review_pk'],
            defaults={'reaction': serializer.validated_data['reaction']}
        )

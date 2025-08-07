from rest_framework import viewsets, permissions, filters
from django.db.models import Avg, Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from .models import Location, Review, ReviewReaction
from .serializers import LocationSerializer, ReviewSerializer, ReviewReactionSerializer
from .filters import LocationFilter


class LocationViewSet(viewsets.ModelViewSet):
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = LocationFilter
    search_fields = ['name', 'description']

    queryset = Location.objects.all()

    def get_queryset(self):
        return Location.objects.annotate(
            average_rating=Avg('reviews__rating')
        ).prefetch_related('reviews__reactions')


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(
            location_id=self.kwargs['location_pk']
        ).annotate(
            like_count=Count('reactions', filter=Q(reactions__reaction=ReactionType.LIKE)),
            dislike_count=Count('reactions', filter=Q(reactions__reaction=ReactionType.DISLIKE))
        ).prefetch_related('reactions')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, location_id=self.kwargs['location_pk'])


class ReviewReactionViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewReactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReviewReaction.objects.filter(review_id=self.kwargs['review_pk'])

    def perform_create(self, serializer):
        ReviewReaction.objects.update_or_create(
            user=self.request.user,
            review_id=self.kwargs['review_pk'],
            defaults={'reaction': serializer.validated_data['reaction']}
        )

from django.urls import path, include
from rest_framework_nested import routers
from .views import LocationViewSet, ReviewViewSet, ReviewReactionViewSet

router = routers.SimpleRouter()
router.register('locations', LocationViewSet)

locations_router = routers.NestedSimpleRouter(router, 'locations', lookup='location')
locations_router.register('reviews', ReviewViewSet, basename='location-reviews')

reviews_router = routers.NestedSimpleRouter(locations_router, 'reviews', lookup='review')
reviews_router.register('reactions', ReviewReactionViewSet, basename='review-reactions')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(locations_router.urls)),
    path('', include(reviews_router.urls)),
]

app_name = 'locations'

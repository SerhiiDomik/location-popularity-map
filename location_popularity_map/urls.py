from django.contrib import admin
from django.urls import path, include

import location_popularity_map

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("locations.urls", namespace="locations")),
    path("users/", include("users.urls")),

]

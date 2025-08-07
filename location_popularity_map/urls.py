from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView  # ← оце обовʼязково


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("locations.urls", namespace="locations")),
    path("users/", include("users.urls"), name="users"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

]

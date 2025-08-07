from django.contrib import admin
from .models import Location, Review, LocationReaction

admin.site.register(Location)
admin.site.register(Review)
admin.site.register(LocationReaction)

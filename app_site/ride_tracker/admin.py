from django.contrib import admin

from .models import UserRides, Ride, Point

admin.site.register(UserRides)
admin.site.register(Ride)
admin.site.register(Point)

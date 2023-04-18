import datetime
import json

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.views import View
from django.views.generic import TemplateView
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.db.models import F

from .models import UserRides, Ride, Point

""" Class Views """

class LoginView(TemplateView):
    """ Login view """
    template_name =  "ride_tracker/auth/login.html"  # GET request

    def post(self, request):
        """ Authenticate user """
        # Check if user exists
        if not User.objects.filter(username=request.POST["username"]).exists():
            messages.error(request, "User doesn't exist.", extra_tags='danger')
            return redirect(reverse("ride_tracker:login"))
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])

        # Check if user credentials are correct
        if not user:
            messages.error(request, "Wrong credentials, try again.", extra_tags='danger')
            return redirect(reverse("ride_tracker:login"))

        # Login user
        login(request, user)
        messages.success(request, "Logged in successfully", extra_tags='success')
        return redirect(reverse("ride_tracker:index"))


class RegisterView(TemplateView):
    """ Register view """
    template_name = "ride_tracker/auth/register.html"  # GET request

    def post(self, request):
        """
        Create a new user and login
        """
        username = request.POST["username"]

        # Check if user exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "User already exists", extra_tags='danger')
            return redirect(reverse("ride_tracker:register"))

        # On success, register user and login
        user = User.objects.create_user(username=username)
        user.set_password(request.POST["password"])
        user.save()
        login(request, user)

        # Create ride counter
        ride_counter = UserRides(user=user)
        ride_counter.save()

        messages.success(request, "Registered successfully", extra_tags='success')
        return redirect(reverse("ride_tracker:index"))


class IndexView(LoginRequiredMixin, TemplateView):
    """ Index page view"""
    template_name = "ride_tracker/pages/index.html"


class RideView(LoginRequiredMixin, TemplateView):
    """ Ride page view"""
    template_name = "ride_tracker/pages/ride.html"


class FinishRideView(LoginRequiredMixin, View):
    """
    Store ride and ride points in database
    """
    def post(self, request):
        ride_data = json.loads(request.body)  # Getting ride data from request body

        request.user.userrides.ride_count += 1
        request.user.userrides.save()

        # Adding ride info
        ride = Ride(user=request.user)
        ride.start_time = datetime.datetime.fromtimestamp(int(ride_data["pts"][0]["timestamp"]))
        ride.end_time = datetime.datetime.fromtimestamp(int(ride_data["pts"][-1]["timestamp"]))
        speeds = [float(pt["speed"]) for pt in ride_data["pts"]]
        ride.avg_speed = round(sum(speeds) / len(speeds), 1)
        ride.max_speed = max(speeds)
        ride.total_time = ride_data["totalSec"]
        ride.moving_time = ride_data["movingSec"]
        ride.distance = ride_data["distance"]
        ride.notes = ride_data["notes"]
        if not ride_data["title"] or len(ride_data["title"]) == 0:  # If the user didn't provide a ride title
            hour = ride.start_time.hour
            if hour in [23, 0, 2]:
                ride.title = "Midnight ride"
            elif hour in range(3, 7):
                ride.title = "Dawn ride"
            elif hour in range (7, 11):
                ride.title = "Morning ride"
            elif hour in range(11, 14):
                ride.title = "Noon ride"
            elif hour in range(11, 19):
                ride.title = "Afternoon ride"
            elif hour in range(19, 23):
                ride.title = "Evening ride"
        else:
            ride.title = ride_data["title"]
        ride.save()

        # Add route points
        for pt in ride_data["pts"]:
            point = Point(
                    ride=ride,
                    latitude=float(pt["latitude"]),
                    longitude=float(pt["longitude"]),
                    timestamp=datetime.datetime.fromtimestamp(int(pt["timestamp"])),
                    speed=float(pt["speed"])
                    )
            point.save()

        return HttpResponse(json.dumps({"success": True}))


class HistoryView(LoginRequiredMixin, TemplateView):
    """ History page view"""
    template_name = "ride_tracker/pages/history.html"

    def get_context_data(self, **kwargs):
        """
        https://docs.djangoproject.com/en/4.1/ref/class-based-views/mixins-simple/#django.views.generic.base.ContextMixin.get_context_data
        """
        context = super().get_context_data(**kwargs)

        # Getting user rides
        user_rides = Ride.objects.filter(user=self.request.user).all()

        context["rides"] = user_rides
        return context


class ViewRideView(LoginRequiredMixin, TemplateView):
    """ View ride page view """
    template_name = "ride_tracker/pages/view_ride.html"

    def get_context_data(self, **kwargs):
        """
        https://docs.djangoproject.com/en/4.1/ref/class-based-views/mixins-simple/#django.views.generic.base.ContextMixin.get_context_data
        """
        context = super().get_context_data(**kwargs)

        # Getting ride data and points
        # ride = Ride.objects.get(pk=self.kwargs["ride_id"])
        ride = Ride.objects.get(pk=self.kwargs["ride_id"])
        points = Point.objects.filter(ride=ride).order_by(F("timestamp").asc()).all().values('latitude', 'longitude')
        pts = list(points)

        context["ride"] = ride
        # print(ride.point_set.all())
        # context["points"] = serializers.serialize('json', points)
        # context["points"] = json.dumps(pts)
        context["points"] = json.dumps(pts, cls=DjangoJSONEncoder)

        return context


""" Function views """

@login_required
def logout_user(request):  # naming the function logout will conflict with the logout import
    logout(request)
    messages.info(request, "Logged out", extra_tags="info")
    return redirect(reverse("ride_tracker:login"))


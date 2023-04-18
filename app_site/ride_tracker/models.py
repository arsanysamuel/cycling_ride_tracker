from django.db import models
from django.contrib.auth.models import User

class UserRides(models.Model):
    """
    Number of user rides
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ride_count = models.IntegerField(default=0)

    def __str__(self):
        return f"<{self.user.username} has been on {self.ride_count} rides.>"


class Ride(models.Model):
    """
    Ride object model
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_time = models.IntegerField()
    moving_time = models.IntegerField()
    distance = models.FloatField()
    avg_speed = models.FloatField()
    max_speed = models.FloatField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"<Ride: {self.title}>"


class Point(models.Model):
    """
    Point on ride route
    """
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField()
    speed = models.FloatField(blank=True)

    def __str__(self):
        return f"<Point: lat:{self.latitude}, lon:{self.longitude} at:{self.timestamp}. of Ride: {self.ride.title}"


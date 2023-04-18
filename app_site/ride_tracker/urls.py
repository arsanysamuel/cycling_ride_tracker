from django.urls import path
from . import views

app_name = "ride_tracker"

urlpatterns = [
        path("login/", views.LoginView.as_view(), name="login"),
        path("register/", views.RegisterView.as_view(), name="register"),
        path("", views.IndexView.as_view(), name="index"),
        path("ride/", views.RideView.as_view(), name="ride"),
        path("finish-ride/", views.FinishRideView.as_view(), name="finish-ride"),
        path("history/", views.HistoryView.as_view(), name="history"),
        path("view-ride/<int:ride_id>/", views.ViewRideView.as_view(), name="view-ride"),
        path("logout/", views.logout_user, name="logout"),
        ]

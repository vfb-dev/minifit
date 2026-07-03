from django.urls import path

from . import views

app_name = "tracker"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("workouts/", views.workout_list, name="workout_list"),
    path("workouts/<int:pk>/", views.workout_detail, name="workout_detail"),
]
from django.urls import path

from . import views

app_name = "tracker"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("workouts/", views.workout_list, name="workout_list"),
    path("workouts/add/", views.workout_create, name="workout_create"),
    path("workouts/<int:pk>/sets/add/", views.workout_set_create, name="workout_set_create"),
    path("workouts/<int:pk>/", views.workout_detail, name="workout_detail"),
    path("exercises/", views.exercise_list, name="exercise_list"),
    path("exercises/add/", views.exercise_create, name="exercise_create"),
]
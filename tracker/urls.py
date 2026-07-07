from django.urls import path

from . import views

app_name = "tracker"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("workouts/", views.workout_list, name="workout_list"),
    path("workouts/add/", views.workout_create, name="workout_create"),
    path("workouts/<int:pk>/sets/add/", views.workout_set_create, name="workout_set_create"),
    path("workouts/<int:pk>/edit/", views.workout_update, name="workout_update"),
    path("workouts/<int:pk>/delete/", views.workout_delete, name="workout_delete"),
    path("workouts/<int:pk>/duplicate/", views.workout_duplicate, name="workout_duplicate"),
    path("workouts/<int:pk>/", views.workout_detail, name="workout_detail"),
    path("templates/", views.template_list, name="template_list"),
    path("templates/add/", views.template_create, name="template_create"),
    path("templates/<int:pk>/", views.template_detail, name="template_detail"),
    path("templates/<int:pk>/sets/add/", views.template_set_create, name="template_set_create"),
    path("templates/<int:pk>/start/", views.template_start_workout, name="template_start_workout"),
    path("exercises/", views.exercise_list, name="exercise_list"),
    path("exercises/add/", views.exercise_create, name="exercise_create"),
    path("exercises/<int:pk>/", views.exercise_detail, name="exercise_detail"),
    path("exercises/<int:pk>/edit/", views.exercise_update, name="exercise_update"),
    path("exercises/<int:pk>/delete/", views.exercise_delete, name="exercise_delete"),
    path("metrics/", views.body_metric_list, name="body_metric_list"),
    path("metrics/add/", views.body_metric_create, name="body_metric_create"),
    path("metrics/<int:pk>/edit/", views.body_metric_update, name="body_metric_update"),
    path("metrics/<int:pk>/delete/", views.body_metric_delete, name="body_metric_delete"),
    path("sets/<int:pk>/edit/", views.workout_set_update, name="workout_set_update"),
    path("sets/<int:pk>/delete/", views.workout_set_delete, name="workout_set_delete"),
    path("goals/", views.goal_list, name="goal_list"),
    path("goals/add/", views.goal_create, name="goal_create"),
    path("goals/<int:pk>/edit/", views.goal_update, name="goal_update"),
    path("goals/<int:pk>/delete/", views.goal_delete, name="goal_delete"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.profile_update, name="profile_update"),
]
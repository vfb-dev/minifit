from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Workout

@login_required
def dashboard(request):
    recent_workouts = Workout.objects.filter(user=request.user)[:5]
    workout_count = Workout.objects.filter(user=request.user).count()

    return render(
        request,
        "tracker/dashboard.html",
        {
            "recent_workouts": recent_workouts,
            "workout_count": workout_count,
        },
    )

@login_required
def workout_list(request):
    workouts = Workout.objects.filter(user=request.user)

    return render(
        request,
        "tracker/workout_list.html",
        {
            "workouts": workouts,
        },
    )

@login_required
def workout_detail(request, pk):
    workout = get_object_or_404(Workout, pk=pk, user=request.user)

    return render(
        request,
        "tracker/workout_detail.html",
        {
            "workout": workout,
        },
    )
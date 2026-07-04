from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Workout

from django.shortcuts import redirect
from django.utils import timezone

from .forms import WorkoutForm, WorkoutSetForm

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

@login_required
def workout_create(request):
    if request.method == "POST":
        form = WorkoutForm(request.POST)

        if form.is_valid():
            workout = form.save(commit=False)
            workout.user = request.user
            workout.save()
            return redirect("tracker:workout_detail", pk=workout.pk)
    else:
        form = WorkoutForm(initial={"date": timezone.localdate()})

    return render(
        request,
        "tracker/workout_form.html",
        {
            "form": form,
        },
    )

@login_required
def workout_set_create(request, pk):
    workout = get_object_or_404(Workout, pk=pk, user=request.user)

    if request.method == "POST":
        form = WorkoutSetForm(request.POST)

        if form.is_valid():
            workout_set = form.save(commit=False)
            workout_set.workout = workout
            workout_set.save()
            return redirect("tracker:workout_detail", pk=workout.pk)
    else:
        next_set_number = workout.sets.count() + 1
        form = WorkoutSetForm(initial={"set_number": next_set_number})

    return render(
        request,
        "tracker/workout_set_form.html",
        {
            "form": form,
            "workout": workout,
        },
    )
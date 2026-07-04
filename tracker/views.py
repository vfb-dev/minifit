from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import BodyMetric, Exercise, Workout, WorkoutSet

from django.shortcuts import redirect
from django.utils import timezone

from .forms import BodyMetricForm, ExerciseForm, WorkoutForm, WorkoutSetForm

@login_required
def dashboard(request):
    workouts = Workout.objects.filter(user=request.user)
    recent_workouts = workouts[:5]

    workout_count = workouts.count()
    total_sets = WorkoutSet.objects.filter(workout__user=request.user).count()
    exercise_count = Exercise.objects.count()
    latest_metric = BodyMetric.objects.filter(user=request.user).first()

    return render(
        request,
        "tracker/dashboard.html",
        {
            "recent_workouts": recent_workouts,
            "workout_count": workout_count,
            "total_sets": total_sets,
            "exercise_count": exercise_count,
            "latest_metric": latest_metric,
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

@login_required
def exercise_list(request):
    exercises = Exercise.objects.order_by("name")

    return render(
        request,
        "tracker/exercise_list.html",
        {
            "exercises": exercises,
        },
    )

@login_required
def exercise_create(request):
    if request.method == "POST":
        form = ExerciseForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("tracker:exercise_list")
    else:
        form = ExerciseForm()

    return render(
        request,
        "tracker/exercise_form.html",
        {
            "form": form,
        },
    )

@login_required
def body_metric_list(request):
    metrics = BodyMetric.objects.filter(user=request.user)

    return render(
        request,
        "tracker/body_metric_list.html",
        {"metrics": metrics},
    )

@login_required
def body_metric_create(request):
    if request.method == "POST":
        form = BodyMetricForm(request.POST)

        if form.is_valid():
            metric = form.save(commit=False)
            metric.user = request.user
            metric.save()
            return redirect("tracker:body_metric_list")
    else:
        form = BodyMetricForm(initial={"date": timezone.localdate()})

    return render(
        request,
        "tracker/body_metric_form.html",
        {"form": form},
    )
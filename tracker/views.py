from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from .forms import BodyMetricForm, ExerciseForm, GoalForm, WorkoutForm, WorkoutSetForm
from .models import BodyMetric, Exercise, Goal, Workout, WorkoutSet

from datetime import timedelta

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("tracker:dashboard")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})

@login_required
def dashboard(request):
    workouts = Workout.objects.filter(user=request.user)
    recent_workouts = workouts[:5]

    workout_count = workouts.count()
    total_sets = WorkoutSet.objects.filter(workout__user=request.user).count()
    exercise_count = Exercise.objects.count()
    latest_metric = BodyMetric.objects.filter(user=request.user).first()
    active_goals = Goal.objects.filter(user=request.user, completed=False).count()

    metrics = BodyMetric.objects.filter(user=request.user).order_by("date")[:20]
    weight_labels = [metric.date.strftime("%b %d") for metric in metrics]
    weight_values = [float(metric.weight_kg) for metric in metrics]

    today = timezone.localdate()
    current_week_start = today - timedelta(days=today.weekday())

    workout_week_labels = []
    workout_week_values = []

    for weeks_ago in range(7, -1, -1):
        week_start = current_week_start - timedelta(weeks=weeks_ago)
        week_end = week_start + timedelta(days=6)

        workout_week_labels.append(week_start.strftime("%b %d"))
        workout_week_values.append(
            workouts.filter(date__range=[week_start, week_end]).count()
        )

    return render(
        request,
        "tracker/dashboard.html",
        {
            "recent_workouts": recent_workouts,
            "workout_count": workout_count,
            "total_sets": total_sets,
            "exercise_count": exercise_count,
            "latest_metric": latest_metric,
            "active_goals": active_goals,
            "weight_labels": weight_labels,
            "weight_values": weight_values,
            "workout_week_labels": workout_week_labels,
            "workout_week_values": workout_week_values,
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
def workout_update(request, pk):
    workout = get_object_or_404(Workout, pk=pk, user=request.user)

    if request.method == "POST":
        form = WorkoutForm(request.POST, instance=workout)

        if form.is_valid():
            form.save()
            return redirect("tracker:workout_detail", pk=workout.pk)
    else:
        form = WorkoutForm(instance=workout)

    return render(
        request,
        "tracker/workout_form.html",
        {
            "form": form,
            "workout": workout,
            "is_editing": True,
        },
    )

@login_required
def workout_delete(request, pk):
    workout = get_object_or_404(Workout, pk=pk, user=request.user)

    if request.method == "POST":
        workout.delete()
        return redirect("tracker:workout_list")

    return render(
        request,
        "tracker/workout_confirm_delete.html",
        {
            "workout": workout,
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
def workout_set_update(request, pk):
    workout_set = get_object_or_404(WorkoutSet, pk=pk, workout__user=request.user)
    workout = workout_set.workout

    if request.method == "POST":
        form = WorkoutSetForm(request.POST, instance=workout_set)

        if form.is_valid():
            form.save()
            return redirect("tracker:workout_detail", pk=workout.pk)
    else:
        form = WorkoutSetForm(instance=workout_set)

    return render(
        request,
        "tracker/workout_set_form.html",
        {
            "form": form,
            "workout": workout,
            "is_editing": True,
        },
    )

@login_required
def workout_set_delete(request, pk):
    workout_set = get_object_or_404(WorkoutSet, pk=pk, workout__user=request.user)
    workout = workout_set.workout

    if request.method == "POST":
        workout_set.delete()
        return redirect("tracker:workout_detail", pk=workout.pk)

    return render(
        request,
        "tracker/workout_set_confirm_delete.html",
        {
            "workout_set": workout_set,
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
def exercise_update(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)

    if request.method == "POST":
        form = ExerciseForm(request.POST, instance=exercise)

        if form.is_valid():
            form.save()
            return redirect("tracker:exercise_list")
    else:
        form = ExerciseForm(instance=exercise)

    return render(
        request,
        "tracker/exercise_form.html",
        {
            "form": form,
            "exercise": exercise,
            "is_editing": True,
        },
    )

@login_required
def exercise_delete(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)

    if request.method == "POST":
        exercise.delete()
        return redirect("tracker:exercise_list")

    return render(
        request,
        "tracker/exercise_confirm_delete.html",
        {
            "exercise": exercise,
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

@login_required
def body_metric_update(request, pk):
    metric = get_object_or_404(BodyMetric, pk=pk, user=request.user)

    if request.method == "POST":
        form = BodyMetricForm(request.POST, instance=metric)

        if form.is_valid():
            form.save()
            return redirect("tracker:body_metric_list")
    else:
        form = BodyMetricForm(instance=metric)

    return render(
        request,
        "tracker/body_metric_form.html",
        {
            "form": form,
            "metric": metric,
            "is_editing": True,
        },
    )

@login_required
def body_metric_delete(request, pk):
    metric = get_object_or_404(BodyMetric, pk=pk, user=request.user)

    if request.method == "POST":
        metric.delete()
        return redirect("tracker:body_metric_list")

    return render(
        request,
        "tracker/body_metric_confirm_delete.html",
        {
            "metric": metric,
        },
    )

@login_required
def goal_list(request):
    goals = Goal.objects.filter(user=request.user).order_by("completed", "deadline")

    return render(request, "tracker/goal_list.html", {"goals": goals})

@login_required
def goal_create(request):
    if request.method == "POST":
        form = GoalForm(request.POST)

        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect("tracker:goal_list")
    else:
        form = GoalForm()

    return render(request, "tracker/goal_form.html", {"form": form})

@login_required
def goal_update(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)

    if request.method == "POST":
        form = GoalForm(request.POST, instance=goal)

        if form.is_valid():
            form.save()
            return redirect("tracker:goal_list")
    else:
        form = GoalForm(instance=goal)

    return render(request, "tracker/goal_form.html", {"form": form, "is_editing": True})

@login_required
def goal_delete(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)

    if request.method == "POST":
        goal.delete()
        return redirect("tracker:goal_list")

    return render(request, "tracker/goal_confirm_delete.html", {"goal": goal})
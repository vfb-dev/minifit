from django.conf import settings
from django.db import models
from django.utils import timezone


class Exercise(models.Model):
    MUSCLE_GROUPS = [
        ("chest", "Chest"),
        ("back", "Back"),
        ("legs", "Legs"),
        ("shoulders", "Shoulders"),
        ("arms", "Arms"),
        ("core", "Core"),
        ("cardio", "Cardio"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=120, unique=True)
    muscle_group = models.CharField(max_length=20, choices=MUSCLE_GROUPS, default="other")

    def __str__(self):
        return self.name


class Workout(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workouts",
    )
    title = models.CharField(max_length=120, default="Workout")
    date = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.title} - {self.date}"


class WorkoutSet(models.Model):
    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,
        related_name="sets",
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name="workout_sets",
    )
    set_number = models.PositiveIntegerField(default=1)
    reps = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["set_number"]

    def __str__(self):
        return f"{self.exercise.name} - set {self.set_number}"


class BodyMetric(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="body_metrics",
    )
    date = models.DateField(default=timezone.localdate)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2)
    body_fat_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user} - {self.date} - {self.weight_kg}kg"


class Goal(models.Model):
    GOAL_TYPES = [
        ("weight", "Weight"),
        ("strength", "Strength"),
        ("habit", "Habit"),
        ("cardio", "Cardio"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="goals",
    )
    title = models.CharField(max_length=120)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES, default="other")
    target_value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=30, blank=True)
    deadline = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title
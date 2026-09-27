from django.db import models
from django.conf import settings


class BodyPart(models.TextChoices):
    CHEST = "chest", "Chest"
    BACK = "back", "Back"
    SHOULDERS = "shoulders", "Shoulders"
    BICEPS = "biceps", "Biceps"
    TRICEPS = "triceps", "Triceps"
    LEGS = "legs", "Legs"
    GLUTES = "glutes", "Glutes"
    CORE = "core", "Core"
    CARDIO = "cardio", "Cardio"
    FULL_BODY = "full_body", "Full body"
    OTHER = "other", "Other"


class Exercise(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exercise_catalog",
    )
    name = models.CharField(max_length=100)
    primary_body_part = models.CharField(
        max_length=40,
        choices=BodyPart.choices,
        blank=True,
    )
    secondary_body_parts = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_exercise_name_per_user",
            )
        ]

    def __str__(self):
        return self.name


class ExerciseSet(models.Model):
    class WorkoutType(models.TextChoices):
        STRENGTH = "strength", "Strength"
        CARDIO = "cardio", "Cardio"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exercise_sets",
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.PROTECT,
        related_name="sets",
        null=True,
        blank=True,
    )
    workout_type = models.CharField(
        max_length=8, choices=WorkoutType.choices, default=WorkoutType.STRENGTH
    )
    cardio_activity = models.CharField(max_length=100, blank=True)
    date = models.DateTimeField()
    reps = models.PositiveIntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    distance_km = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    calories_burned = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        if self.workout_type == self.WorkoutType.CARDIO:
            name = self.exercise.name if self.exercise_id else self.cardio_activity
            return f"{name} ({self.duration_minutes} min)"
        return f"{self.exercise.name} ({self.reps} reps @ {self.weight}kg)"


class WorkoutRoutine(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workout_routines",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_routine_name_per_user",
            )
        ]

    def __str__(self):
        return self.name


class WorkoutRoutineExercise(models.Model):
    routine = models.ForeignKey(
        WorkoutRoutine,
        on_delete=models.CASCADE,
        related_name="items",
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.PROTECT,
        related_name="routine_items",
    )
    order = models.PositiveIntegerField(default=0)
    target_sets = models.PositiveIntegerField(default=3)
    target_reps = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["routine", "exercise"],
                name="unique_exercise_per_routine",
            )
        ]

    def __str__(self):
        return f"{self.routine.name}: {self.exercise.name}"

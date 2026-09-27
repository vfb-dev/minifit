from django.contrib import admin
from .models import Exercise, ExerciseSet, WorkoutRoutine, WorkoutRoutineExercise


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "primary_body_part", "user", "updated_at")
    search_fields = ("name", "user__email", "user__username")
    list_filter = ("primary_body_part",)


@admin.register(ExerciseSet)
class ExerciseSetAdmin(admin.ModelAdmin):
    list_display = (
        "workout_type", "exercise", "cardio_activity", "reps", "weight",
        "duration_minutes", "distance_km", "calories_burned", "date", "user",
    )
    search_fields = ("exercise__name", "cardio_activity", "user__email", "user__username")
    list_filter = ("workout_type", "date")


class WorkoutRoutineExerciseInline(admin.TabularInline):
    model = WorkoutRoutineExercise
    extra = 0


@admin.register(WorkoutRoutine)
class WorkoutRoutineAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "exercise_total", "updated_at")
    search_fields = ("name", "description", "user__email", "user__username")
    inlines = [WorkoutRoutineExerciseInline]

    def exercise_total(self, obj):
        return obj.items.count()

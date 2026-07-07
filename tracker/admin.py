from django.contrib import admin

from .models import BodyMetric, Exercise, Goal, Workout, WorkoutSet, WorkoutTemplate, WorkoutTemplateSet


class WorkoutSetInline(admin.TabularInline):
    model = WorkoutSet
    extra = 1

class WorkoutTemplateSetInline(admin.TabularInline):
    model = WorkoutTemplateSet
    extra = 1

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "muscle_group")
    search_fields = ("name",)
    list_filter = ("muscle_group",)

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "date", "created_at")
    list_filter = ("date",)
    search_fields = ("title", "notes", "user__username")
    inlines = [WorkoutSetInline]

@admin.register(WorkoutSet)
class WorkoutSetAdmin(admin.ModelAdmin):
    list_display = ("workout", "exercise", "set_number", "reps", "weight_kg", "duration_minutes", "distance_km")
    list_filter = ("exercise",)

@admin.register(WorkoutTemplate)
class WorkoutTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at")
    search_fields = ("name", "notes", "user__username")
    inlines = [WorkoutTemplateSetInline]

@admin.register(WorkoutTemplateSet)
class WorkoutTemplateSetAdmin(admin.ModelAdmin):
    list_display = ("template", "exercise", "set_number", "reps", "weight_kg", "duration_minutes", "distance_km")
    list_filter = ("exercise",)

@admin.register(BodyMetric)
class BodyMetricAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "weight_kg", "body_fat_percentage")
    list_filter = ("date",)
    search_fields = ("user__username",)

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "goal_type", "target_value", "unit", "deadline", "completed")
    list_filter = ("goal_type", "completed", "deadline")
    search_fields = ("title", "user__username")
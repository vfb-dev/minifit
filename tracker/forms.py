from django import forms
from django.contrib.auth import get_user_model

from .models import BodyMetric, Exercise, Goal, Workout, WorkoutSet, WorkoutTemplate, WorkoutTemplateSet

User = get_user_model()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ["title", "date", "notes"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

class WorkoutSetForm(forms.ModelForm):
    class Meta:
        model = WorkoutSet
        fields = [
            "exercise",
            "set_number",
            "reps",
            "weight_kg",
            "duration_minutes",
            "distance_km",
        ]
        widgets = {
            "exercise": forms.Select(attrs={"class": "form-select"}),
            "set_number": forms.NumberInput(attrs={"class": "form-control"}),
            "reps": forms.NumberInput(attrs={"class": "form-control"}),
            "weight_kg": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "duration_minutes": forms.NumberInput(attrs={"class": "form-control"}),
            "distance_km": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }

class WorkoutTemplateForm(forms.ModelForm):
    class Meta:
        model = WorkoutTemplate
        fields = ["name", "notes"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class WorkoutTemplateSetForm(forms.ModelForm):
    class Meta:
        model = WorkoutTemplateSet
        fields = ["exercise", "set_number", "reps", "weight_kg", "duration_minutes", "distance_km"]
        widgets = {
            "exercise": forms.Select(attrs={"class": "form-select"}),
            "set_number": forms.NumberInput(attrs={"class": "form-control"}),
            "reps": forms.NumberInput(attrs={"class": "form-control"}),
            "weight_kg": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "duration_minutes": forms.NumberInput(attrs={"class": "form-control"}),
            "distance_km": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ["name", "muscle_group"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "muscle_group": forms.Select(attrs={"class": "form-select"}),
        }

class BodyMetricForm(forms.ModelForm):
    class Meta:
        model = BodyMetric
        fields = ["date", "weight_kg", "body_fat_percentage", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "weight_kg": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "body_fat_percentage": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ["title", "goal_type", "target_value", "unit", "deadline", "completed"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "goal_type": forms.Select(attrs={"class": "form-select"}),
            "target_value": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "unit": forms.TextInput(attrs={"class": "form-control", "placeholder": "kg, workouts, km..."}),
            "deadline": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "completed": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
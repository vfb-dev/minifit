from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import BodyMetric, Exercise, Goal, Workout, WorkoutSet, WorkoutTemplate, WorkoutTemplateSet

User = get_user_model()


class SetValidationMixin:
    performance_fields = ["reps", "weight_kg", "duration_minutes", "distance_km"]

    def clean(self):
        cleaned_data = super().clean()

        set_number = cleaned_data.get("set_number")
        reps = cleaned_data.get("reps")
        weight_kg = cleaned_data.get("weight_kg")
        duration_minutes = cleaned_data.get("duration_minutes")
        distance_km = cleaned_data.get("distance_km")

        if set_number is not None and set_number < 1:
            self.add_error("set_number", "Set number must be at least 1.")

        if reps is not None and reps < 1:
            self.add_error("reps", "Reps must be at least 1.")

        if weight_kg is not None and weight_kg < 0:
            self.add_error("weight_kg", "Weight cannot be negative.")

        if duration_minutes is not None and duration_minutes < 1:
            self.add_error("duration_minutes", "Duration must be at least 1 minute.")

        if distance_km is not None and distance_km < 0:
            self.add_error("distance_km", "Distance cannot be negative.")

        if not any(cleaned_data.get(field) is not None for field in self.performance_fields):
            raise forms.ValidationError("Add reps, weight, duration, or distance for this set.")

        return cleaned_data

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

    def clean_date(self):
        workout_date = self.cleaned_data["date"]

        if workout_date > timezone.localdate():
            raise forms.ValidationError("Workout date cannot be in the future.")

        return workout_date

class WorkoutSetForm(SetValidationMixin, forms.ModelForm):
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
            "set_number": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "reps": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "weight_kg": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
            "duration_minutes": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "distance_km": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
        }

class WorkoutTemplateForm(forms.ModelForm):
    class Meta:
        model = WorkoutTemplate
        fields = ["name", "notes"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class WorkoutTemplateSetForm(SetValidationMixin, forms.ModelForm):
    class Meta:
        model = WorkoutTemplateSet
        fields = ["exercise", "set_number", "reps", "weight_kg", "duration_minutes", "distance_km"]
        widgets = {
            "exercise": forms.Select(attrs={"class": "form-select"}),
            "set_number": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "reps": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "weight_kg": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
            "duration_minutes": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "distance_km": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
        }

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ["name", "muscle_group"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "muscle_group": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_name(self):
        return self.cleaned_data["name"].strip()

class BodyMetricForm(forms.ModelForm):
    class Meta:
        model = BodyMetric
        fields = ["date", "weight_kg", "body_fat_percentage", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "weight_kg": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0.01"}),
            "body_fat_percentage": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0, "max": 100}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean_date(self):
        metric_date = self.cleaned_data["date"]

        if metric_date > timezone.localdate():
            raise forms.ValidationError("Metric date cannot be in the future.")

        return metric_date

    def clean_weight_kg(self):
        weight_kg = self.cleaned_data["weight_kg"]

        if weight_kg <= 0:
            raise forms.ValidationError("Weight must be greater than 0.")

        return weight_kg

    def clean_body_fat_percentage(self):
        body_fat_percentage = self.cleaned_data.get("body_fat_percentage")

        if body_fat_percentage is not None and not 0 <= body_fat_percentage <= 100:
            raise forms.ValidationError("Body fat must be between 0 and 100.")

        return body_fat_percentage

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ["title", "goal_type", "target_value", "unit", "deadline", "completed"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "goal_type": forms.Select(attrs={"class": "form-select"}),
            "target_value": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
            "unit": forms.TextInput(attrs={"class": "form-control", "placeholder": "kg, workouts, km..."}),
            "deadline": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "completed": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_target_value(self):
        target_value = self.cleaned_data.get("target_value")

        if target_value is not None and target_value < 0:
            raise forms.ValidationError("Target value cannot be negative.")

        return target_value

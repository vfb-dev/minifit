from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import BodyMetricForm, WorkoutForm, WorkoutSetForm
from .models import Exercise, Workout, WorkoutSet, WorkoutTemplate, WorkoutTemplateSet


User = get_user_model()


class FormValidationTests(TestCase):
    def setUp(self):
        self.exercise = Exercise.objects.create(name="Bench Press", muscle_group="chest")

    def test_workout_form_rejects_future_dates(self):
        form = WorkoutForm(
            data={
                "title": "Future workout",
                "date": timezone.localdate() + timedelta(days=1),
                "notes": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    def test_workout_set_form_requires_positive_useful_values(self):
        empty_form = WorkoutSetForm(
            data={
                "exercise": self.exercise.pk,
                "set_number": 1,
                "reps": "",
                "weight_kg": "",
                "duration_minutes": "",
                "distance_km": "",
            }
        )

        self.assertFalse(empty_form.is_valid())
        self.assertIn("__all__", empty_form.errors)

        negative_form = WorkoutSetForm(
            data={
                "exercise": self.exercise.pk,
                "set_number": 1,
                "reps": 8,
                "weight_kg": "-10",
                "duration_minutes": "",
                "distance_km": "",
            }
        )

        self.assertFalse(negative_form.is_valid())
        self.assertIn("weight_kg", negative_form.errors)

    def test_body_metric_form_rejects_future_date_and_invalid_body_fat(self):
        form = BodyMetricForm(
            data={
                "date": timezone.localdate() + timedelta(days=1),
                "weight_kg": "80.00",
                "body_fat_percentage": "120",
                "notes": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)
        self.assertIn("body_fat_percentage", form.errors)


class TrackerViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="victor", password="pass12345")
        self.other_user = User.objects.create_user(username="other", password="pass12345")
        self.exercise = Exercise.objects.create(name="Squat", muscle_group="legs")

    def test_workout_detail_requires_owner(self):
        workout = Workout.objects.create(
            user=self.other_user,
            title="Other workout",
            date=timezone.localdate(),
        )

        self.client.login(username="victor", password="pass12345")
        response = self.client.get(reverse("tracker:workout_detail", args=[workout.pk]))

        self.assertEqual(response.status_code, 404)

    def test_calendar_shows_user_workout(self):
        workout = Workout.objects.create(
            user=self.user,
            title="Leg Day",
            date=timezone.localdate(),
        )

        self.client.login(username="victor", password="pass12345")
        response = self.client.get(
            reverse("tracker:workout_calendar"),
            {"year": workout.date.year, "month": workout.date.month},
        )

        self.assertContains(response, "Leg Day")

    def test_template_start_creates_workout_with_sets(self):
        template = WorkoutTemplate.objects.create(user=self.user, name="Push Day")
        WorkoutTemplateSet.objects.create(
            template=template,
            exercise=self.exercise,
            set_number=1,
            reps=10,
            weight_kg=Decimal("50.00"),
        )

        self.client.login(username="victor", password="pass12345")
        response = self.client.post(reverse("tracker:template_start_workout", args=[template.pk]))

        self.assertEqual(response.status_code, 302)
        workout = Workout.objects.get(user=self.user, title="Push Day")
        self.assertEqual(workout.sets.count(), 1)
        self.assertEqual(workout.sets.first().exercise, self.exercise)

    def test_workout_csv_export_only_includes_current_user_data(self):
        own_workout = Workout.objects.create(
            user=self.user,
            title="My Workout",
            date=timezone.localdate(),
        )
        other_workout = Workout.objects.create(
            user=self.other_user,
            title="Hidden Workout",
            date=timezone.localdate(),
        )
        WorkoutSet.objects.create(
            workout=own_workout,
            exercise=self.exercise,
            set_number=1,
            reps=5,
            weight_kg=Decimal("100.00"),
        )
        WorkoutSet.objects.create(
            workout=other_workout,
            exercise=self.exercise,
            set_number=1,
            reps=5,
            weight_kg=Decimal("100.00"),
        )

        self.client.login(username="victor", password="pass12345")
        response = self.client.get(reverse("tracker:export_workouts_csv"))
        content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("My Workout", content)
        self.assertNotIn("Hidden Workout", content)

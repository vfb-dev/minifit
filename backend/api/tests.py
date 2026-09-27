from datetime import date
from importlib import import_module

from django.test import SimpleTestCase
from django.contrib.auth import get_user_model
from django.apps import apps
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Exercise, ExerciseSet
from .views import calculate_workout_streaks


class WorkoutStreakTests(SimpleTestCase):
    def test_streak_stays_active_before_four_rest_days(self):
        workout_days = [
            date(2026, 8, 24),
            date(2026, 8, 28),
        ]

        streak, max_streak = calculate_workout_streaks(
            workout_days,
            date(2026, 8, 31),
        )

        self.assertEqual(streak, 2)
        self.assertEqual(max_streak, 2)

    def test_streak_resets_after_four_rest_days(self):
        workout_days = [
            date(2026, 8, 24),
            date(2026, 8, 28),
        ]

        streak, max_streak = calculate_workout_streaks(
            workout_days,
            date(2026, 9, 1),
        )

        self.assertEqual(streak, 0)
        self.assertEqual(max_streak, 2)


class CardioWorkoutTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="cardio@example.com", password="testpass123", username="cardio"
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/v1/exercise-sets/"
        self.date = timezone.now().isoformat()
        self.cardio_exercise = Exercise.objects.create(
            user=self.user, name="running", primary_body_part="cardio"
        )

    def test_cardio_can_be_logged_edited_and_shown_in_history_and_stats(self):
        response = self.client.post(self.url, {
            "workout_type": "cardio",
            "exercise": self.cardio_exercise.id,
            "duration_minutes": 30,
            "distance_km": "5.25",
            "calories_burned": 320,
            "date": self.date,
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "running")
        self.assertEqual(response.data["exercise"], self.cardio_exercise.id)
        self.assertEqual(response.data["calories_burned"], 320)
        workout_id = response.data["id"]

        history = self.client.get(self.url + "history/")
        self.assertEqual(history.status_code, 200)
        self.assertEqual(history.data["results"][0]["workout_type"], "cardio")
        self.assertEqual(history.data["results"][0]["exercises"][0]["duration_minutes"], 30)
        self.assertEqual(history.data["results"][0]["exercises"][0]["calories_burned"], 320)

        stats = self.client.get(self.url + "stats_cards/")
        self.assertEqual(stats.data["total_workouts"], 1)

        for metric, expected in (("duration", 30), ("distance", 5.25), ("calories", 320)):
            chart = self.client.get(
                self.url + f"chart/?workout_type=cardio&exercise={self.cardio_exercise.id}&metric={metric}&period=30D"
            )
            self.assertEqual(chart.status_code, 200)
            self.assertEqual(sum(float(point["value"]) for point in chart.data), expected)

        updated = self.client.put(self.url + f"{workout_id}/", {
            "workout_type": "cardio",
            "exercise": self.cardio_exercise.id,
            "duration_minutes": 45,
            "distance_km": None,
            "calories_burned": 450,
            "date": self.date,
        }, format="json")
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data["name"], "running")
        self.assertIsNone(updated.data["distance_km"])
        self.assertEqual(updated.data["calories_burned"], 450)

        chart = self.client.get(
            self.url + f"chart/?workout_type=cardio&exercise={self.cardio_exercise.id}&metric=calories&period=30D"
        )
        self.assertEqual(chart.status_code, 200)
        self.assertEqual(sum(point["value"] for point in chart.data), 450)

    def test_cardio_requires_exercise_and_positive_duration(self):
        response = self.client.post(self.url, {
            "workout_type": "cardio",
            "duration_minutes": 0,
            "date": self.date,
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("exercise", response.data)

    def test_strength_still_uses_reps_and_weight_and_cardio_is_excluded_from_chart(self):
        exercise = Exercise.objects.create(user=self.user, name="squat")
        strength = self.client.post(self.url, {
            "exercise": exercise.id,
            "date": self.date,
            "reps": 8,
            "weight": "60.00",
        })
        self.assertEqual(strength.status_code, 201)
        self.assertEqual(strength.data["workout_type"], "strength")
        self.client.post(self.url, {
            "workout_type": "cardio",
            "exercise": self.cardio_exercise.id,
            "duration_minutes": 30,
            "date": self.date,
        })
        self.assertEqual(ExerciseSet.objects.count(), 2)
        chart = self.client.get(self.url + "chart/?metric=reps&period=30D")
        self.assertEqual(chart.status_code, 200)
        self.assertEqual(sum(point["value"] for point in chart.data), 8)

    def test_edit_can_switch_between_strength_and_cardio(self):
        exercise = Exercise.objects.create(user=self.user, name="squat")
        created = self.client.post(self.url, {
            "exercise": exercise.id,
            "date": self.date,
            "reps": 8,
            "weight": "60.00",
        })
        workout_url = self.url + f"{created.data['id']}/"

        cardio = self.client.put(workout_url, {
            "workout_type": "cardio",
            "exercise": self.cardio_exercise.id,
            "duration_minutes": 20,
            "date": self.date,
        })
        self.assertEqual(cardio.status_code, 200)
        self.assertEqual(cardio.data["exercise"], self.cardio_exercise.id)
        self.assertIsNone(cardio.data["reps"])

        strength = self.client.put(workout_url, {
            "workout_type": "strength",
            "exercise": exercise.id,
            "reps": 10,
            "weight": "65.00",
            "date": self.date,
        })
        self.assertEqual(strength.status_code, 200)
        self.assertEqual(strength.data["reps"], 10)
        self.assertIsNone(strength.data["duration_minutes"])

    def test_existing_free_text_cardio_is_linked_to_exercise(self):
        old = ExerciseSet.objects.create(
            user=self.user,
            workout_type="cardio",
            cardio_activity="Cycling",
            duration_minutes=25,
            date=timezone.now(),
        )
        migration = import_module("api.migrations.0009_cardio_exercise_and_calories")
        migration.link_existing_cardio_workouts(apps, None)
        old.refresh_from_db()
        self.assertEqual(old.exercise.name, "cycling")
        self.assertEqual(old.exercise.primary_body_part, "cardio")

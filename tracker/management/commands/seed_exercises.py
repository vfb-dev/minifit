from django.core.management.base import BaseCommand

from tracker.models import Exercise


EXERCISES = [
    ("Bench Press", "chest"),
    ("Push Up", "chest"),
    ("Incline Dumbbell Press", "chest"),
    ("Pull Up", "back"),
    ("Barbell Row", "back"),
    ("Lat Pulldown", "back"),
    ("Squat", "legs"),
    ("Deadlift", "legs"),
    ("Leg Press", "legs"),
    ("Shoulder Press", "shoulders"),
    ("Lateral Raise", "shoulders"),
    ("Bicep Curl", "arms"),
    ("Tricep Pushdown", "arms"),
    ("Plank", "core"),
    ("Crunch", "core"),
    ("Running", "cardio"),
    ("Cycling", "cardio"),
    ("Walking", "cardio"),
]


class Command(BaseCommand):
    help = "Seed shared exercises for DJ Fit."

    def handle(self, *args, **options):
        created_count = 0

        for name, muscle_group in EXERCISES:
            _, created = Exercise.objects.get_or_create(
                name=name,
                defaults={
                    "muscle_group": muscle_group,
                    "created_by": None,
                },
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Seeded {created_count} new exercises.")
        )
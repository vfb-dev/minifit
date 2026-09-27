from django.db import migrations, models


def link_existing_cardio_workouts(apps, schema_editor):
    Exercise = apps.get_model("api", "Exercise")
    ExerciseSet = apps.get_model("api", "ExerciseSet")

    for workout in ExerciseSet.objects.filter(
        workout_type="cardio", exercise__isnull=True
    ).iterator():
        name = (workout.cardio_activity or "").strip().lower() or "cardio"
        exercise = Exercise.objects.filter(
            user_id=workout.user_id, name__iexact=name
        ).first()
        if exercise is None:
            exercise = Exercise.objects.create(
                user_id=workout.user_id,
                name=name,
                primary_body_part="cardio",
            )
        workout.exercise_id = exercise.id
        workout.save(update_fields=["exercise"])


class Migration(migrations.Migration):
    dependencies = [("api", "0008_cardio_workouts")]

    operations = [
        migrations.AddField(
            model_name="exerciseset",
            name="calories_burned",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.RunPython(link_existing_cardio_workouts, migrations.RunPython.noop),
    ]

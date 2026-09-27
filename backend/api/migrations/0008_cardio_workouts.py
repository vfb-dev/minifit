from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("api", "0007_workout_routines")]

    operations = [
        migrations.AddField(
            model_name="exerciseset",
            name="workout_type",
            field=models.CharField(
                choices=[("strength", "Strength"), ("cardio", "Cardio")],
                default="strength",
                max_length=8,
            ),
        ),
        migrations.AddField(
            model_name="exerciseset",
            name="cardio_activity",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="exerciseset",
            name="duration_minutes",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="exerciseset",
            name="distance_km",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True),
        ),
        migrations.AlterField(
            model_name="exerciseset",
            name="exercise",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="sets",
                to="api.exercise",
            ),
        ),
        migrations.AlterField(
            model_name="exerciseset",
            name="reps",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="exerciseset",
            name="weight",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=6, null=True
            ),
        ),
    ]

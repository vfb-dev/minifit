from rest_framework import serializers
from .models import (
    BodyPart,
    Exercise,
    ExerciseSet,
    WorkoutRoutine,
    WorkoutRoutineExercise,
)

from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth.password_validation import validate_password
from django.utils.http import urlsafe_base64_decode
from users.tokens import password_reset_token

User = get_user_model()

VALID_BODY_PARTS = {value for value, _ in BodyPart.choices}


class ExerciseSerializer(serializers.ModelSerializer):
    set_count = serializers.IntegerField(read_only=True)
    last_logged_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Exercise
        fields = [
            "id",
            "name",
            "primary_body_part",
            "secondary_body_parts",
            "set_count",
            "last_logged_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

    def validate_name(self, value):
        name = value.strip().lower()

        if not name:
            raise serializers.ValidationError("Exercise name is required.")

        request = self.context.get("request")

        if request and request.user.is_authenticated:
            queryset = Exercise.objects.filter(user=request.user, name=name)

            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError("Exercise already exists.")

        return name

    def validate_secondary_body_parts(self, value):
        if value in (None, ""):
            return []

        if not isinstance(value, list):
            raise serializers.ValidationError("Secondary body parts must be a list.")

        body_parts = []
        for item in value:
            if not isinstance(item, str):
                raise serializers.ValidationError("Body parts must be text values.")

            body_part = item.strip().lower()

            if body_part not in VALID_BODY_PARTS:
                raise serializers.ValidationError(f"Invalid body part: {item}")

            if body_part not in body_parts:
                body_parts.append(body_part)

        return body_parts

    def validate(self, attrs):
        primary_body_part = attrs.get(
            "primary_body_part",
            self.instance.primary_body_part if self.instance else "",
        )
        secondary_body_parts = attrs.get(
            "secondary_body_parts",
            self.instance.secondary_body_parts if self.instance else [],
        )

        if primary_body_part:
            secondary_body_parts = [
                body_part
                for body_part in secondary_body_parts
                if body_part != primary_body_part
            ]

        attrs["secondary_body_parts"] = secondary_body_parts
        return attrs


class ExerciseSetSerializer(serializers.ModelSerializer):
    formatted_date = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = ExerciseSet
        fields = [
            "id",
            "exercise",
            "name",
            "workout_type",
            "cardio_activity",
            "date",
            "formatted_date",
            "reps",
            "weight",
            "duration_minutes",
            "distance_km",
            "calories_burned",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

    def validate_exercise(self, value):
        request = self.context.get("request")

        if value and request and value.user_id != request.user.id:
            raise serializers.ValidationError("Exercise not found.")

        return value

    def validate(self, attrs):
        workout_type = attrs.get(
            "workout_type",
            self.instance.workout_type if self.instance else ExerciseSet.WorkoutType.STRENGTH,
        )

        if workout_type == ExerciseSet.WorkoutType.CARDIO:
            exercise = attrs.get(
                "exercise", self.instance.exercise if self.instance else None
            )
            duration = attrs.get(
                "duration_minutes", self.instance.duration_minutes if self.instance else None
            )
            distance = attrs.get(
                "distance_km", self.instance.distance_km if self.instance else None
            )
            calories = attrs.get(
                "calories_burned", self.instance.calories_burned if self.instance else None
            )
            if exercise is None:
                raise serializers.ValidationError({"exercise": "Exercise is required."})
            if not duration or duration < 1:
                raise serializers.ValidationError({"duration_minutes": "Duration must be at least 1 minute."})
            if distance is not None and distance < 0:
                raise serializers.ValidationError({"distance_km": "Distance cannot be negative."})
            if calories is not None and calories < 0:
                raise serializers.ValidationError({"calories_burned": "Calories cannot be negative."})
            attrs.update(
                cardio_activity=exercise.name,
                reps=None,
                weight=None,
            )
        else:
            exercise = attrs.get(
                "exercise", self.instance.exercise if self.instance else None
            )
            reps = attrs.get("reps", self.instance.reps if self.instance else None)
            weight = attrs.get("weight", self.instance.weight if self.instance else None)
            if exercise is None:
                raise serializers.ValidationError({"exercise": "Exercise is required."})
            if reps is None or reps < 1:
                raise serializers.ValidationError({"reps": "Reps must be at least 1."})
            if weight is None or weight < 0:
                raise serializers.ValidationError({"weight": "Weight cannot be negative."})
            attrs.update(
                cardio_activity="",
                duration_minutes=None,
                distance_km=None,
                calories_burned=None,
            )

        return attrs

    def get_name(self, obj):
        if obj.workout_type == ExerciseSet.WorkoutType.CARDIO:
            return obj.exercise.name if obj.exercise_id else obj.cardio_activity
        return obj.exercise.name

    def get_formatted_date(self, obj):
        now = timezone.localtime()
        date = timezone.localtime(obj.date)

        # Same year → 24 May
        if date.year == now.year:
            return date.strftime("%d %b")

        # Different year → 15 Dec 2025
        return date.strftime("%d %b %Y")


class WorkoutRoutineItemSerializer(serializers.ModelSerializer):
    exercise_name = serializers.CharField(source="exercise.name", read_only=True)
    primary_body_part = serializers.CharField(
        source="exercise.primary_body_part",
        read_only=True,
    )
    secondary_body_parts = serializers.JSONField(
        source="exercise.secondary_body_parts",
        read_only=True,
    )

    class Meta:
        model = WorkoutRoutineExercise
        fields = [
            "id",
            "exercise",
            "exercise_name",
            "primary_body_part",
            "secondary_body_parts",
            "order",
            "target_sets",
            "target_reps",
        ]
        read_only_fields = [
            "id",
            "exercise_name",
            "primary_body_part",
            "secondary_body_parts",
        ]

    def validate_exercise(self, value):
        request = self.context.get("request")

        if request and value.user_id != request.user.id:
            raise serializers.ValidationError("Exercise not found.")

        return value

    def validate_target_sets(self, value):
        if value < 1:
            raise serializers.ValidationError("Target sets must be at least 1.")

        return value

    def validate_target_reps(self, value):
        if value is not None and value < 1:
            raise serializers.ValidationError("Target reps must be at least 1.")

        return value


class WorkoutRoutineSerializer(serializers.ModelSerializer):
    items = WorkoutRoutineItemSerializer(many=True)
    exercise_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = WorkoutRoutine
        fields = [
            "id",
            "name",
            "description",
            "items",
            "exercise_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

    def validate_name(self, value):
        name = value.strip().lower()

        if not name:
            raise serializers.ValidationError("Routine name is required.")

        request = self.context.get("request")

        if request and request.user.is_authenticated:
            queryset = WorkoutRoutine.objects.filter(user=request.user, name=name)

            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError("Routine already exists.")

        return name

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Add at least one exercise.")

        exercise_ids = []

        for item in value:
            exercise_id = item["exercise"].id

            if exercise_id in exercise_ids:
                raise serializers.ValidationError(
                    "Each exercise can appear only once in a routine."
                )

            exercise_ids.append(exercise_id)

        return value

    def create(self, validated_data):
        items = validated_data.pop("items", [])
        routine = WorkoutRoutine.objects.create(**validated_data)
        self.sync_items(routine, items)

        return routine

    def update(self, instance, validated_data):
        items = validated_data.pop("items", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if items is not None:
            instance.items.all().delete()
            self.sync_items(instance, items)

        return instance

    def sync_items(self, routine, items):
        for index, item in enumerate(items):
            WorkoutRoutineExercise.objects.create(
                routine=routine,
                exercise=item["exercise"],
                order=index,
                target_sets=item.get("target_sets", 3),
                target_reps=item.get("target_reps"),
            )


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return value

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
        )
    
class LoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_verified:
            raise serializers.ValidationError(
                "Please verify your email first."
            )

        return data
    
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        try:
            uid = urlsafe_base64_decode(attrs["uid"]).decode()
            user = User.objects.get(pk=uid)
        except Exception:
            raise serializers.ValidationError({
                "detail": "Invalid reset link."
            })

        if not password_reset_token.check_token(user, attrs["token"]):
            raise serializers.ValidationError({
                "detail": "Invalid or expired reset link."
            })

        validate_password(attrs["password"], user=user)

        attrs["user"] = user
        return attrs

    def save(self):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["password"])
        user.save()
        return user

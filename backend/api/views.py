from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Exercise, ExerciseSet, WorkoutRoutine
from .serializers import (
    ExerciseSerializer,
    ExerciseSetSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    WorkoutRoutineSerializer,
)
from .pagination import ExercisePagination

from django.db.models import Count, Sum, Max, F, Q
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from datetime import date, timedelta
from django.utils import timezone

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated

from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from users.tokens import email_verification_token, password_reset_token
from django.contrib.auth import get_user_model

User = get_user_model()

STREAK_RESET_AFTER_REST_DAYS = 4
STREAK_RESET_DELTA = timedelta(days=STREAK_RESET_AFTER_REST_DAYS)


def calculate_workout_streaks(workout_days: list[date], today: date):
    streak = 0
    max_streak = 0

    if not workout_days:
        return streak, max_streak

    current_streak = 0
    previous_day = None

    for day in workout_days:
        if previous_day is None or day - previous_day <= STREAK_RESET_DELTA:
            current_streak += 1
        else:
            current_streak = 1

        max_streak = max(max_streak, current_streak)
        previous_day = day

    last_workout_day = workout_days[-1]

    if today - last_workout_day < STREAK_RESET_DELTA:
        streak = current_streak

    return streak, max_streak


class WorkoutRoutineViewset(viewsets.ModelViewSet):
    serializer_class = WorkoutRoutineSerializer
    pagination_class = ExercisePagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = (
            WorkoutRoutine.objects
            .filter(user=self.request.user)
            .prefetch_related("items__exercise")
            .annotate(exercise_count=Count("items"))
        )

        search = self.request.query_params.get("search", "").strip()

        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset.order_by("name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ExerciseViewset(viewsets.ModelViewSet):
    serializer_class = ExerciseSerializer
    pagination_class = ExercisePagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = (
            Exercise.objects
            .filter(user=self.request.user)
            .annotate(
                set_count=Count("sets"),
                cardio_count=Count(
                    "sets", filter=Q(sets__workout_type=ExerciseSet.WorkoutType.CARDIO)
                ),
                strength_count=Count(
                    "sets", filter=Q(sets__workout_type=ExerciseSet.WorkoutType.STRENGTH)
                ),
                last_logged_at=Max("sets__date"),
            )
        )

        search = self.request.query_params.get("search", "").strip()

        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset.order_by("name")
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        exercise = self.get_object()

        if exercise.sets.exists():
            return Response(
                {"detail": "Cannot delete an exercise that has logged sets."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def options(self, request):
        exercises = self.get_queryset().values(
            "id",
            "name",
            "primary_body_part",
            "secondary_body_parts",
            "cardio_count",
            "strength_count",
        )

        return Response(exercises)


class ExerciseSetViewset(viewsets.ModelViewSet):
    serializer_class = ExerciseSetSerializer
    pagination_class = ExercisePagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            ExerciseSet.objects
            .filter(user=self.request.user)
            .select_related("exercise")
            .order_by("-date")
        )
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=["get"])
    def history(self, request):
        search = request.query_params.get("search")

        exercise_sets = self.get_queryset().only(
            "id",
            "exercise",
            "exercise__name",
            "workout_type",
            "cardio_activity",
            "date",
            "weight",
            "reps",
            "duration_minutes",
            "distance_km",
            "calories_burned",
        )

        if search:
            exercise_sets = exercise_sets.filter(
                Q(exercise__name__icontains=search)
                | Q(cardio_activity__icontains=search)
            )

        grouped = {}

        for exercise_set in exercise_sets:
            name = exercise_set.exercise.name if exercise_set.exercise_id else exercise_set.cardio_activity
            key = (
                exercise_set.workout_type,
                exercise_set.exercise_id or name,
                exercise_set.date.date(),
            )

            if key not in grouped:
                grouped[key] = {
                    "group_id": f"{exercise_set.workout_type}-{key[1]}-{exercise_set.date.date()}",
                    "exercise": exercise_set.exercise_id,
                    "name": name,
                    "workout_type": exercise_set.workout_type,
                    "date": exercise_set.date.strftime("%b %d"), 
                    "sets": 0 , 
                    "exercises":[]}

            grouped[key]["sets"] += 1
            grouped[key]["exercises"].append({
                "id": exercise_set.id,
                "exercise": exercise_set.exercise_id,
                "name": name,
                "workout_type": exercise_set.workout_type,
                "date": exercise_set.date,
                "weight": exercise_set.weight,
                "reps": exercise_set.reps,
                "cardio_activity": exercise_set.cardio_activity,
                "duration_minutes": exercise_set.duration_minutes,
                "distance_km": exercise_set.distance_km,
                "calories_burned": exercise_set.calories_burned,
            })

            for group in grouped.values():
                group["exercises"].sort(
                    key=lambda exercise: exercise["date"],
                    reverse=False # oldest first
                )

        history = list(grouped.values())

        page = self.paginate_queryset(history)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(history)

    @action(detail=False, methods=["get"])
    def chart(self, request):
        exercise = request.query_params.get("exercise")
        metric = request.query_params.get("metric", "volume")
        period  = request.query_params.get("period", "30D")
        workout_type = request.query_params.get("workout_type", "strength")

        valid_metrics = {
            "strength": {"volume", "weight", "reps"},
            "cardio": {"duration", "distance", "calories"},
        }
        if metric not in valid_metrics.get(workout_type, set()):
            return Response({"detail": "Invalid workout type or metric."}, status=400)

        queryset = self.get_queryset().filter(workout_type=workout_type)

        # filter exercise
        if exercise:
            queryset = queryset.filter(exercise_id=exercise)

        # filter period
        now = timezone.now()

        period_map = { "7D": 7, "30D": 30, "90D": 90, "1Y": 365,}
        
        if period in period_map:
            desired_period = now - timedelta(days=period_map[period])
            queryset = queryset.filter(date__gte=desired_period)

        # group by day
        if period in ["7D", "30D", "90D"]:
            queryset = queryset.annotate(group_date=TruncDay("date"))
        elif period == "1Y":
            queryset = queryset.annotate(group_date=TruncMonth("date"))
        else:
            queryset = queryset.annotate(group_date=TruncYear("date"))

        # metric logic
        if metric == "volume":
            queryset = queryset.annotate(calculated=F("weight") * F("reps")).values("group_date").annotate(value=Sum("calculated"))
        elif metric == "weight":
            queryset = queryset.values("group_date").annotate(value=Max("weight"))
        elif metric == "reps":
            queryset = queryset.values("group_date").annotate(value=Sum("reps"))
        elif metric == "duration":
            queryset = queryset.values("group_date").annotate(value=Sum("duration_minutes"))
        elif metric == "distance":
            queryset = queryset.filter(distance_km__isnull=False).values("group_date").annotate(value=Sum("distance_km"))
        elif metric == "calories":
            queryset = queryset.filter(calories_burned__isnull=False).values("group_date").annotate(value=Sum("calories_burned"))

        short_label_format = ""
        if period in ["7D", "30D", "90D"]:
            short_label_format = "%b %d"
        elif period == "1Y":
            short_label_format = "%b"
        else:
            short_label_format = "%Y"

        data = [
            {
                "label": item["group_date"].strftime(short_label_format),
                "tooltip_label": item["group_date"].strftime("%b %d, %Y"),
                "value": item["value"],
            }
            for item in queryset.order_by("group_date")
        ]

        return Response(data)
    
    @action(detail=False, methods=["get"])
    def stats_cards(self, request):
        queryset = self.get_queryset()

        workout_days = list(
            queryset
            .values_list("date__date", flat=True)
            .distinct()
            .order_by("date__date")
        )

        total_workouts = len(workout_days)
        today = timezone.localdate()
        month_start = today.replace(day=1)
        if month_start.month == 12:
            next_month_start = month_start.replace(
                year=month_start.year + 1,
                month=1,
            )
        else:
            next_month_start = month_start.replace(month=month_start.month + 1)
        month_workouts = sum(
            1 for day in workout_days if month_start <= day < next_month_start
        )

        streak, max_streak = calculate_workout_streaks(workout_days, today)

        data = {
            "total_workouts": total_workouts,
            "month_workouts": month_workouts,
            "streak": streak,
            "max_streak": max_streak,
        }

        return Response(data)

def send_verification_email(user, verification_url):
    app_name = settings.APP_NAME

    subject = f"Confirm your {app_name} email"

    text_body = (
        f"Hi {user.username},\n\n"
        f"Welcome to {app_name}. Please confirm this email address so you can sign in:\n\n"
        f"{verification_url}\n\n"
        "If you did not create this account, you can safely ignore this email.\n\n"
        f"Thanks,\nThe {app_name} team"
    )

    html_body = f"""
<!doctype html>
<html lang="en">
  <body style="margin:0;padding:0;background:#f6f7f9;font-family:Arial,sans-serif;color:#18181b;">
    <div style="max-width:560px;margin:0 auto;padding:32px 20px;">
      <div style="background:#ffffff;border:1px solid #e4e4e7;border-radius:8px;padding:28px;">
        <h1 style="margin:0 0 16px;font-size:22px;line-height:1.3;color:#18181b;">
          Confirm your email
        </h1>

        <p style="margin:0 0 16px;font-size:15px;line-height:1.6;">
          Hi {user.username},
        </p>

        <p style="margin:0 0 24px;font-size:15px;line-height:1.6;">
          Welcome to {app_name}. Please confirm this email address so you can sign in.
        </p>

        <p style="margin:0 0 24px;">
          <a href="{verification_url}" style="display:inline-block;background:#18181b;color:#ffffff;text-decoration:none;border-radius:6px;padding:12px 18px;font-size:15px;font-weight:600;">
            Confirm email
          </a>
        </p>

        <p style="margin:0 0 12px;font-size:13px;line-height:1.6;color:#52525b;">
          If the button does not work, paste this link into your browser:
        </p>

        <p style="margin:0 0 24px;font-size:13px;line-height:1.6;word-break:break-all;color:#52525b;">
          {verification_url}
        </p>

        <p style="margin:0;font-size:13px;line-height:1.6;color:#71717a;">
          If you did not create this account, you can safely ignore this email.
        </p>
      </div>
    </div>
  </body>
</html>
"""

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
        reply_to=[settings.SUPPORT_EMAIL],
        headers={
            "Auto-Submitted": "auto-generated",
            "X-Auto-Response-Suppress": "All",
        },
    )

    email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=False)

def send_password_reset_email(user, reset_url):
    app_name = settings.APP_NAME
    subject = f"Reset your {app_name} password"

    text_body = (
        f"Hi {user.username},\n\n"
        f"Use this link to reset your password:\n\n"
        f"{reset_url}\n\n"
        "If you did not request this, you can safely ignore this email.\n\n"
        f"Thanks,\nThe {app_name} team"
    )

    html_body = f"""
<!doctype html>
<html lang="en">
  <body style="margin:0;padding:0;background:#f6f7f9;font-family:Arial,sans-serif;color:#18181b;">
    <div style="max-width:560px;margin:0 auto;padding:32px 20px;">
      <div style="background:#ffffff;border:1px solid #e4e4e7;border-radius:8px;padding:28px;">
        <h1 style="margin:0 0 16px;font-size:22px;">Reset your password</h1>
        <p style="margin:0 0 16px;font-size:15px;line-height:1.6;">Hi {user.username},</p>
        <p style="margin:0 0 24px;font-size:15px;line-height:1.6;">
          Click the button below to create a new password.
        </p>
        <p style="margin:0 0 24px;">
          <a href="{reset_url}" style="display:inline-block;background:#18181b;color:#ffffff;text-decoration:none;border-radius:6px;padding:12px 18px;font-size:15px;font-weight:600;">
            Reset password
          </a>
        </p>
        <p style="margin:0 0 12px;font-size:13px;color:#52525b;">
          If the button does not work, paste this link into your browser:
        </p>
        <p style="margin:0 0 24px;font-size:13px;word-break:break-all;color:#52525b;">
          {reset_url}
        </p>
        <p style="margin:0;font-size:13px;color:#71717a;">
          If you did not request this, you can safely ignore this email.
        </p>
      </div>
    </div>
  </body>
</html>
"""

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
        reply_to=[settings.SUPPORT_EMAIL],
        headers={
            "Auto-Submitted": "auto-generated",
            "X-Auto-Response-Suppress": "All",
        },
    )

    email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=False)

class PasswordResetRequestView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = password_reset_token.make_token(user)

            frontend_url = settings.FRONTEND_URL.rstrip("/")
            reset_url = f"{frontend_url}/reset-password/{uid}/{token}"

            send_password_reset_email(user, reset_url)

        return Response(
            {"detail": "If an account exists for that email, a reset link has been sent."},
            status=status.HTTP_200_OK,
        )

class PasswordResetConfirmView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Password reset successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access = response.data["access"]
            refresh = response.data["refresh"]

            res = Response(
                {"success": True},
                status=status.HTTP_200_OK
            )

            res.set_cookie(
                key="access_token",
                value=access,
                httponly=True,
                secure=True,  # True in production
                samesite="Lax",
                max_age=60 * 30,  # 30 minutes
            )

            res.set_cookie(
                key="refresh_token",
                value=refresh,
                httponly=True,
                secure=True,  # True in production
                samesite="Lax",
                max_age=60 * 60 * 24 * 7,  # 7 days
            )

            return res

        return response
    
class LogoutView(APIView):

    def post(self, request):
        response = Response(
            {"success": True},
            status=status.HTTP_200_OK
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response
    
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "is_verified": request.user.is_verified,
            "date_joined": request.user.date_joined,
        })

class RefreshView(APIView):

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(refresh_token)

            response = Response(
                {"detail": "Token refreshed successfully."},
                status=status.HTTP_200_OK,
            )

            response.set_cookie(
                key="access_token",
                value=str(refresh.access_token),
                httponly=True,
                secure=True,
                samesite="Lax",
                max_age=60 * 30,  # 30 minutes
            )

            return response

        except Exception:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            uid = urlsafe_base64_encode(
                force_bytes(user.pk)
            )

            token = email_verification_token.make_token(user)

            frontend_url = settings.FRONTEND_URL.rstrip("/")

            verification_url = (
                f"{frontend_url}/verify-email/"
                f"{uid}/{token}"
            )

            send_verification_email(user, verification_url)

            return Response(
                {
                    "detail": "Account created. Check your email."
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
    
class VerifyEmailView(APIView):
    permission_classes = []

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)

        except Exception:
            return Response(
                {"detail": "Invalid link"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if email_verification_token.check_token(user, token):
            user.is_verified = True
            user.save()

            return Response(
                {"detail": "Email verified"},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "Invalid token"},
            status=status.HTTP_400_BAD_REQUEST,
        )

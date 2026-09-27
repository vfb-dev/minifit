import { apiFetch } from "./wrapper";

import { apiUrl } from "@/lib/api";

export async function get_chart_data(params: {
  workout_type: "strength" | "cardio";
  exercise: string;
  metric: string;
  period: string;
}) {
  const searchParams = new URLSearchParams({
    workout_type: params.workout_type,
    exercise: params.exercise,
    metric: params.metric,
    period: params.period,
  });

  const response = await apiFetch(
    apiUrl(`/api/v1/exercise-sets/chart/?${searchParams}`),
  );

  return response.json();
}

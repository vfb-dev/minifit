import { apiFetch } from "./wrapper";

import { apiUrl } from "@/lib/api";

export type ExerciseSet = {
  id: number;
  exercise: number | null;
  name: string;
  workout_type: "strength" | "cardio";
  cardio_activity: string;
  date: string;
  formatted_date: string;
  reps: number | null;
  weight: number | string | null;
  duration_minutes: number | null;
  distance_km: number | string | null;
  calories_burned: number | null;
};

export type ExerciseSetGroup = {
  group_id: string;
  exercise: number | null;
  name: string;
  workout_type: "strength" | "cardio";
  date: string;
  sets: number;
  exercises: ExerciseSet[];
};

export type ExerciseSetsResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: ExerciseSet[];
};

export type ExerciseSetHistoryResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: ExerciseSetGroup[];
};

export type ExerciseSetPayload = {
  workout_type: "strength" | "cardio";
  exercise?: number | null;
  date: string;
  reps?: number | null;
  weight?: number | null;
  cardio_activity?: string;
  duration_minutes?: number | null;
  distance_km?: number | null;
  calories_burned?: number | null;
};

export async function getExerciseSets(page = 1) {
  const response = await apiFetch(apiUrl(`/api/v1/exercise-sets/?page=${page}`));

  if (!response.ok) {
    throw new Error("Failed to fetch exercise sets");
  }

  return response.json();
}

type HistoryParams = { page?: number; search?: string };
export async function getExerciseSetHistory({
  page = 1,
  search,
}: HistoryParams = {}) {
  const params = new URLSearchParams({ page: String(page) });

  if (search) {
    params.set("search", search);
  }

  const response = await apiFetch(
    apiUrl(`/api/v1/exercise-sets/history/?${params}`),
  );

  if (!response.ok) {
    throw new Error("Failed to fetch exercise set history");
  }

  return response.json();
}

export async function createExerciseSet(exerciseData: ExerciseSetPayload) {
  const response = await apiFetch(apiUrl("/api/v1/exercise-sets/"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(exerciseData),
  });

  if (!response.ok) {
    throw new Error("Failed to create exercise set");
  }

  return response.json();
}

export async function updateExerciseSet(
  id: number,
  exerciseData: ExerciseSetPayload,
) {
  const response = await apiFetch(apiUrl(`/api/v1/exercise-sets/${id}/`), {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(exerciseData),
  });

  if (!response.ok) {
    throw new Error("Failed to update exercise set");
  }

  return response.json();
}

export async function deleteExerciseSet(id: number) {
  const response = await apiFetch(apiUrl(`/api/v1/exercise-sets/${id}/`), {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error("Failed to delete exercise set");
  }
}

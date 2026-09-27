import { apiFetch } from "./wrapper";

import { apiUrl } from "@/lib/api";

export type Exercise = {
  id: number;
  name: string;
  primary_body_part: string;
  secondary_body_parts: string[];
  set_count?: number;
  cardio_count?: number;
  strength_count?: number;
  last_logged_at?: string | null;
  created_at?: string;
  updated_at?: string;
};

export type ExercisesResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: Exercise[];
};

export type ExercisePayload = {
  name: string;
  primary_body_part: string;
  secondary_body_parts: string[];
};

type GetExercisesParams = {
  page?: number;
  pageSize?: number;
  search?: string;
};

export async function getExercises({
  page = 1,
  pageSize,
  search,
}: GetExercisesParams = {}) {
  const params = new URLSearchParams({ page: String(page) });

  if (pageSize) {
    params.set("page_size", String(pageSize));
  }

  if (search?.trim()) {
    params.set("search", search.trim());
  }

  const response = await apiFetch(apiUrl(`/api/v1/exercises/?${params}`));

  if (!response.ok) {
    throw new Error("Failed to fetch exercises");
  }

  return response.json();
}

export async function getExerciseOptions() {
  const response = await apiFetch(apiUrl("/api/v1/exercises/options/"));

  if (!response.ok) {
    throw new Error("Failed to fetch exercise options");
  }

  return response.json();
}

export async function createExercise(exerciseData: ExercisePayload) {
  const response = await apiFetch(apiUrl("/api/v1/exercises/"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(exerciseData),
  });

  if (!response.ok) {
    throw new Error("Failed to create exercise");
  }

  return response.json();
}

export async function updateExercise(
  id: number,
  exerciseData: ExercisePayload,
) {
  const response = await apiFetch(apiUrl(`/api/v1/exercises/${id}/`), {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(exerciseData),
  });

  if (!response.ok) {
    throw new Error("Failed to update exercise");
  }

  return response.json();
}

export async function deleteExercise(id: number) {
  const response = await apiFetch(apiUrl(`/api/v1/exercises/${id}/`), {
    method: "DELETE",
  });

  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new Error(data?.detail ?? "Failed to delete exercise");
  }
}

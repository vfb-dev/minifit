import type { Exercise } from "@/services/exercises";

export type WorkoutType = "strength" | "cardio";

export function getWorkoutExercises(
  exercises: Exercise[],
  workoutType: WorkoutType,
) {
  return exercises.filter((exercise) =>
    workoutType === "cardio"
      ? exercise.primary_body_part === "cardio" || (exercise.cardio_count ?? 0) > 0
      : exercise.primary_body_part !== "cardio" || (exercise.strength_count ?? 0) > 0,
  );
}

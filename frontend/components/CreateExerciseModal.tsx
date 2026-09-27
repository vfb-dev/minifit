"use client";

import Link from "next/link";
import {
  CalendarClock,
  Dumbbell,
  Hash,
  Loader2,
  PlusCircle,
  Scale,
  Timer,
  Route,
  X,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { useModalStore } from "@/store/modalStore";

import { Controller, useForm, useWatch } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { createExerciseSet } from "@/services/exerciseSets";
import { getExerciseOptions, type Exercise } from "@/services/exercises";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { format } from "date-fns";
import { useEffect, useMemo } from "react";
import { translations } from "@/lib/translations";
import { useLanguageStore } from "@/store/languageStore";
import { getWorkoutExercises } from "@/lib/workoutExercises";

type Translation = (typeof translations)[keyof typeof translations];

function createExerciseSetSchema(t: Translation) {
  return z.object({
    workout_type: z.enum(["strength", "cardio"]),
    date: z.string().min(1, t.common.required),
    exercise: z.string(),
    reps: z.number().optional(),
    weight: z.number().optional(),
    duration_minutes: z.number().optional(),
    distance_km: z.number().optional(),
    calories_burned: z.number().optional(),
  }).superRefine((value, context) => {
    const m = t.dashboard.exerciseModal;
    if (value.workout_type === "cardio") {
      if (!value.exercise) context.addIssue({ code: "custom", path: ["exercise"], message: m.selectExercise });
      if (!value.duration_minutes || value.duration_minutes < 1) context.addIssue({ code: "custom", path: ["duration_minutes"], message: m.durationRequired });
      if (value.distance_km !== undefined && value.distance_km < 0) context.addIssue({ code: "custom", path: ["distance_km"], message: m.distanceInvalid });
      if (value.calories_burned !== undefined && value.calories_burned < 0) context.addIssue({ code: "custom", path: ["calories_burned"], message: m.caloriesInvalid });
    } else {
      if (!value.exercise) context.addIssue({ code: "custom", path: ["exercise"], message: m.selectExercise });
      if (!value.reps || value.reps < 1) context.addIssue({ code: "custom", path: ["reps"], message: m.minimumOneRep });
      if (value.weight === undefined || value.weight < 0) context.addIssue({ code: "custom", path: ["weight"], message: m.mustBePositive });
      if (value.weight !== undefined && value.weight > 9999) context.addIssue({ code: "custom", path: ["weight"], message: m.maxWeight });
    }
  });
}

type FormData = z.infer<ReturnType<typeof createExerciseSetSchema>>;

function toTitleCase(text: string) {
  return text.replace(/\w\S*/g, (word) => {
    return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
  });
}

export function CreateExerciseModal() {
  const { createModal, handleCreateModal } = useModalStore();
  const queryClient = useQueryClient();
  const { language } = useLanguageStore();
  const t = translations[language];
  const schema = useMemo(() => createExerciseSetSchema(t), [t]);

  const { data: exerciseOptions = [] } = useQuery<Exercise[]>({
    queryKey: ["exercise_options"],
    queryFn: () => getExerciseOptions(),
    enabled: createModal,
  });

  const {
    control,
    register,
    handleSubmit,
    reset,
    setValue,
    getValues,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      workout_type: "strength",
      date: "",
      exercise: "",
      reps: 1,
      weight: 0,
    },
  });
  const workoutType = useWatch({ control, name: "workout_type" });
  const availableExercises = useMemo(
    () => getWorkoutExercises(exerciseOptions, workoutType),
    [exerciseOptions, workoutType],
  );

  useEffect(() => {
    if (!createModal) return;

    setValue("date", format(new Date(), "yyyy-MM-dd'T'HH:mm"));

  }, [createModal, setValue]);

  useEffect(() => {
    if (!createModal) return;
    const selected = getValues("exercise");
    if (!availableExercises.some((exercise) => String(exercise.id) === selected)) {
      const nextId = String(availableExercises[0]?.id ?? "");
      if (selected !== nextId) setValue("exercise", nextId);
    }
  }, [createModal, availableExercises, getValues, setValue]);

  const createMutation = useMutation({
    mutationFn: createExerciseSet,

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["exercise_sets"],
      });

      await queryClient.invalidateQueries({
        queryKey: ["history"],
      });

      await queryClient.invalidateQueries({
        queryKey: ["exercises"],
      });
      await queryClient.invalidateQueries({ queryKey: ["exercise_options"] });

      await queryClient.invalidateQueries({
        queryKey: ["chart"],
      });

      await queryClient.invalidateQueries({
        queryKey: ["stats_cards"],
      });

      reset();
      handleCreateModal(false);
    },
  });

  function onSubmit(formData: FormData) {
    createMutation.mutate(formData.workout_type === "cardio" ? {
      workout_type: "cardio",
      exercise: Number(formData.exercise),
      date: formData.date,
      duration_minutes: formData.duration_minutes,
      distance_km: formData.distance_km ?? null,
      calories_burned: formData.calories_burned ?? null,
    } : {
      workout_type: "strength",
      exercise: Number(formData.exercise),
      date: formData.date,
      reps: formData.reps,
      weight: formData.weight,
    });
  }

  if (!createModal) return null;

  const hasExercises = availableExercises.length > 0;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-zinc-950/60 p-0 backdrop-blur-md sm:items-center sm:p-6"
      role="presentation"
      onMouseDown={() => handleCreateModal(false)}
    >
      <Card
        role="dialog"
        aria-modal="true"
        aria-labelledby="create-exercise-title"
        className="max-h-[90vh] w-full max-w-md overflow-y-auto rounded-t-3xl rounded-b-none border-zinc-200 bg-white shadow-2xl ring-1 ring-black/5 sm:rounded-2xl"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <CardHeader className="border-b border-zinc-100 px-6 py-5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <CardTitle
                id="create-exercise-title"
                className="text-xl font-semibold tracking-normal text-zinc-950"
              >
                {t.dashboard.exerciseModal.createTitle}
              </CardTitle>
              <p className="mt-1 text-sm leading-5 text-zinc-500">
                {t.dashboard.exerciseModal.createDescription}
              </p>
            </div>

            <button
              type="button"
              aria-label={t.dashboard.exerciseModal.closeModal}
              onClick={() => handleCreateModal(false)}
              className="grid size-10 shrink-0 cursor-pointer place-items-center rounded-full bg-white/80 text-zinc-500 shadow-sm ring-1 ring-zinc-200 transition hover:bg-white hover:text-zinc-950 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
            >
              <X className="size-4" />
            </button>
          </div>
        </CardHeader>

        <CardContent className="px-6 py-6">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="grid gap-4">
                <div className="grid gap-2">
                  <Label>{t.dashboard.exerciseModal.workoutType}</Label>
                  <div className="grid grid-cols-2 gap-2">
                    {(["strength", "cardio"] as const).map((type) => (
                      <Button key={type} type="button" variant={workoutType === type ? "default" : "outline"}
                        className="h-11 cursor-pointer rounded-xl" onClick={() => setValue("workout_type", type)}>
                        {t.dashboard.exerciseModal[type]}
                      </Button>
                    ))}
                  </div>
                </div>
                <div className="grid gap-2">
                  <Label
                    htmlFor="date"
                    className="text-sm font-semibold text-zinc-800"
                  >
                    {t.common.date}
                  </Label>
                  <div className="relative">
                    <CalendarClock className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-zinc-400" />
                    <Input
                      id="date"
                      type="datetime-local"
                      className="h-11 rounded-xl pl-10"
                      {...register("date")}
                    />
                  </div>
                  {errors.date && (
                    <p className="text-sm font-medium text-red-500">
                      {errors.date.message}
                    </p>
                  )}
                </div>

                {hasExercises ? <div className="grid gap-2">
                  <Label
                    htmlFor="exercise"
                    className="text-sm font-semibold text-zinc-800"
                  >
                    {t.common.exercise}
                  </Label>
                  <Controller
                    control={control}
                    name="exercise"
                    render={({ field }) => (
                      <Select
                        value={field.value}
                        onValueChange={field.onChange}
                      >
                        <SelectTrigger
                          id="exercise"
                          className="h-11 w-full cursor-pointer rounded-xl"
                        >
                          <SelectValue
                            placeholder={
                              t.dashboard.exerciseModal.selectExercise
                            }
                          />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectGroup>
                            {availableExercises.map((exercise) => (
                              <SelectItem
                                key={exercise.id}
                                value={String(exercise.id)}
                              >
                                {toTitleCase(exercise.name)}
                              </SelectItem>
                            ))}
                          </SelectGroup>
                        </SelectContent>
                      </Select>
                    )}
                  />
                  {errors.exercise && (
                    <p className="text-sm font-medium text-red-500">
                      {errors.exercise.message}
                    </p>
                  )}
                </div> : <div className="rounded-2xl border border-dashed bg-zinc-50 p-5 text-center">
                  <Dumbbell className="mx-auto mb-3 size-5 text-zinc-500" />
                  <h3 className="text-sm font-semibold">{workoutType === "cardio" ? t.dashboard.exerciseModal.noCardioExercisesTitle : t.dashboard.exerciseModal.noExercisesTitle}</h3>
                  <p className="mt-2 text-sm text-zinc-500">{workoutType === "cardio" ? t.dashboard.exerciseModal.noCardioExercisesDescription : t.dashboard.exerciseModal.noExercisesDescription}</p>
                  <Button asChild className="mt-4"><Link href="/exercises" onClick={() => handleCreateModal(false)}><PlusCircle className="size-4" />{t.dashboard.exerciseModal.manageExercises}</Link></Button>
                </div>}

                {workoutType === "strength" && hasExercises && <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div className="grid gap-2">
                    <Label
                      htmlFor="reps"
                      className="text-sm font-semibold text-zinc-800"
                    >
                      {t.common.reps}
                    </Label>
                    <div className="relative">
                      <Hash className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-zinc-400" />
                      <Input
                        id="reps"
                        type="number"
                        placeholder="12"
                        className="h-11 rounded-xl pl-10"
                        {...register("reps", { setValueAs: (value) => value === "" ? undefined : Number(value) })}
                      />
                    </div>
                    {errors.reps && (
                      <p className="text-sm font-medium text-red-500">
                        {errors.reps.message}
                      </p>
                    )}
                  </div>

                  <div className="grid gap-2">
                    <Label
                      htmlFor="weight"
                      className="text-sm font-semibold text-zinc-800"
                    >
                      {t.common.weight}
                    </Label>
                    <div className="relative">
                      <Scale className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-zinc-400" />
                      <Input
                        id="weight"
                        type="number"
                        placeholder="20.5"
                        step="0.01"
                        max={9999}
                        className="h-11 rounded-xl pl-10"
                        {...register("weight", { setValueAs: (value) => value === "" ? undefined : Number(value) })}
                      />
                    </div>
                    {errors.weight && (
                      <p className="text-sm font-medium text-red-500">
                        {errors.weight.message}
                      </p>
                    )}
                  </div>
                </div>}
                {workoutType === "cardio" && <>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div className="grid gap-2">
                      <Label htmlFor="duration_minutes">{t.dashboard.exerciseModal.duration}</Label>
                      <div className="relative"><Timer className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-zinc-400" /><Input id="duration_minutes" type="number" min="1" className="h-11 rounded-xl pl-10" {...register("duration_minutes", { setValueAs: (value) => value === "" ? undefined : Number(value) })} /></div>
                      {errors.duration_minutes && <p className="text-sm font-medium text-red-500">{errors.duration_minutes.message}</p>}
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="distance_km">{t.dashboard.exerciseModal.distance}</Label>
                      <div className="relative"><Route className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-zinc-400" /><Input id="distance_km" type="number" min="0" step="0.01" className="h-11 rounded-xl pl-10" {...register("distance_km", { setValueAs: (value) => value === "" ? undefined : Number(value) })} /></div>
                      {errors.distance_km && <p className="text-sm font-medium text-red-500">{errors.distance_km.message}</p>}
                    </div>
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="calories_burned">{t.dashboard.exerciseModal.calories}</Label>
                    <Input id="calories_burned" type="number" min="0" className="h-11 rounded-xl" {...register("calories_burned", { setValueAs: (value) => value === "" ? undefined : Number(value) })} />
                    {errors.calories_burned && <p className="text-sm font-medium text-red-500">{errors.calories_burned.message}</p>}
                  </div>
                </>}
              </div>
              {createMutation.isError && <p role="alert" className="text-sm text-red-600">{t.dashboard.exerciseModal.saveError}</p>}

              <div className="flex flex-col-reverse gap-3 border-t border-zinc-100 pt-5 sm:flex-row sm:justify-end">
                <Button
                  type="button"
                  variant="outline"
                  className="h-11 cursor-pointer rounded-xl px-5"
                  onClick={() => handleCreateModal(false)}
                >
                  {t.common.cancel}
                </Button>

                <Button
                  type="submit"
                  disabled={createMutation.isPending || !hasExercises}
                  className="h-11 cursor-pointer rounded-xl bg-zinc-950 px-6 font-semibold text-white shadow-lg shadow-zinc-950/15 hover:bg-zinc-800"
                >
                  {createMutation.isPending && (
                    <Loader2 className="mr-2 size-4 animate-spin" />
                  )}
                  {t.dashboard.exerciseModal.addExercise}
                </Button>
              </div>
            </form>
        </CardContent>
      </Card>
    </div>
  );
}

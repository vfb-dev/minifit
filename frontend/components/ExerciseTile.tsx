"use client";

import { Dumbbell, ChevronDown, MoreHorizontal } from "lucide-react";

import { useState } from "react";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { Button } from "@/components/ui/button";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  deleteExerciseSet,
  type ExerciseSet,
  type ExerciseSetGroup,
} from "@/services/exerciseSets";
import { translations } from "@/lib/translations";
import { useLanguageStore } from "@/store/languageStore";
import { useModalStore } from "@/store/modalStore";

type ExerciseTileProps = {
  exercise: ExerciseSetGroup;
  handleSelectedExercise: (ex: ExerciseSet) => void;
};

function toTitleCase(text: string) {
  return text.replace(/\w\S*/g, (word) => {
    return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
  });
}

export function ExerciseTile({
  exercise,
  handleSelectedExercise,
}: ExerciseTileProps) {
  const { handleEditModal } = useModalStore();
  const [isOpen, setisOpen] = useState<boolean>(false);

  const { language } = useLanguageStore();
  const t = translations[language].dashboard.history;

  const queryClient = useQueryClient();

  const deleteMutation = useMutation({
    mutationFn: deleteExerciseSet,

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["history"],
      });

      await queryClient.invalidateQueries({
        queryKey: ["exercise_sets"],
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
    },
  });

  return (
    <div className="w-full bg-white rounded-lg shadow-sm p-2">
      <div className="flex h-full items-center gap-3">
        <div className="rounded-lg bg-zinc-100 p-3">
          {exercise.workout_type === "cardio" ? (
            <span role="img" aria-label={t.cardio} className="grid size-6 place-items-center text-xl leading-none">❤️</span>
          ) : (
            <Dumbbell className="size-6" />
          )}
        </div>

        <div>
          <p>{toTitleCase(exercise.name)}</p>
          <p className="text-sm text-zinc-400">{exercise.date}</p>
        </div>

        <div className="ml-auto text-sm font-semibold text-zinc-600">{exercise.workout_type === "cardio" ? t.cardio : `${exercise.sets} ${t.sets}`}</div>

        <button
          onClick={() => setisOpen((prev) => !prev)}
          className="cursor-pointer bg-white text-zinc-500 rounded-full border p-1 shadow-sm transition-all duration-300 hover:scale-110 hover:bg-zinc-100 hover:text-black"
        >
          <ChevronDown
            className={`size-4 transition-transform duration-500 ${isOpen ? "rotate-180" : "rotate-0"}`}
          ></ChevronDown>
        </button>
      </div>

      <div
        className={`
        overflow-hidden
        transition-all
        duration-500
        ease-in-out
        ${isOpen ? "max-h-125 opacity-100 mt-2" : "max-h-0 opacity-0"}
      `}
      >
        <Table className="mt-2">
          <TableHeader>
            <TableRow>
              <TableHead className="text-zinc-500">{t.sets}</TableHead>

              <TableHead className="text-zinc-500">{exercise.workout_type === "cardio" ? t.durationCalories : t.reps}</TableHead>

              <TableHead className="text-zinc-500">{exercise.workout_type === "cardio" ? t.distance : t.weight}</TableHead>

              <TableHead className="text-zinc-500">{t.actions}</TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            {exercise.exercises.map((ex, index) => {
              return (
                <TableRow key={ex.id}>
                  <TableCell>{index + 1}</TableCell>
                  <TableCell>{ex.workout_type === "cardio" ? <>{ex.duration_minutes} {t.minutesShort}{ex.calories_burned !== null && <span className="block text-xs text-zinc-500">{ex.calories_burned} kcal</span>}</> : ex.reps}</TableCell>
                  <TableCell>{ex.workout_type === "cardio" ? (ex.distance_km === null ? "—" : `${ex.distance_km} ${t.kmShort}`) : ex.weight}</TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="size-8 cursor-pointer"
                        >
                          <MoreHorizontal />
                        </Button>
                      </DropdownMenuTrigger>

                      <DropdownMenuContent align="center">
                        <DropdownMenuItem
                          className="cursor-pointer"
                          onClick={() => {
                            handleSelectedExercise(ex);
                            handleEditModal(true);
                          }}
                        >
                          {t.edit}
                        </DropdownMenuItem>

                        <DropdownMenuSeparator />

                        <DropdownMenuItem
                          className="cursor-pointer"
                          variant="destructive"
                          onClick={() => deleteMutation.mutate(ex.id)}
                        >
                          {t.delete}
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

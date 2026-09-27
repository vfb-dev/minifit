"use client";

import { useState } from "react";
import { MoreHorizontal, NotebookPen } from "lucide-react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { CreateExerciseModal } from "@/components/CreateExerciseModal";
import { EditExerciseModal } from "@/components/EditExerciseModal";
import { SimplePagination } from "@/components/SimplePagination";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { Button } from "@/components/ui/button";
import { useModalStore } from "@/store/modalStore";
import {
  deleteExerciseSet,
  getExerciseSets,
  type ExerciseSet,
  type ExerciseSetsResponse,
} from "@/services/exerciseSets";
import { translations } from "@/lib/translations";
import { useLanguageStore } from "@/store/languageStore";

const PAGE_SIZE = 10;

function toTitleCase(text: string) {
  return text.replace(/\w\S*/g, (word) => {
    return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
  });
}

export function HistoryTable() {
  const queryClient = useQueryClient();
  const { handleCreateModal, handleEditModal } = useModalStore();
  const { language } = useLanguageStore();
  const t = translations[language].dashboard.history;

  const [currentPage, setCurrentPage] = useState(1);
  const [selectedExercise, setSelectedExercise] = useState<ExerciseSet | null>(
    null,
  );

  const { data, isLoading } = useQuery<ExerciseSetsResponse>({
    queryKey: ["exercise_sets", currentPage],
    queryFn: () => getExerciseSets(currentPage),
    placeholderData: (previousData) => previousData,
  });

  const exercises = data?.results ?? [];

  const paginationInfo = {
    count: data?.count ?? 0,
    next: data?.next ?? null,
    previous: data?.previous ?? null,
  };

  const totalPages = Math.max(Math.ceil(paginationInfo.count / PAGE_SIZE), 1);

  const deleteMutation = useMutation({
    mutationFn: deleteExerciseSet,

    onSuccess: async () => {
      const isLastItemOnPage = exercises.length === 1;

      if (isLastItemOnPage && currentPage > 1) {
        setCurrentPage((prev) => prev - 1);
      }

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
    },
  });

  if (isLoading) {
    return <div>{t.loading}</div>;
  }

  return (
    <>
      <CreateExerciseModal />
      <EditExerciseModal selectedExercise={selectedExercise} />

      <div className="mb-4 flex justify-between">
        <h3 className="text-lg font-semibold">{t.title}</h3>

        <Button
          className="cursor-pointer gap-2"
          onClick={() => handleCreateModal(true)}
        >
          <NotebookPen className="size-4" />
          {t.newEntry}
        </Button>
      </div>

      <Table className="mb-4">
        <TableHeader>
          <TableRow>
            <TableHead className="font-bold">{t.date}</TableHead>

            <TableHead className="font-bold">{t.exercise}</TableHead>

            <TableHead className="font-bold">{t.details}</TableHead>

            <TableHead className="font-bold text-right">{t.actions}</TableHead>
          </TableRow>
        </TableHeader>

        <TableBody>
          {exercises.length ? (
            exercises.map((exercise) => (
              <TableRow key={exercise.id}>
                <TableCell>{exercise.formatted_date}</TableCell>

                <TableCell>
                  <span className="block">{toTitleCase(exercise.name)}</span>
                  <span className="text-xs text-zinc-500">{t[exercise.workout_type]}</span>
                </TableCell>

                <TableCell>{exercise.workout_type === "cardio"
                  ? `${exercise.duration_minutes} ${t.minutesShort}${exercise.distance_km !== null ? ` · ${exercise.distance_km} ${t.kmShort}` : ""}${exercise.calories_burned !== null ? ` · ${exercise.calories_burned} kcal` : ""}`
                  : `${exercise.reps} ${t.reps} · ${exercise.weight} kg`}</TableCell>

                <TableCell className="text-right">
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

                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        className="cursor-pointer"
                        onClick={() => {
                          setSelectedExercise(exercise);
                          handleEditModal(true);
                        }}
                      >
                        {t.edit}
                      </DropdownMenuItem>

                      <DropdownMenuSeparator />

                      <DropdownMenuItem
                        className="cursor-pointer"
                        variant="destructive"
                        onClick={() => deleteMutation.mutate(exercise.id)}
                      >
                        {t.delete}
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell
                colSpan={4}
                className="h-24 text-center text-muted-foreground"
              >
                {t.empty}
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      <SimplePagination
        currentPage={currentPage}
        totalPages={totalPages}
        previousLabel={t.previous}
        nextLabel={t.next}
        onPageChange={setCurrentPage}
      />
    </>
  );
}

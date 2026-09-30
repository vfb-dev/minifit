"use client";

import Link from "next/link";
import { useState } from "react";
import { ArrowLeft, NotebookPen, Search, X } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { ExerciseGrid } from "@/components/exercises/ExerciseGrid";
import { ExerciseModal } from "@/components/exercises/ExerciseModal";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { SimplePagination } from "@/components/SimplePagination";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { translations } from "@/lib/translations";
import {
  createExercise,
  deleteExercise,
  getExercises,
  updateExercise,
  type Exercise,
  type ExercisePayload,
  type ExercisesResponse,
} from "@/services/exercises";
import { useLanguageStore } from "@/store/languageStore";

const PAGE_SIZE = 9;

export default function ExercisesPage() {
  const queryClient = useQueryClient();
  const { language } = useLanguageStore();
  const t = translations[language].exercisePage;

  const [currentPage, setCurrentPage] = useState(1);
  const [search, setSearch] = useState("");
  const [exerciseModalOpen, setExerciseModalOpen] = useState(false);
  const [editingExercise, setEditingExercise] = useState<Exercise | null>(null);
  const [formError, setFormError] = useState("");

  const normalizedSearch = search.trim();
  const hasSearch = normalizedSearch.length > 0;

  const { data, isLoading } = useQuery<ExercisesResponse>({
    queryKey: ["exercises", currentPage, normalizedSearch],
    queryFn: () =>
      getExercises({
        page: currentPage,
        pageSize: PAGE_SIZE,
        search: normalizedSearch,
      }),
    placeholderData: (previousData) => previousData,
  });

  const exercises = data?.results ?? [];
  const totalCount = data?.count ?? 0;
  const totalPages = Math.max(Math.ceil(totalCount / PAGE_SIZE), 1);
  const firstResult = totalCount ? (currentPage - 1) * PAGE_SIZE + 1 : 0;
  const lastResult = Math.min(currentPage * PAGE_SIZE, totalCount);

  async function invalidateExerciseQueries() {
    await queryClient.invalidateQueries({ queryKey: ["exercises"] });
    await queryClient.invalidateQueries({ queryKey: ["exercise_options"] });
    await queryClient.invalidateQueries({ queryKey: ["exercise_sets"] });
    await queryClient.invalidateQueries({ queryKey: ["history"] });
    await queryClient.invalidateQueries({ queryKey: ["chart"] });
  }

  const createMutation = useMutation({
    mutationFn: createExercise,
    onSuccess: async () => {
      await invalidateExerciseQueries();
      handleCloseModal();
    },
    onError: (error) => {
      setFormError(error instanceof Error ? error.message : t.saveError);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({
      id,
      exerciseData,
    }: {
      id: number;
      exerciseData: ExercisePayload;
    }) => updateExercise(id, exerciseData),
    onSuccess: async () => {
      await invalidateExerciseQueries();
      handleCloseModal();
    },
    onError: (error) => {
      setFormError(error instanceof Error ? error.message : t.saveError);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteExercise,
    onSuccess: async () => {
      setFormError("");

      const isLastItemOnPage = exercises.length === 1;

      if (isLastItemOnPage && currentPage > 1) {
        setCurrentPage((previousPage) => previousPage - 1);
      }

      await invalidateExerciseQueries();
    },
    onError: (error) => {
      setFormError(error instanceof Error ? error.message : t.deleteError);
    },
  });

  const savePending = createMutation.isPending || updateMutation.isPending;

  function handleCloseModal() {
    setEditingExercise(null);
    setFormError("");
    setExerciseModalOpen(false);
  }

  function handleCreateClick() {
    setEditingExercise(null);
    setFormError("");
    setExerciseModalOpen(true);
  }

  function handleEdit(exercise: Exercise) {
    setEditingExercise(exercise);
    setFormError("");
    setExerciseModalOpen(true);
  }

  function handleSearchChange(value: string) {
    setSearch(value);
    setCurrentPage(1);
  }

  function handlePageChange(page: number) {
    setCurrentPage(Math.min(Math.max(page, 1), totalPages));
  }

  function handleSubmit(exerciseData: ExercisePayload) {
    setFormError("");

    if (editingExercise) {
      updateMutation.mutate({
        id: editingExercise.id,
        exerciseData,
      });
      return;
    }

    createMutation.mutate(exerciseData);
  }

  return (
    <ProtectedRoute>
      <div className="w-full max-w-7xl px-6 pt-8 pb-28 md:py-10">
        {/* HEADER */}
        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <Button asChild variant="ghost" className="mb-3 -ml-2 gap-2">
              <Link href="/">
                <ArrowLeft className="size-4" />
                {t.backToDashboard}
              </Link>
            </Button>

            {/* Title */}
            <h1 className="text-2xl font-bold tracking-normal text-zinc-950 md:text-3xl">
              {t.title}
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-500">
              {t.description}
            </p>
          </div>

          {/* Desktop Button */}
          <Button
            type="button"
            className="hidden h-10 w-full cursor-pointer rounded-xl bg-zinc-950 px-4 font-semibold text-white hover:bg-zinc-800 md:flex md:w-auto"
            onClick={handleCreateClick}
          >
            <NotebookPen className="size-4" />
            {t.createTitle}
          </Button>

          {/* Mobile Button */}
          <Button
            size="icon"
            className="fixed right-6 bottom-6 h-16 w-16 rounded-full shadow-xl md:hidden"
            onClick={handleCreateClick}
          >
            <NotebookPen className="size-6" />
          </Button>
        </div>

        {exerciseModalOpen && (
          <ExerciseModal
            key={editingExercise?.id ?? "create"}
            editingExercise={editingExercise}
            formError={formError}
            savePending={savePending}
            onClose={handleCloseModal}
            onSubmit={handleSubmit}
          />
        )}

        {/* EXERCISE LIBRARY */}
        <section className="rounded-2xl border bg-white p-5 shadow-sm">
          <div className="mb-5 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            {/* Title */}
            <div>
              <h2 className="text-lg font-semibold text-zinc-950">
                {t.libraryTitle}
              </h2>
              <p className="mt-1 text-sm text-zinc-500">
                {t.libraryDescription}
              </p>
            </div>

            {/* Search Input */}
            <div className="relative w-full sm:max-w-xs">
              <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-zinc-400" />
              <Input
                id="exercise-library-search"
                type="text"
                value={search}
                placeholder={t.searchPlaceholder}
                className="h-10 rounded-xl bg-white pr-10 pl-10"
                onChange={(event) => handleSearchChange(event.target.value)}
              />
              {search && (
                <button
                  type="button"
                  aria-label={t.clearSearch}
                  className="absolute top-1/2 right-2 grid size-7 -translate-y-1/2 place-items-center rounded-full text-zinc-400 transition hover:bg-zinc-100 hover:text-zinc-700"
                  onClick={() => handleSearchChange("")}
                >
                  <X className="size-4" />
                </button>
              )}
            </div>
          </div>

          {formError && !exerciseModalOpen && (
            <p className="mb-4 rounded-xl bg-red-50 px-3 py-2 text-sm font-medium text-red-600">
              {formError}
            </p>
          )}

          {/* Exercise Tiles */}
          <ExerciseGrid
            exercises={exercises}
            isLoading={isLoading}
            hasSearch={hasSearch}
            deletePending={deleteMutation.isPending}
            onDelete={(id) => deleteMutation.mutate(id)}
            onEdit={handleEdit}
          />

          {/* Pagination */}
          {totalCount > 0 && (
            <div className="mt-5 flex flex-col gap-3 border-t border-zinc-100 pt-5 sm:flex-row sm:items-center sm:justify-between">
              <p className="w-full text-sm text-zinc-500">
                {t.showing} {firstResult}-{lastResult} {t.of} {totalCount}
              </p>

              <SimplePagination
                currentPage={currentPage}
                totalPages={totalPages}
                previousLabel={t.previous}
                nextLabel={t.next}
                className="justify-end sm:w-auto"
                onPageChange={handlePageChange}
              />
            </div>
          )}
        </section>
      </div>
    </ProtectedRoute>
  );
}

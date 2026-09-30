"use client";

import Link from "next/link";
import { useState } from "react";
import { ArrowLeft, ClipboardList, Search, X } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { ProtectedRoute } from "@/components/ProtectedRoute";
import { RoutineGrid } from "@/components/routines/RoutineGrid";
import { RoutineModal } from "@/components/routines/RoutineModal";
import { SimplePagination } from "@/components/SimplePagination";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { translations } from "@/lib/translations";
import {
  createRoutine,
  deleteRoutine,
  getRoutines,
  updateRoutine,
  type RoutinePayload,
  type RoutinesResponse,
  type WorkoutRoutine,
} from "@/services/routines";
import { useLanguageStore } from "@/store/languageStore";

const PAGE_SIZE = 9;

export default function RoutinesPage() {
  const queryClient = useQueryClient();
  const { language } = useLanguageStore();
  const t = translations[language].routinePage;

  const [currentPage, setCurrentPage] = useState(1);
  const [search, setSearch] = useState("");
  const [routineModalOpen, setRoutineModalOpen] = useState(false);
  const [editingRoutine, setEditingRoutine] = useState<WorkoutRoutine | null>(
    null,
  );
  const [formError, setFormError] = useState("");

  const normalizedSearch = search.trim();
  const hasSearch = normalizedSearch.length > 0;

  const { data, isLoading } = useQuery<RoutinesResponse>({
    queryKey: ["routines", currentPage, normalizedSearch],
    queryFn: () =>
      getRoutines({
        page: currentPage,
        pageSize: PAGE_SIZE,
        search: normalizedSearch,
      }),
    placeholderData: (previousData) => previousData,
  });

  const routines = data?.results ?? [];
  const totalCount = data?.count ?? 0;
  const totalPages = Math.max(Math.ceil(totalCount / PAGE_SIZE), 1);
  const firstResult = totalCount ? (currentPage - 1) * PAGE_SIZE + 1 : 0;
  const lastResult = Math.min(currentPage * PAGE_SIZE, totalCount);

  async function invalidateRoutineQueries() {
    await queryClient.invalidateQueries({ queryKey: ["routines"] });
  }

  const createMutation = useMutation({
    mutationFn: createRoutine,
    onSuccess: async () => {
      await invalidateRoutineQueries();
      handleCloseModal();
    },
    onError: (error) => {
      setFormError(error instanceof Error ? error.message : t.saveError);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({
      id,
      routineData,
    }: {
      id: number;
      routineData: RoutinePayload;
    }) => updateRoutine(id, routineData),
    onSuccess: async () => {
      await invalidateRoutineQueries();
      handleCloseModal();
    },
    onError: (error) => {
      setFormError(error instanceof Error ? error.message : t.saveError);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteRoutine,
    onSuccess: async () => {
      setFormError("");

      const isLastItemOnPage = routines.length === 1;

      if (isLastItemOnPage && currentPage > 1) {
        setCurrentPage((previousPage) => previousPage - 1);
      }

      await invalidateRoutineQueries();
    },
    onError: (error) => {
      setFormError(error instanceof Error ? error.message : t.deleteError);
    },
  });

  const savePending = createMutation.isPending || updateMutation.isPending;

  function handleCloseModal() {
    setEditingRoutine(null);
    setFormError("");
    setRoutineModalOpen(false);
  }

  function handleCreateClick() {
    setEditingRoutine(null);
    setFormError("");
    setRoutineModalOpen(true);
  }

  function handleEdit(routine: WorkoutRoutine) {
    setEditingRoutine(routine);
    setFormError("");
    setRoutineModalOpen(true);
  }

  function handleSearchChange(value: string) {
    setSearch(value);
    setCurrentPage(1);
  }

  function handlePageChange(page: number) {
    setCurrentPage(Math.min(Math.max(page, 1), totalPages));
  }

  function handleSubmit(routineData: RoutinePayload) {
    setFormError("");

    if (editingRoutine) {
      updateMutation.mutate({
        id: editingRoutine.id,
        routineData,
      });
      return;
    }

    createMutation.mutate(routineData);
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
            <ClipboardList className="size-4" />
            {t.createTitle}
          </Button>

          {/* Mobile Button */}
          <Button
            size="icon"
            className="fixed right-6 bottom-6 h-16 w-16 rounded-full shadow-xl md:hidden"
            onClick={handleCreateClick}
          >
            <ClipboardList className="size-6" />
          </Button>
        </div>

        {routineModalOpen && (
          <RoutineModal
            key={editingRoutine?.id ?? "create"}
            editingRoutine={editingRoutine}
            formError={formError}
            savePending={savePending}
            onClose={handleCloseModal}
            onSubmit={handleSubmit}
          />
        )}

        {/* ROUTINE LIBRARY */}
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
                id="routine-library-search"
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

          {formError && !routineModalOpen && (
            <p className="mb-4 rounded-xl bg-red-50 px-3 py-2 text-sm font-medium text-red-600">
              {formError}
            </p>
          )}

          {/* Routine Tiles */}
          <RoutineGrid
            deletePending={deleteMutation.isPending}
            hasSearch={hasSearch}
            isLoading={isLoading}
            routines={routines}
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

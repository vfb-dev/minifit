import { Dumbbell, Heart, Trash2, Pencil } from "lucide-react";

import { Button } from "@/components/ui/button";

import { translations } from "@/lib/translations";
import { useLanguageStore, type Language } from "@/store/languageStore";
import { getBodyPartLabel } from "@/lib/bodyParts";
import type { Exercise } from "@/services/exercises";

function toTitleCase(text: string) {
  return text.replace(/\w\S*/g, (word) => {
    return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
  });
}

function formatLastLogged(
  value: string | null | undefined,
  language: Language,
  fallback: string,
) {
  if (!value) return fallback;

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return fallback;

  return new Intl.DateTimeFormat(language === "pt" ? "pt-BR" : "en", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

type ExerciseTileProps = {
  deletePending: boolean;
  exercise: Exercise;
  onDelete: (id: number) => void;
  onEdit: (exercise: Exercise) => void;
};

export function ExerciseTile({
  deletePending,
  exercise,
  onDelete,
  onEdit,
}: ExerciseTileProps) {
  const { language } = useLanguageStore();
  const t = translations[language].exercisePage;
  const secondaryBodyParts = exercise.secondary_body_parts ?? [];

  return (
    <article
      key={exercise.id}
      className="rounded-xl border border-zinc-200 p-3 sm:p-4"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="grid size-8 shrink-0 place-items-center rounded-lg bg-zinc-100 sm:size-10 sm:rounded-xl">
              {exercise.primary_body_part === "cardio" ? (
                <Heart className="size-4 text-zinc-700 sm:size-5" />
              ) : (
                <Dumbbell className="size-4 text-zinc-700 sm:size-5" />
              )}
            </div>

            <div className="min-w-0">
              <h3 className="truncate text-sm font-semibold text-zinc-950 sm:text-base">
                {toTitleCase(exercise.name)}
              </h3>
              <p className="text-xs text-zinc-500 sm:text-sm">
                {exercise.set_count ?? 0} {t.setsLogged}
              </p>
            </div>
          </div>

          <div className="mt-2 flex flex-wrap gap-1.5 sm:mt-4 sm:gap-2">
            {exercise.primary_body_part ? (
              <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[11px] font-medium text-emerald-700 ring-1 ring-emerald-100 sm:px-3 sm:py-1 sm:text-xs">
                {getBodyPartLabel(exercise.primary_body_part, language)}
              </span>
            ) : (
              <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-[11px] font-medium text-zinc-500 sm:px-3 sm:py-1 sm:text-xs">
                {t.noPrimary}
              </span>
            )}

            {secondaryBodyParts.length > 0 && (
              <span className="rounded-full bg-blue-50 px-2 py-0.5 text-[11px] font-medium text-blue-700 ring-1 ring-blue-100 sm:hidden">
                +{secondaryBodyParts.length}
              </span>
            )}

            {secondaryBodyParts.map((bodyPart) => (
              <span
                key={bodyPart}
                className="hidden rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700 ring-1 ring-blue-100 sm:inline-flex"
              >
                {getBodyPartLabel(bodyPart, language)}
              </span>
            ))}
          </div>

          <p className="mt-3 hidden text-xs text-zinc-400 sm:block">
            {t.lastLogged}{" "}
            {formatLastLogged(exercise.last_logged_at, language, t.neverLogged)}
          </p>
        </div>

        <div className="flex shrink-0 gap-1.5 sm:gap-2">
          <Button
            type="button"
            variant="outline"
            size="icon"
            className="size-7 cursor-pointer sm:size-8"
            aria-label={t.edit}
            onClick={() => onEdit(exercise)}
          >
            <Pencil className="size-3.5 sm:size-4" />
          </Button>

          <Button
            type="button"
            variant="destructive"
            size="icon"
            className="size-7 cursor-pointer sm:size-8"
            aria-label={t.delete}
            disabled={deletePending}
            onClick={() => onDelete(exercise.id)}
          >
            <Trash2 className="size-3.5 sm:size-4" />
          </Button>
        </div>
      </div>
    </article>
  );
}

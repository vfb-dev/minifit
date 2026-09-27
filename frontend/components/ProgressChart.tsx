"use client";

import { SlidersHorizontal, Dumbbell, Activity } from "lucide-react";

import { ResponsiveBar } from "@nivo/bar";

import { useState } from "react";
import { useMediaQuery } from "usehooks-ts";

import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import {
  Popover,
  PopoverContent,
  PopoverDescription,
  PopoverHeader,
  PopoverTitle,
  PopoverTrigger,
} from "@/components/ui/popover";

import { Field, FieldGroup, FieldLabel } from "@/components/ui/field";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { Button } from "@/components/ui/button";

import { useQuery } from "@tanstack/react-query";
import { get_chart_data } from "@/services/chart";
import { getExerciseOptions, type Exercise } from "@/services/exercises";
import { translations } from "@/lib/translations";
import { useLanguageStore } from "@/store/languageStore";
import { getWorkoutExercises, type WorkoutType } from "@/lib/workoutExercises";

const PERIOD_OPTIONS = ["7D", "30D", "90D", "1Y", "max"];

type ChartData = {
  label: string;
  tooltip_label: string;
  value: number;
};

function toTitleCase(text: string) {
  return text.replace(/\w\S*/g, (word) => {
    return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
  });
}

function formatChartNumber(value: number) {
  if (value >= 1_000_000) {
    return `${Number((value / 1_000_000).toFixed(1))}M`;
  }

  if (value >= 1_000) {
    return `${Number((value / 1_000).toFixed(1))}k`;
  }

  return String(value);
}

export function ProgressChart() {
  const isMobile = useMediaQuery("(max-width: 768px)");
  const { language } = useLanguageStore();
  const t = translations[language].dashboard.chart;

  const [exerciseId, setExerciseId] = useState<string>("");
  const [workoutType, setWorkoutType] = useState<WorkoutType>("strength");
  const [period, setPeriod] = useState<string>("30D");
  const [metric, setMetric] = useState<string>("volume");

  const { data: exerciseOptions = [] } = useQuery<Exercise[]>({
    queryKey: ["exercise_options"],
    queryFn: () => getExerciseOptions(),
  });
  const availableExercises = getWorkoutExercises(exerciseOptions, workoutType);

  const hasSelectedExercise = availableExercises.some(
    (exercise) => String(exercise.id) === exerciseId,
  );
  const selectedExerciseId = hasSelectedExercise
    ? exerciseId
    : String(availableExercises[0]?.id ?? "");
  const selectedExercise = availableExercises.find(
    (exercise) => String(exercise.id) === selectedExerciseId,
  );
  const selectedExerciseName = selectedExercise?.name ?? "";

  const { data: chartData = [] } = useQuery<ChartData[]>({
    queryKey: ["chart", workoutType, selectedExerciseId, metric, period],

    queryFn: () =>
      get_chart_data({
        workout_type: workoutType,
        exercise: selectedExerciseId,
        metric,
        period,
      }),

    enabled: Boolean(selectedExerciseId),
  });

  const maxChartValue = Math.max(...chartData.map((item) => item.value), 0);
  const chartMax =
    maxChartValue > 0
      ? maxChartValue * (chartData.length <= 3 ? 1.25 : 1.15)
      : 1;
  const getBarPadding = (count: number) => {
    if (count <= 1) return isMobile ? 0.75 : 0.9;
    if (count <= 4) return isMobile ? 0.55 : 0.8;
    return isMobile ? 0.35 : 0.6;
  };
  const visibleTicks = chartData
    .filter((_, index) => {
      if (isMobile) {
        if (chartData.length <= 6) return true;
        if (chartData.length <= 12) return index % 2 === 0;

        return index % 4 === 0;
      }

      if (chartData.length <= 7) return true;
      if (chartData.length <= 14) return index % 2 === 0;

      return index % 3 === 0;
    })
    .map((item) => item.label);
  const selectedMetricLabel = {
    volume: t.volume,
    weight: t.weight,
    reps: t.reps,
    duration: t.duration,
    distance: t.distance,
    calories: t.calories,
  }[metric as "volume" | "weight" | "reps" | "duration" | "distance" | "calories"];

  function selectWorkoutType(type: WorkoutType) {
    setWorkoutType(type);
    setExerciseId("");
    setMetric(type === "cardio" ? "duration" : "volume");
  }

  const emptyState = (
    <div className="flex h-72 w-full flex-col items-center justify-center rounded-xl border border-dashed bg-zinc-50/50 px-4 text-center md:h-90 md:rounded-2xl">
      <div className="mb-4 rounded-full bg-white p-3 shadow-sm md:p-4">
        {workoutType === "cardio" ? <Activity className="size-5 text-zinc-400 md:size-6" /> : <Dumbbell className="size-5 text-zinc-400 md:size-6" />}
      </div>

      <h3 className="text-sm font-semibold text-zinc-900">{t.emptyTitle}</h3>

      <p className="mt-1 max-w-xs text-sm text-zinc-500">
        {workoutType === "cardio" && !availableExercises.length ? t.noCardioExercises : t.emptyDescription}
      </p>
    </div>
  );

  return (
    <>
      <div className="mb-4 space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <h3 className="text-lg font-semibold">{t.progress}</h3>

            {selectedExerciseName && <p className="mt-1 truncate text-xs text-zinc-500 sm:max-w-sm">
              {toTitleCase(selectedExerciseName)} - {selectedMetricLabel}
            </p>}
          </div>

          <div className="flex shrink-0 items-center gap-2">
            {!isMobile && (
              <ToggleGroup
                value={period}
                type="single"
                className="flex-wrap justify-start sm:justify-end"
                onValueChange={(value) => value && setPeriod(value)}
              >
                {PERIOD_OPTIONS.map((value) => (
                  <ToggleGroupItem
                    key={value}
                    className="w-12 cursor-pointer"
                    value={value}
                    aria-label={`Toggle ${value}`}
                  >
                    {value === "max" ? t.max : value}
                  </ToggleGroupItem>
                ))}
              </ToggleGroup>
            )}

            {/* Filters */}
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  className="size-9 cursor-pointer p-0 md:w-auto md:px-3"
                  variant="secondary"
                  aria-label={t.filters}
                >
                  <SlidersHorizontal className="size-4" />
                  <span className="hidden md:inline">{t.filters}</span>
                </Button>
              </PopoverTrigger>
              <PopoverContent
                className="w-[min(20rem,calc(100vw-2rem))] p-4"
                align="end"
              >
                <PopoverHeader className="mb-4">
                  <PopoverTitle>{t.filters}</PopoverTitle>
                  <PopoverDescription>{t.customizeChart}</PopoverDescription>
                </PopoverHeader>

                <FieldGroup className="gap-4">
                  <Field className="gap-2">
                    <FieldLabel htmlFor="exercise">{t.exercise}</FieldLabel>
                    <Select
                      value={selectedExerciseId}
                      onValueChange={(value) => setExerciseId(value)}
                    >
                      <SelectTrigger className="w-full cursor-pointer">
                        <SelectValue placeholder={t.exercise} />
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
                  </Field>
                  <Field className="gap-2">
                    <FieldLabel htmlFor="metric">{t.metric}</FieldLabel>

                    <Select
                      value={metric}
                      onValueChange={(value) => setMetric(value)}
                    >
                      <SelectTrigger className="w-full cursor-pointer">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectGroup>
                          {workoutType === "strength" ? <>
                            <SelectItem value="volume">{t.volume}</SelectItem>
                            <SelectItem value="weight">{t.weight}</SelectItem>
                            <SelectItem value="reps">{t.reps}</SelectItem>
                          </> : <>
                            <SelectItem value="duration">{t.duration}</SelectItem>
                            <SelectItem value="distance">{t.distance}</SelectItem>
                            <SelectItem value="calories">{t.calories}</SelectItem>
                          </>}
                        </SelectGroup>
                      </SelectContent>
                    </Select>
                  </Field>
                </FieldGroup>
              </PopoverContent>
            </Popover>
          </div>
        </div>

        <div className="flex gap-2" aria-label={t.workoutType}>
          {(["strength", "cardio"] as const).map((type) => (
            <Button key={type} type="button" size="sm" variant={workoutType === type ? "default" : "outline"}
              className="cursor-pointer" onClick={() => selectWorkoutType(type)}>
              {t[type]}
            </Button>
          ))}
        </div>

        {isMobile && (
          <div className="grid grid-cols-5 gap-1 rounded-xl bg-zinc-100 p-1">
            {PERIOD_OPTIONS.map((value) => {
              const isSelected = period === value;

              return (
                <button
                  key={value}
                  type="button"
                  className={`h-8 cursor-pointer rounded-lg text-xs font-medium transition ${
                    isSelected
                      ? "bg-white text-zinc-950 shadow-sm"
                      : "text-zinc-500 hover:text-zinc-900"
                  }`}
                  onClick={() => setPeriod(value)}
                >
                  {value === "max" ? t.max : value}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Chart */}
      {chartData.length ? (
        <div className="h-72 w-full md:h-90">
          <ResponsiveBar
            data={chartData}
            keys={["value"]}
            indexBy="label"
            margin={{
              top: isMobile ? 12 : 20,
              right: isMobile ? 4 : 20,
              bottom: 45,
              left: isMobile ? 38 : 60,
            }}
            padding={getBarPadding(chartData.length)}
            valueScale={{
              type: "linear",
              max: chartMax,
            }}
            indexScale={{ type: "band", round: true }}
            borderRadius={4}
            enableLabel={false}
            colors={({ index }) => {
              const start = [155, 223, 231]; // #9bdfe7
              const end = [77, 151, 215]; // #4d97d7

              const factor =
                chartData.length <= 1 ? 1 : index / (chartData.length - 1);

              const r = Math.round(start[0] + (end[0] - start[0]) * factor);
              const g = Math.round(start[1] + (end[1] - start[1]) * factor);
              const b = Math.round(start[2] + (end[2] - start[2]) * factor);

              return `rgb(${r}, ${g}, ${b})`;
            }}
            animate
            motionConfig="gentle"
            theme={{
              background: "transparent",

              text: {
                fill: "#9ca3af",
                fontSize: isMobile ? 10 : 11,
                fontFamily: "Inter, sans-serif",
              },

              axis: {
                domain: {
                  line: {
                    stroke: "transparent",
                  },
                },

                ticks: {
                  line: {
                    stroke: "transparent",
                  },

                  text: {
                    fill: "#9ca3af",
                    fontSize: isMobile ? 10 : 11,
                  },
                },
              },

              grid: {
                line: {
                  stroke: "#eceff1",
                  strokeWidth: 1,
                },
              },

              tooltip: {
                container: {
                  background: "white",
                  color: "#111827",
                  fontSize: 12,
                  borderRadius: "10px",
                  border: "1px solid #f1f5f9",
                  boxShadow: "0 4px 20px rgba(0,0,0,0.05)",
                  padding: "8px 10px",
                },
              },
            }}
            axisTop={null}
            axisRight={null}
            axisBottom={{
              tickSize: 0,
              tickPadding: isMobile ? 8 : 12,
              tickRotation: isMobile ? -45 : chartData.length > 7 ? -25 : 0,
              tickValues: visibleTicks,
            }}
            axisLeft={{
              tickSize: 0,
              tickPadding: 10,
              tickValues: 5,
              format: (value) => formatChartNumber(Number(value)),
            }}
            enableGridY
            gridYValues={5}
            tooltip={({ value, color, data }) => (
              <div className="min-w-32 rounded-xl border border-zinc-200 bg-white px-4 py-3 shadow-xl">
                {/* date */}
                <p className="text-[11px] font-medium uppercase tracking-wide text-zinc-400">
                  {data.tooltip_label}
                </p>

                {/* main value */}
                <div className="mt-2 flex items-center gap-2">
                  <div
                    className="size-2 rounded-full"
                    style={{ backgroundColor: color }}
                  />

                  <span className="text-xl font-bold text-zinc-900">
                    {Number(value).toLocaleString()}
                  </span>
                </div>

                {/* metric */}
                <p className="mt-1 text-xs text-zinc-500">
                  {metric === "volume" && t.trainingVolume}
                  {metric === "weight" && t.maxWeight}
                  {metric === "reps" && t.totalReps}
                  {metric === "duration" && t.totalDuration}
                  {metric === "distance" && t.totalDistance}
                  {metric === "calories" && t.totalCalories}
                </p>

                {/* exercise */}
                <div className="mt-3 border-t border-zinc-100 pt-2">
                  <p className="text-xs font-medium text-zinc-700">
                    {toTitleCase(selectedExerciseName)}
                  </p>
                </div>
              </div>
            )}
          />
        </div>
      ) : (
        emptyState
      )}
    </>
  );
}

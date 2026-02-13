"use client";

import dynamic from "next/dynamic";
import { PredictionResult } from "@/lib/api";

const Globe = dynamic(
  () => import("@/components/globe").then((mod) => ({ default: mod.Globe })),
  { ssr: false, loading: () => <div className="flex h-[500px] w-full items-center justify-center text-muted-foreground">Loading globe...</div> }
);

interface GlobeWrapperProps {
  prediction: PredictionResult | null;
}

export function GlobeWrapper({ prediction }: GlobeWrapperProps) {
  return <Globe prediction={prediction} />;
}

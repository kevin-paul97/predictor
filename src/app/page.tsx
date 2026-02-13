"use client";

import { useState } from "react";
import { PredictionResult } from "@/lib/api";
import { ImageUpload } from "@/components/image-upload";
import { PredictionResultDisplay } from "@/components/prediction-result";
import { GlobeWrapper } from "@/components/globe-wrapper";

export default function Home() {
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);

  return (
    <main className="min-h-screen bg-background p-6 md:p-12">
      <h1 className="mb-8 text-center text-3xl font-bold">
        Satellite Image Geolocation Predictor
      </h1>
      <div className="mx-auto grid max-w-6xl gap-6 md:grid-cols-2">
        <div className="space-y-6">
          <ImageUpload onPrediction={setPrediction} />
          {prediction && <PredictionResultDisplay result={prediction} />}
        </div>
        <div>
          <GlobeWrapper prediction={prediction} />
        </div>
      </div>
    </main>
  );
}

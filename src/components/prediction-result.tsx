"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PredictionResult } from "@/lib/api";

interface PredictionResultDisplayProps {
  result: PredictionResult;
}

export function PredictionResultDisplay({ result }: PredictionResultDisplayProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Predicted Coordinates</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Longitude</p>
            <p className="text-2xl font-mono font-semibold">
              {result.longitude.toFixed(4)}°
            </p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Latitude</p>
            <p className="text-2xl font-mono font-semibold">
              {result.latitude.toFixed(4)}°
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

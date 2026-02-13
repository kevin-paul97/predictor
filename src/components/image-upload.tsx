"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { predictLocation, PredictionResult } from "@/lib/api";

interface ImageUploadProps {
  onPrediction: (result: PredictionResult) => void;
}

export function ImageUpload({ onPrediction }: ImageUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const selected = acceptedFiles[0];
    if (!selected) return;
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setError(null);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [] },
    maxFiles: 1,
  });

  const handlePredict = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const result = await predictLocation(file);
      onPrediction(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prediction failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload Satellite Image</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div
          {...getRootProps()}
          className={`flex min-h-[200px] cursor-pointer items-center justify-center rounded-lg border-2 border-dashed p-6 transition-colors ${
            isDragActive
              ? "border-primary bg-primary/5"
              : "border-muted-foreground/25 hover:border-primary/50"
          }`}
        >
          <input {...getInputProps()} />
          {preview ? (
            <img
              src={preview}
              alt="Preview"
              className="max-h-[200px] rounded-md object-contain"
            />
          ) : (
            <p className="text-center text-sm text-muted-foreground">
              {isDragActive
                ? "Drop the image here..."
                : "Drag & drop a satellite image, or click to select"}
            </p>
          )}
        </div>

        {error && (
          <p className="text-sm text-destructive">{error}</p>
        )}

        <Button
          onClick={handlePredict}
          disabled={!file || loading}
          className="w-full"
        >
          {loading ? "Predicting..." : "Predict Location"}
        </Button>
      </CardContent>
    </Card>
  );
}

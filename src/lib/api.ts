export interface PredictionResult {
  longitude: number;
  latitude: number;
}

export async function predictLocation(file: File): Promise<PredictionResult> {
  const formData = new FormData();
  formData.append("file", file);

  let response: Response;
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    response = await fetch(`${apiUrl}/predict`, {
      method: "POST",
      body: formData,
    });
  } catch {
    throw new Error(
      "Cannot reach the backend. Make sure the server is running: cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000"
    );
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Prediction failed" }));
    throw new Error(error.detail || "Prediction failed");
  }

  return response.json();
}

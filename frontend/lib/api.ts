import type { AnalysisResult, HealthStatus } from "@/types/detection";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function analyzeImage(file: File): Promise<AnalysisResult> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/api/detect`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export async function getHistory(
  limit = 20,
  offset = 0
): Promise<AnalysisResult[]> {
  const response = await fetch(
    `${API_URL}/api/images?limit=${limit}&offset=${offset}`
  );
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}

export async function getHealth(): Promise<HealthStatus> {
  const response = await fetch(`${API_URL}/api/health`);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}

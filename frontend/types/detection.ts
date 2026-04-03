export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export type Severity = "critical" | "high" | "medium" | "low";

export interface Detection {
  label: string;
  confidence: number;
  bbox: BoundingBox;
  severity: Severity;
  source: "object-detection" | "zero-shot";
}

export interface AnalysisSummary {
  total_detections: number;
  hazards_found: number;
  safety_score: number;
  timestamp: string;
}

export interface AnalysisResult {
  id: string;
  image_url: string;
  detections: Detection[];
  summary: AnalysisSummary;
  created_at: string;
}

export interface HealthStatus {
  status: string;
  database: string;
  huggingface_api: string;
  version: string;
}

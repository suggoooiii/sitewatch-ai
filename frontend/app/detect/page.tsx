"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ImageUploader } from "@/components/ImageUploader";
import { DetectionCanvas } from "@/components/DetectionCanvas";
import { ResultsPanel } from "@/components/ResultsPanel";
import { analyzeImage } from "@/lib/api";
import type { AnalysisResult } from "@/types/detection";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function DetectPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setIsLoading(true);
    setError(null);
    setResult(null);
    try {
      const analysisResult = await analyzeImage(selectedFile);
      setResult(analysisResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">
          🔍 Site Safety Detection
        </h1>
        <p className="text-gray-400 mt-1">
          Upload a construction site image to detect safety hazards
        </p>
      </div>

      <div className="max-w-xl space-y-4">
        <ImageUploader
          onFileSelect={setSelectedFile}
          isLoading={isLoading}
          selectedFile={selectedFile}
        />
        <Button
          onClick={handleAnalyze}
          disabled={!selectedFile || isLoading}
          size="lg"
          className="w-full bg-blue-600 hover:bg-blue-700"
        >
          {isLoading ? "⏳ Analyzing..." : "🚀 Analyze Image"}
        </Button>
        {error && (
          <p className="text-red-400 text-sm bg-red-400/10 px-4 py-3 rounded-lg">
            ⚠️ {error}
          </p>
        )}
      </div>

      {isLoading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-96 rounded-xl bg-gray-800" />
          <div className="space-y-4">
            <Skeleton className="h-40 rounded-xl bg-gray-800" />
            <Skeleton className="h-64 rounded-xl bg-gray-800" />
          </div>
        </div>
      )}

      {result && !isLoading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h2 className="text-sm font-medium text-gray-400 mb-3">
              Detection Overlay
            </h2>
            <DetectionCanvas
              imageUrl={`${API_URL}${result.image_url}`}
              detections={result.detections}
            />
          </div>
          <div>
            <h2 className="text-sm font-medium text-gray-400 mb-3">
              Analysis Results
            </h2>
            <ResultsPanel result={result} />
          </div>
        </div>
      )}
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { getHistory } from "@/lib/api";
import type { AnalysisResult } from "@/types/detection";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function SafetyBadge({ score }: { score: number }) {
  const color =
    score >= 80
      ? "border-green-500/50 text-green-400 bg-green-500/10"
      : score >= 60
      ? "border-yellow-500/50 text-yellow-400 bg-yellow-500/10"
      : score >= 40
      ? "border-orange-500/50 text-orange-400 bg-orange-500/10"
      : "border-red-500/50 text-red-400 bg-red-500/10";
  return (
    <Badge variant="outline" className={`text-sm font-bold px-3 py-1 ${color}`}>
      {score}/100
    </Badge>
  );
}

export default function HistoryPage() {
  const [analyses, setAnalyses] = useState<AnalysisResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHistory()
      .then(setAnalyses)
      .catch((e) => setError(e.message))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">📋 Analysis History</h1>
        <p className="text-gray-400 mt-1">
          Browse past site safety analyses
        </p>
      </div>

      {isLoading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-48 rounded-xl bg-gray-800" />
          ))}
        </div>
      )}

      {error && (
        <p className="text-red-400 bg-red-400/10 px-4 py-3 rounded-lg">
          ⚠️ Failed to load history: {error}
        </p>
      )}

      {!isLoading && !error && analyses.length === 0 && (
        <div className="text-center py-24 space-y-4">
          <span className="text-6xl block">📭</span>
          <h2 className="text-xl font-semibold text-gray-400">
            No analyses yet
          </h2>
          <p className="text-gray-500">
            Head to the{" "}
            <Link href="/detect" className="text-blue-400 hover:underline">
              Detect
            </Link>{" "}
            page to run your first analysis.
          </p>
        </div>
      )}

      {!isLoading && analyses.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {analyses.map((a) => (
            <Card
              key={a.id}
              className="bg-gray-900 border-white/10 hover:border-white/20 transition-colors overflow-hidden"
            >
              <div className="aspect-video bg-gray-800 flex items-center justify-center overflow-hidden">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={`${API_URL}${a.image_url}`}
                  alt="Site analysis"
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src =
                      "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg'/>";
                  }}
                />
              </div>
              <CardContent className="pt-4 space-y-3">
                <div className="flex items-center justify-between">
                  <SafetyBadge score={a.summary.safety_score} />
                  <span className="text-xs text-gray-500">
                    {new Date(a.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex gap-4 text-sm">
                  <span className="text-gray-400">
                    <span className="text-white font-medium">
                      {a.summary.total_detections}
                    </span>{" "}
                    detections
                  </span>
                  <span className="text-gray-400">
                    <span
                      className={
                        a.summary.hazards_found > 0
                          ? "text-red-400 font-medium"
                          : "text-green-400 font-medium"
                      }
                    >
                      {a.summary.hazards_found}
                    </span>{" "}
                    hazards
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

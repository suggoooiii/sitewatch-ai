"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { HazardBadge } from "@/components/HazardBadge";
import type { AnalysisResult } from "@/types/detection";

interface ResultsPanelProps {
  result: AnalysisResult;
}

function SafetyScoreColor(score: number): string {
  if (score >= 80) return "text-green-400";
  if (score >= 60) return "text-yellow-400";
  if (score >= 40) return "text-orange-400";
  return "text-red-400";
}

export function ResultsPanel({ result }: ResultsPanelProps) {
  const { summary, detections } = result;

  return (
    <div className="space-y-4">
      <Card className="bg-gray-900 border-white/10">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-gray-400">
            Safety Score
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className={`text-5xl font-bold mb-3 ${SafetyScoreColor(summary.safety_score)}`}>
            {summary.safety_score}
            <span className="text-2xl text-gray-500">/100</span>
          </div>
          <Progress
            value={summary.safety_score}
            className="h-2 mb-4"
          />
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-white">
                {summary.total_detections}
              </div>
              <div className="text-xs text-gray-400">Detections</div>
            </div>
            <div>
              <div className={`text-2xl font-bold ${summary.hazards_found > 0 ? "text-red-400" : "text-green-400"}`}>
                {summary.hazards_found}
              </div>
              <div className="text-xs text-gray-400">Hazards</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-gray-900 border-white/10">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-gray-400">
            Detections ({detections.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <ScrollArea className="h-[400px]">
            {detections.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                <span className="text-3xl block mb-2">✅</span>
                No detections found
              </div>
            ) : (
              <div className="divide-y divide-white/5">
                {detections.map((det, idx) => (
                  <div key={idx} className="p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-white capitalize">
                        {det.label}
                      </span>
                      <HazardBadge severity={det.severity} />
                    </div>
                    <div className="flex items-center gap-2">
                      <Progress
                        value={det.confidence * 100}
                        className="h-1.5 flex-1"
                      />
                      <span className="text-xs text-gray-400 w-10 text-right">
                        {Math.round(det.confidence * 100)}%
                      </span>
                    </div>
                    <div className="flex gap-2">
                      <span className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded">
                        {det.source}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}

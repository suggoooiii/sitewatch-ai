"use client";

import { useCallback, useEffect, useRef } from "react";
import type { Detection, Severity } from "@/types/detection";

interface DetectionCanvasProps {
  imageUrl: string;
  detections: Detection[];
  className?: string;
}

const SEVERITY_COLORS: Record<Severity, string> = {
  critical: "#ef4444",
  high: "#f97316",
  medium: "#eab308",
  low: "#22c55e",
};

export function DetectionCanvas({
  imageUrl,
  detections,
  className = "",
}: DetectionCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imageRef = useRef<HTMLImageElement | null>(null);

  const drawCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    const img = imageRef.current;
    if (!canvas || !img) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;
    ctx.drawImage(img, 0, 0);

    for (const det of detections) {
      const { x, y, width, height } = det.bbox;
      const color = SEVERITY_COLORS[det.severity];

      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.strokeRect(x, y, width, height);

      const label = `${det.label} ${Math.round(det.confidence * 100)}%`;
      ctx.font = "bold 14px sans-serif";
      const textMetrics = ctx.measureText(label);
      const textWidth = textMetrics.width + 10;
      const textHeight = 22;
      const labelY = Math.max(0, y - textHeight);

      ctx.fillStyle = color + "cc";
      ctx.fillRect(x, labelY, textWidth, textHeight);

      ctx.fillStyle = "#ffffff";
      ctx.fillText(label, x + 5, labelY + 15);
    }
  }, [detections]);

  useEffect(() => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      imageRef.current = img;
      drawCanvas();
    };
    img.src = imageUrl;
  }, [imageUrl, drawCanvas]);

  return (
    <canvas
      ref={canvasRef}
      className={`w-full h-auto rounded-lg ${className}`}
      style={{ maxWidth: "100%" }}
    />
  );
}

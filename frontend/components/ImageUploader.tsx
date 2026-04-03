"use client";

import { useCallback, useState } from "react";
import { cn } from "@/lib/utils";

interface ImageUploaderProps {
  onFileSelect: (file: File) => void;
  isLoading?: boolean;
  selectedFile?: File | null;
}

const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];
const MAX_SIZE_MB = 10;

export function ImageUploader({
  onFileSelect,
  isLoading = false,
  selectedFile,
}: ImageUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFile = useCallback(
    (file: File) => {
      setError(null);
      if (!ACCEPTED_TYPES.includes(file.type)) {
        setError("Please upload a JPG, PNG, or WebP image.");
        return;
      }
      if (file.size > MAX_SIZE_MB * 1024 * 1024) {
        setError(`Image must be under ${MAX_SIZE_MB}MB.`);
        return;
      }
      onFileSelect(file);
    },
    [onFileSelect]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <div className="space-y-4">
      <label
        htmlFor="image-upload"
        className={cn(
          "flex flex-col items-center justify-center w-full h-48 border-2 border-dashed rounded-xl cursor-pointer transition-all",
          isDragging
            ? "border-blue-400 bg-blue-400/10"
            : "border-white/20 hover:border-white/40 hover:bg-white/5",
          isLoading && "pointer-events-none opacity-50"
        )}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
      >
        <div className="flex flex-col items-center gap-3 text-center px-6">
          <span className="text-4xl">{selectedFile ? "🖼️" : "📂"}</span>
          {selectedFile ? (
            <div>
              <p className="text-sm font-medium text-white">{selectedFile.name}</p>
              <p className="text-xs text-gray-400 mt-1">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          ) : (
            <div>
              <p className="text-sm font-medium text-white">
                Drag & drop an image here
              </p>
              <p className="text-xs text-gray-400 mt-1">
                or click to browse — JPG, PNG, WebP up to 10MB
              </p>
            </div>
          )}
        </div>
        <input
          id="image-upload"
          type="file"
          accept={ACCEPTED_TYPES.join(",")}
          className="hidden"
          onChange={handleInputChange}
          disabled={isLoading}
        />
      </label>
      {error && (
        <p className="text-red-400 text-sm text-center">{error}</p>
      )}
    </div>
  );
}

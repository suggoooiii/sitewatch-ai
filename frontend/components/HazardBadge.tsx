import { Badge } from "@/components/ui/badge";
import type { Severity } from "@/types/detection";

interface HazardBadgeProps {
  severity: Severity;
  className?: string;
}

const severityConfig: Record<Severity, { label: string; className: string }> = {
  critical: { label: "CRITICAL", className: "bg-red-500/20 text-red-400 border-red-500/50" },
  high: { label: "HIGH", className: "bg-orange-500/20 text-orange-400 border-orange-500/50" },
  medium: { label: "MEDIUM", className: "bg-yellow-500/20 text-yellow-400 border-yellow-500/50" },
  low: { label: "LOW", className: "bg-green-500/20 text-green-400 border-green-500/50" },
};

export function HazardBadge({ severity, className = "" }: HazardBadgeProps) {
  const config = severityConfig[severity];
  return (
    <Badge
      variant="outline"
      className={`text-xs font-semibold ${config.className} ${className}`}
    >
      {config.label}
    </Badge>
  );
}

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const features = [
  {
    icon: "🔍",
    title: "Real-time Detection",
    description:
      "Detect PPE compliance, unsafe behaviors, and site hazards in seconds using state-of-the-art computer vision models.",
  },
  {
    icon: "🎯",
    title: "Zero-Shot Hazard ID",
    description:
      "Identify novel hazards without retraining. OWL-ViT detects any label you describe — no custom dataset required.",
  },
  {
    icon: "📊",
    title: "Safety Scoring",
    description:
      "Get an instant 0–100 safety score with severity-weighted deductions for every detected hazard.",
  },
  {
    icon: "📋",
    title: "Incident History",
    description:
      "Browse all past analyses, track trends, and review detection results anytime.",
  },
];

const hfTasks = [
  "Object Detection",
  "Zero-Shot Object Detection",
  "Image Classification",
];

export default function HomePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-24">
      {/* Hero */}
      <section className="text-center space-y-6">
        <div className="inline-flex items-center gap-2 text-5xl">🏗️</div>
        <h1 className="text-5xl sm:text-6xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
          SiteWatch AI
        </h1>
        <p className="text-xl text-gray-400 max-w-2xl mx-auto">
          AI-Powered Construction Site Safety Monitoring. Upload a photo, get
          instant hazard detection, severity scoring, and actionable safety
          insights.
        </p>
        <div className="flex gap-4 justify-center flex-wrap">
          <Button asChild size="lg" className="bg-blue-600 hover:bg-blue-700">
            <Link href="/detect">🚀 Get Started</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/history">📋 View History</Link>
          </Button>
        </div>
      </section>

      {/* Features */}
      <section>
        <h2 className="text-2xl font-bold text-center mb-8 text-gray-200">
          What It Does
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((f) => (
            <Card
              key={f.title}
              className="bg-gray-900 border-white/10 hover:border-white/20 transition-colors"
            >
              <CardContent className="pt-6 space-y-3">
                <div className="text-3xl">{f.icon}</div>
                <h3 className="font-semibold text-white">{f.title}</h3>
                <p className="text-sm text-gray-400">{f.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* HF Tasks */}
      <section className="text-center space-y-4">
        <h2 className="text-xl font-semibold text-gray-300">
          Powered by Hugging Face
        </h2>
        <div className="flex flex-wrap gap-2 justify-center">
          {hfTasks.map((task) => (
            <Badge
              key={task}
              variant="outline"
              className="text-sm px-4 py-1.5 border-orange-400/40 text-orange-300"
            >
              🤗 {task}
            </Badge>
          ))}
        </div>
      </section>
    </div>
  );
}

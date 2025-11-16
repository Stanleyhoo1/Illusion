import { GlassSurface } from "./GlassSurface";
import { FiShield, FiEye, FiAlertTriangle } from "react-icons/fi";
import { Progress } from "@/components/ui/progress";

interface Score {
  label: string;
  value: number;
  icon: "shield" | "eye" | "alert";
  description: string;
}

interface TransparencyScoresProps {
  scores: Score[];
}

export const TransparencyScores = ({ scores }: TransparencyScoresProps) => {
  const getIcon = (type: "shield" | "eye" | "alert") => {
    switch (type) {
      case "shield":
        return FiShield;
      case "eye":
        return FiEye;
      case "alert":
        return FiAlertTriangle;
    }
  };

  const getScoreColor = (value: number) => {
    if (value >= 80) return "from-green-500 to-emerald-500";
    if (value >= 60) return "from-yellow-500 to-orange-500";
    return "from-orange-500 to-red-500";
  };

  return (
    <GlassSurface width={0} height={0} borderRadius={32} className="w-full shadow-glass-glow backdrop-blur-glass-lg">
      <div className="space-y-6">
        <div className="flex items-center gap-3 pb-4 border-b-2" style={{
          borderColor: "hsl(var(--glass-border-start) / 0.3)",
        }}>
          <div className="p-3 rounded-2xl bg-gradient-to-br from-blue-500/90 to-teal-400/90 shadow-glass">
            <FiShield className="w-5 h-5 text-white" />
          </div>
          <h3 className="text-2xl font-black text-foreground">Transparency Scores</h3>
        </div>

        <div className="space-y-6">
          {scores.map((score, index) => {
            const Icon = getIcon(score.icon);
            return (
              <div
                key={index}
                className="p-5 rounded-2xl"
                style={{
                  background: "linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0.2) 100%)",
                  backdropFilter: "blur(20px)",
                }}
              >
                <div className="flex items-center gap-3 mb-3">
                  <Icon className="w-5 h-5 text-foreground" />
                  <h4 className="text-lg font-bold text-foreground">{score.label}</h4>
                  <span className={`ml-auto text-2xl font-black bg-gradient-to-r ${getScoreColor(score.value)} bg-clip-text text-transparent`}>
                    {score.value}%
                  </span>
                </div>
                <Progress value={score.value} className="mb-3 h-2" />
                <p className="text-sm text-muted-foreground font-medium">{score.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </GlassSurface>
  );
};

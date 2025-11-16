import { FiCheckCircle } from "react-icons/fi";

interface TransparencyScoreCircularProps {
  score: number;
}

export const TransparencyScoreCircular = ({ score }: TransparencyScoreCircularProps) => {
  const getScoreColor = (value: number) => {
    if (value >= 4) return "hsl(142, 76%, 36%)"; // green
    if (value >= 3) return "hsl(45, 93%, 47%)"; // yellow
    return "hsl(0, 84%, 60%)"; // red
  };

  const getScoreLabel = (value: number) => {
    if (value >= 4) return "Good";
    if (value >= 3) return "Fair";
    return "Poor";
  };

  const percentage = (score / 5) * 100;
  const circumference = 2 * Math.PI * 70; // radius = 70
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="w-full h-full rounded-[32px] bg-light-blue shadow-glass p-6 flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="relative w-48 h-48">
          {/* Background circle */}
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="96"
              cy="96"
              r="70"
              stroke="hsl(var(--muted))"
              strokeWidth="12"
              fill="none"
            />
            {/* Progress circle */}
            <circle
              cx="96"
              cy="96"
              r="70"
              stroke={getScoreColor(score)}
              strokeWidth="12"
              fill="none"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          
          {/* Center content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <FiCheckCircle className="w-8 h-8 mb-2" style={{ color: getScoreColor(score) }} />
            <span className="text-5xl font-black" style={{ color: getScoreColor(score) }}>
              {score}
            </span>
            <span className="text-lg text-muted-foreground font-medium">/5</span>
          </div>
        </div>
        
        <div className="text-center">
          <h3 className="text-2xl font-black text-foreground mb-1">Transparency Score</h3>
          <p className="text-lg font-semibold" style={{ color: getScoreColor(score) }}>
            {getScoreLabel(score)}
          </p>
        </div>
      </div>
    </div>
  );
};

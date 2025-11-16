import { FiFileText } from "react-icons/fi";
import { GlassIcon } from "./GlassIcon";

interface SummaryBoxProps {
  overview: string;
  key_findings: string[];
  final_recommendation: string;
}

export const SummaryBox = ({ overview, key_findings, final_recommendation }: SummaryBoxProps) => {
  return (
    <div className="w-full rounded-[32px] bg-light-blue shadow-glass p-6">
      <div className="space-y-4">
        <div className="flex items-center gap-3 pb-4 border-b-2" style={{
          borderColor: "hsl(var(--glass-border-start) / 0.3)",
        }}>
          <GlassIcon icon={<FiFileText className="w-5 h-5" />} color="blue" size="sm" />
          <h3 className="text-2xl font-black text-foreground">Summary</h3>
        </div>

        <div className="space-y-4">
          <div className="p-5 rounded-2xl bg-card/50">
            <h4 className="text-base font-bold text-foreground mb-3">Overview</h4>
            <ul className="space-y-2">
              {key_findings.map((finding, index) => (
                <li key={index} className="text-sm text-foreground flex gap-2">
                  <span className="text-primary font-bold">•</span>
                  <span>{finding}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="p-5 rounded-2xl bg-card/50">
            <h4 className="text-base font-bold text-foreground mb-2">Final Recommendation</h4>
            <p className="text-sm text-foreground leading-relaxed">{final_recommendation}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

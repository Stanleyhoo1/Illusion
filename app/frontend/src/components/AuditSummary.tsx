import { GlassSurface } from "./GlassSurface";
import { FiFileText } from "react-icons/fi";

interface AuditSummaryProps {
  companyName: string;
  summary: {
    whatHappening: string;
    whatsGood: string[];
    whatsConcerning: string[];
    whatToKnow: string;
    whyItMatters: string;
  };
}

export const AuditSummary = ({ companyName, summary }: AuditSummaryProps) => {
  return (
    <GlassSurface width={0} height={0} borderRadius={32} className="w-full shadow-glass-glow backdrop-blur-glass-lg">
      <div className="space-y-6">
        <div className="flex items-center gap-3 pb-4 border-b-2" style={{
          borderColor: "hsl(var(--glass-border-start) / 0.3)",
        }}>
          <div className="p-3 rounded-2xl bg-gradient-to-br from-blue-500/90 to-teal-400/90 shadow-glass">
            <FiFileText className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-2xl font-black text-foreground">Transparency Audit</h3>
            <p className="text-sm text-muted-foreground font-medium">{companyName}</p>
          </div>
        </div>

        <div className="space-y-5">
          <div className="p-5 rounded-2xl" style={{
            background: "linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%)",
            backdropFilter: "blur(20px)",
          }}>
            <h4 className="text-lg font-bold text-foreground mb-2">What's happening?</h4>
            <p className="text-sm text-muted-foreground font-medium leading-relaxed">
              {summary.whatHappening}
            </p>
          </div>

          <div className="p-5 rounded-2xl" style={{
            background: "linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%)",
            backdropFilter: "blur(20px)",
          }}>
            <h4 className="text-lg font-bold text-foreground mb-3">What's good?</h4>
            <ul className="space-y-2">
              {summary.whatsGood.map((item, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground font-medium">
                  <span className="text-green-600 dark:text-green-400 mt-0.5">✓</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="p-5 rounded-2xl" style={{
            background: "linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%)",
            backdropFilter: "blur(20px)",
          }}>
            <h4 className="text-lg font-bold text-foreground mb-3">What's concerning?</h4>
            <ul className="space-y-2">
              {summary.whatsConcerning.map((item, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground font-medium">
                  <span className="text-red-600 dark:text-red-400 mt-0.5">⚠</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="p-5 rounded-2xl" style={{
            background: "linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0.2) 100%)",
            backdropFilter: "blur(20px)",
          }}>
            <h4 className="text-lg font-bold text-foreground mb-2">What should you know?</h4>
            <p className="text-sm text-muted-foreground font-medium leading-relaxed">
              {summary.whatToKnow}
            </p>
          </div>

          <div className="p-5 rounded-2xl" style={{
            background: "linear-gradient(135deg, rgba(147, 51, 234, 0.1) 0%, rgba(126, 34, 206, 0.05) 100%)",
            backdropFilter: "blur(20px)",
          }}>
            <h4 className="text-lg font-bold text-foreground mb-2">Why does this matter?</h4>
            <p className="text-sm text-muted-foreground font-medium leading-relaxed">
              {summary.whyItMatters}
            </p>
          </div>
        </div>
      </div>
    </GlassSurface>
  );
};

import { GlassSurface } from "./GlassSurface";
import { FiCheckCircle, FiAlertCircle, FiInfo } from "react-icons/fi";
import { Badge } from "@/components/ui/badge";

interface Finding {
  id: string;
  category: string;
  type: "good" | "concern" | "info";
  title: string;
  description: string;
  citation: string;
  source: string;
}

interface KeyFindingsProps {
  findings: Finding[];
}

export const KeyFindings = ({ findings }: KeyFindingsProps) => {
  const getIcon = (type: "good" | "concern" | "info") => {
    switch (type) {
      case "good":
        return FiCheckCircle;
      case "concern":
        return FiAlertCircle;
      case "info":
        return FiInfo;
    }
  };

  const getTypeStyles = (type: "good" | "concern" | "info") => {
    switch (type) {
      case "good":
        return {
          bg: "linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.05) 100%)",
          iconColor: "text-green-600 dark:text-green-400",
          badgeVariant: "default" as const,
        };
      case "concern":
        return {
          bg: "linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.05) 100%)",
          iconColor: "text-red-600 dark:text-red-400",
          badgeVariant: "destructive" as const,
        };
      case "info":
        return {
          bg: "linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.05) 100%)",
          iconColor: "text-blue-600 dark:text-blue-400",
          badgeVariant: "secondary" as const,
        };
    }
  };

  const groupedFindings = findings.reduce((acc, finding) => {
    if (!acc[finding.category]) {
      acc[finding.category] = [];
    }
    acc[finding.category].push(finding);
    return acc;
  }, {} as Record<string, Finding[]>);

  return (
    <GlassSurface width={0} height={0} borderRadius={32} className="w-full shadow-glass-glow backdrop-blur-glass-lg">
      <div className="space-y-6">
        <div className="flex items-center gap-3 pb-4 border-b-2" style={{
          borderColor: "hsl(var(--glass-border-start) / 0.3)",
        }}>
          <div className="p-3 rounded-2xl bg-gradient-to-br from-blue-500/90 to-teal-400/90 shadow-glass">
            <FiInfo className="w-5 h-5 text-white" />
          </div>
          <h3 className="text-2xl font-black text-foreground">Key Findings</h3>
        </div>

        <div className="space-y-6">
          {Object.entries(groupedFindings).map(([category, categoryFindings]) => (
            <div key={category}>
              <h4 className="text-lg font-black text-foreground mb-4 bg-gradient-to-r from-blue-700 via-cyan-600 to-teal-600 bg-clip-text text-transparent">
                {category}
              </h4>
              <div className="space-y-4">
                {categoryFindings.map((finding) => {
                  const Icon = getIcon(finding.type);
                  const styles = getTypeStyles(finding.type);
                  
                  return (
                    <div
                      key={finding.id}
                      className="p-5 rounded-2xl"
                      style={{
                        background: styles.bg,
                        backdropFilter: "blur(20px)",
                      }}
                    >
                      <div className="flex items-start gap-3 mb-3">
                        <Icon className={`w-5 h-5 mt-0.5 flex-shrink-0 ${styles.iconColor}`} />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2">
                            <h5 className="text-base font-bold text-foreground">{finding.title}</h5>
                            <Badge variant={styles.badgeVariant} className="text-xs">
                              {finding.type}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground font-medium mb-3">
                            {finding.description}
                          </p>
                          <div className="p-3 rounded-xl" style={{
                            background: "rgba(0,0,0,0.1)",
                          }}>
                            <p className="text-xs text-muted-foreground italic mb-2">
                              "{finding.citation}"
                            </p>
                            <p className="text-xs font-bold text-foreground">
                              Source: {finding.source}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </GlassSurface>
  );
};

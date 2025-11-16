import { FiAlertCircle } from "react-icons/fi";
import { GlassIcon } from "./GlassIcon";

interface ReasoningItem {
  rating: string;
  evidence: Array<{
    url: string;
    point: string;
  }>;
  explanation: string;
}

interface ReasoningBoxProps {
  reasoning: ReasoningItem[];
}

export const ReasoningBox = ({ reasoning }: ReasoningBoxProps) => {
  const formatRatingName = (rating: string) => {
    return rating
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className="w-full rounded-[32px] bg-light-blue shadow-glass p-6">
      <div className="space-y-4">
        <div className="flex items-center gap-3 pb-4 border-b-2" style={{
          borderColor: "hsl(var(--glass-border-start) / 0.3)",
        }}>
          <GlassIcon icon={<FiAlertCircle className="w-5 h-5" />} color="blue" size="sm" />
          <h3 className="text-2xl font-black text-foreground">Reasoning</h3>
        </div>

        <div className="space-y-4">
          {reasoning.map((item, index) => (
            <div key={index} className="p-5 rounded-2xl bg-card/50">
              <h4 className="text-lg font-bold text-foreground mb-3">
                {formatRatingName(item.rating)}
              </h4>
              
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-semibold text-muted-foreground mb-2">Evidence:</p>
                  {item.evidence.map((ev, evIndex) => (
                    <div key={evIndex} className="ml-4 mb-2">
                      <p className="text-sm text-foreground font-medium">• {ev.point}</p>
                      <a 
                        href={ev.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-xs text-primary hover:underline"
                      >
                        Source: {ev.url}
                      </a>
                    </div>
                  ))}
                </div>
                
                <div>
                  <p className="text-sm font-semibold text-muted-foreground mb-2">Explanation:</p>
                  <p className="text-sm text-foreground ml-4">{item.explanation}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

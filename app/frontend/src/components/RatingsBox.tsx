import { useState } from "react";
import { FiShield, FiUsers, FiEye, FiCheckCircle, FiInfo } from "react-icons/fi";
import { GlassIcon } from "./GlassIcon";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";

interface ReasoningItem {
  rating: string;
  evidence: Array<{
    url: string;
    point: string;
  }>;
  explanation: string;
}

interface RatingsBoxProps {
  ratings: {
    data_collection_risk: number;
    data_sharing_risk: number;
    tracking_risk: number;
    transparency_score: number;
  };
  reasoning: ReasoningItem[];
}

export const RatingsBox = ({ ratings, reasoning }: RatingsBoxProps) => {
  const [selectedRisk, setSelectedRisk] = useState<string | null>(null);

  const formatRatingName = (rating: string) => {
    return rating
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const getReasoning = (riskType: string) => {
    return reasoning.find(r => r.rating === riskType);
  };
  const getRatingColor = (value: number, inverse: boolean = false) => {
    if (inverse) {
      if (value >= 4) return "text-green-600";
      if (value >= 3) return "text-yellow-600";
      return "text-red-600";
    }
    if (value >= 4) return "text-red-600";
    if (value >= 3) return "text-yellow-600";
    return "text-green-600";
  };

  const getRatingLabel = (value: number, inverse: boolean = false) => {
    if (inverse) {
      if (value >= 4) return "Good";
      if (value >= 3) return "Fair";
      return "Poor";
    }
    if (value >= 4) return "High Risk";
    if (value >= 3) return "Medium Risk";
    return "Low Risk";
  };

  const ratingItems = [
    {
      icon: <FiShield className="w-5 h-5" />,
      label: "Data Collection Risk",
      value: ratings.data_collection_risk,
      color: "indigo",
      inverse: false,
      riskType: "data_collection_risk"
    },
    {
      icon: <FiUsers className="w-5 h-5" />,
      label: "Data Sharing Risk",
      value: ratings.data_sharing_risk,
      color: "blue",
      inverse: false,
      riskType: "data_sharing_risk"
    },
    {
      icon: <FiEye className="w-5 h-5" />,
      label: "Tracking Risk",
      value: ratings.tracking_risk,
      color: "indigo",
      inverse: false,
      riskType: "tracking_risk"
    }
  ];

  const selectedReasoning = selectedRisk ? getReasoning(selectedRisk) : null;

  return (
    <div className="w-full rounded-[32px] bg-light-blue shadow-glass p-6">
      <div className="space-y-4">
        <div className="flex items-center gap-3 pb-4 border-b-2" style={{
          borderColor: "hsl(var(--glass-border-start) / 0.3)",
        }}>
          <GlassIcon icon={<FiShield className="w-5 h-5" />} color="blue" size="sm" />
          <h3 className="text-2xl font-black text-foreground">Risk Ratings</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {ratingItems.map((item, index) => (
            <div key={index} className="p-4 rounded-2xl bg-card/50 relative">
              <button
                onClick={() => setSelectedRisk(item.riskType)}
                className="absolute top-3 right-3 p-1 rounded-lg hover:bg-muted/50 transition-colors"
                aria-label="View reasoning"
              >
                <FiInfo className="w-4 h-4 text-muted-foreground hover:text-foreground" />
              </button>
              <div className="flex flex-col items-center text-center gap-3 h-full justify-center">
                <GlassIcon icon={item.icon} color={item.color as any} size="sm" />
                <span className="text-base font-bold text-foreground min-h-[3rem] flex items-center">{item.label}</span>
                <div className="flex items-center gap-2">
                  <span className={`text-3xl font-black ${getRatingColor(item.value, item.inverse)}`}>
                    {item.value}
                  </span>
                  <span className="text-sm text-muted-foreground">/5</span>
                </div>
                <span className={`text-sm font-semibold ${getRatingColor(item.value, item.inverse)}`}>
                  {getRatingLabel(item.value, item.inverse)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <Dialog open={selectedRisk !== null} onOpenChange={(open) => !open && setSelectedRisk(null)}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-2xl font-black">
              {selectedReasoning && formatRatingName(selectedReasoning.rating)}
            </DialogTitle>
          </DialogHeader>
          {selectedReasoning && (
            <div className="space-y-4 mt-4">
              <div>
                <p className="text-sm font-semibold text-muted-foreground mb-2">Evidence:</p>
                {selectedReasoning.evidence.map((ev, evIndex) => (
                  <div key={evIndex} className="ml-4 mb-3">
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
              
              <div className="border-t-2 pt-4" style={{
                borderColor: "hsl(var(--glass-border-start) / 0.3)",
              }}>
                <p className="text-sm font-semibold text-muted-foreground mb-2">Explanation:</p>
                <p className="text-sm text-foreground ml-4">{selectedReasoning.explanation}</p>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

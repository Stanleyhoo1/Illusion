import { FiShield } from "react-icons/fi";
import { GlassIcon } from "./GlassIcon";

interface UserProtectionAdviceBoxProps {
  advice: string[];
}

export const UserProtectionAdviceBox = ({ advice }: UserProtectionAdviceBoxProps) => {
  return (
    <div className="w-full rounded-[32px] bg-light-blue shadow-glass p-6">
      <div className="space-y-4">
        <div className="flex items-center gap-3 pb-4 border-b-2" style={{
          borderColor: "hsl(var(--glass-border-start) / 0.3)",
        }}>
          <GlassIcon icon={<FiShield className="w-5 h-5" />} color="green" size="sm" />
          <h3 className="text-2xl font-black text-foreground">Protection Advice</h3>
        </div>

        <div className="p-5 rounded-2xl bg-card/50">
          <ul className="space-y-3">
            {advice.map((item, index) => (
              <li key={index} className="text-sm text-foreground flex gap-3">
                <span className="text-primary font-bold text-base">✓</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

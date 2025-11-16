import { GlassSurface } from "./GlassSurface";
import { FiLink } from "react-icons/fi";
import { GlassIcon } from "./GlassIcon";

interface Source {
  url: string;
  policy_type: string;
  relevance: number;
  title: string | null;
}

interface SourcesBoxProps {
  sources: Source[];
}

export const SourcesBox = ({ sources }: SourcesBoxProps) => {
  const formatPolicyType = (type: string) => {
    return type
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
          <GlassIcon icon={<FiLink className="w-5 h-5" />} color="indigo" size="sm" />
          <h3 className="text-2xl font-black text-foreground">Sources</h3>
        </div>

        <div className="p-5 rounded-2xl bg-card/50 space-y-3">
          {sources.map((source, index) => (
            <a
              key={index}
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block p-4 rounded-xl bg-background/50 hover:bg-background/80 transition-all duration-300 group"
            >
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-3 flex-1">
                  <FiLink className="w-5 h-5 text-primary group-hover:scale-110 transition-transform flex-shrink-0" />
                  <div className="flex flex-col gap-1">
                    <span className="text-base font-bold text-foreground group-hover:text-primary transition-colors">
                      {source.title || formatPolicyType(source.policy_type)}
                    </span>
                    <span className="text-sm text-muted-foreground truncate max-w-md">
                      {source.url}
                    </span>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-1 flex-shrink-0">
                  <span className="text-xs text-muted-foreground">{formatPolicyType(source.policy_type)}</span>
                  <span className="text-xs font-semibold text-primary">
                    {Math.round(source.relevance * 100)}% relevant
                  </span>
                </div>
              </div>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
};

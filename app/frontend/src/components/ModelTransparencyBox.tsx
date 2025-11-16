import { Brain, Clock, DollarSign, Sparkles, Wrench, Search, FileText, Database, Globe, Code, MessageSquare, Zap, FileSearch, ScrollText, Download } from "lucide-react";

interface ModelTransparencyProps {
  data: {
    token_usage: number;
    total_cost: number;
    elapsed_time: number;
    tools_used: string[];
    thoughts: string[];
  };
}

// Map tool names to icons
const getToolIcon = (toolName: string) => {
  const lowerName = toolName.toLowerCase();
  if (lowerName.includes('extract')) return Download;
  if (lowerName.includes('summary') || lowerName.includes('summarize')) return ScrollText;
  if (lowerName.includes('search') || lowerName.includes('query')) return Search;
  if (lowerName.includes('database') || lowerName.includes('db')) return Database;
  if (lowerName.includes('web') || lowerName.includes('browser')) return Globe;
  if (lowerName.includes('code') || lowerName.includes('script')) return Code;
  if (lowerName.includes('message') || lowerName.includes('chat')) return MessageSquare;
  if (lowerName.includes('file') || lowerName.includes('document')) return FileText;
  if (lowerName.includes('analyze') || lowerName.includes('analysis')) return FileSearch;
  return Zap; // default icon
};

export const ModelTransparencyBox = ({ data }: ModelTransparencyProps) => {
  return (
    <div className="w-full rounded-[32px] bg-light-blue shadow-glass p-6">
      <div className="space-y-3">
      <div className="flex items-center gap-3 mb-4">
        <Brain className="w-6 h-6 text-primary" />
        <h2 className="text-2xl font-bold text-foreground">Transparency</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-5">
        {/* Metrics */}
        <div className="md:border-r md:border-border md:pr-6">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold text-foreground">Metrics</h3>
          </div>
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-primary/10">
                <Sparkles className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground font-medium">Token Usage</p>
                <p className="text-2xl font-bold text-foreground">{data.token_usage.toLocaleString()}</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-primary/10">
                <DollarSign className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground font-medium">Total Cost</p>
                <p className="text-2xl font-bold text-foreground">${data.total_cost.toFixed(4)}</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-primary/10">
                <Clock className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground font-medium">Processing Time</p>
                <p className="text-2xl font-bold text-foreground">{data.elapsed_time.toFixed(2)}s</p>
              </div>
            </div>
          </div>
        </div>

        {/* Tools Used */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Wrench className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold text-foreground">Tools Used</h3>
          </div>
          <ol className="list-none space-y-2">
            {data.tools_used.map((tool, index) => {
              const ToolIcon = getToolIcon(tool);
              return (
                <li key={index} className="flex items-center gap-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <ToolIcon className="w-4 h-4 text-primary" />
                  </div>
                  <span className="text-base text-muted-foreground">{tool}</span>
                </li>
              );
            })}
          </ol>
        </div>
      </div>

      {/* Thoughts */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Brain className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-semibold text-foreground">Analysis Process</h3>
        </div>
        <div className="space-y-2">
          {data.thoughts.map((thought, index) => (
            <div key={index} className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/20 text-primary text-sm font-bold flex items-center justify-center leading-none">
                {index + 1}
              </span>
              <p className="text-sm text-muted-foreground flex-1">{thought}</p>
            </div>
          ))}
        </div>
      </div>
      </div>
    </div>
  );
};

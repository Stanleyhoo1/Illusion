import { useState, useEffect, useRef, useMemo } from "react";
import { GlassSurface } from "@/components/GlassSurface";
import { FiFileText, FiEye } from "react-icons/fi";
import { ArrowUp, Mic, MicOff } from "lucide-react";
import updraftIcon from "@/assets/updraft-icon.png";
import { GlassIcon } from "@/components/GlassIcon";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { RatingsBox } from "@/components/RatingsBox";
import { SummaryBox } from "@/components/SummaryBox";
import { UserProtectionAdviceBox } from "@/components/UserProtectionAdviceBox";
import { SourcesBox } from "@/components/SourcesBox";
import { TransparencyScoreCircular } from "@/components/TransparencyScoreCircular";
import { ModelTransparencyBox } from "@/components/ModelTransparencyBox";
// import digestionData from "@/data/sampleDigestion.json";
import Iridescence from "@/components/Iridescence";
import BlurText from "@/components/BlurText";

// Mock data types - replace with actual API response types
interface AuditResult {
  companyName: string;
  agentSteps: Array<{
    id: string;
    title: string;
    description: string;
    status: "complete" | "current" | "pending";
    documents?: string[];
  }>;
  scores: Array<{
    label: string;
    value: number;
    icon: "shield" | "eye" | "alert";
    description: string;
  }>;
  findings: Array<{
    id: string;
    category: string;
    type: "good" | "concern" | "info";
    title: string;
    description: string;
    citation: string;
    source: string;
  }>;
  summary: {
    whatHappening: string;
    whatsGood: string[];
    whatsConcerning: string[];
    whatToKnow: string;
    whyItMatters: string;
  };
  digestion: string;
}

const Index = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [input, setInput] = useState("");
  const [digestionData, setDigestionData] = useState<any | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isListening, setIsListening] = useState(false);
  const { toast } = useToast();
  const resultsRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);
  const iridescenceColor = useMemo(() => [0.584, 0.745, 0.812] as [number, number, number], []);

  useEffect(() => {
    if (showModal && resultsRef.current) {
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    }
  }, [showModal]);

  useEffect(() => {
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
        setIsListening(false);
      };

      recognitionRef.current.onerror = () => {
        setIsListening(false);
        toast({
          title: "Error",
          description: "Failed to recognize speech. Please try again.",
          variant: "destructive",
        });
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, [toast]);


  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const toggleListening = () => {
    if (!recognitionRef.current) {
      toast({
        title: "Not Supported",
        description: "Speech recognition is not supported in your browser.",
        variant: "destructive",
      });
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setIsLoading(true);
    setError(null);
    setShowModal(false);

    const company = encodeURIComponent(input.trim());
    const url = `http://127.0.0.1:8000/${company}`;

    try {
      console.log(`Fetching from: ${url}`);
      const resp = await fetch(url, {
        method: "GET",
        headers: {
          "Accept": "application/json",
        },
      });

      if (!resp.ok) {
        const text = await resp.text().catch(() => null);
        throw new Error(text || `Server returned ${resp.status}`);
      }

      const data = await resp.json();
      console.log("API Response:", data);
      setDigestionData(data);
      setShowModal(true);
    } catch (err: any) {
      console.error("Failed to fetch digestion data:", err);
      const errorMsg = err?.message?.includes("Failed to fetch")
        ? "Could not connect to the server. Make sure the backend is running at http://127.0.0.1:8000"
        : err?.message || "Unable to analyze this company. Please check the name or URL and try again.";
      setError(errorMsg);
      setDigestionData(null);
      toast({
        title: "Error",
        description: errorMsg,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`min-h-screen flex flex-col items-center relative ${!showModal ? 'justify-center' : ''}`}>
      {/* Animated iridescent background */}
      <div className="fixed inset-0">
        <Iridescence
          color={iridescenceColor}
          mouseReact={false}
          amplitude={0.1}
          speed={0.3}
        />
      </div>
      {/* Background overlay */}
      <div className="fixed inset-0 bg-background/60"></div>

      {/* Centered Content */}
      <div className={`w-full max-w-5xl px-4 relative z-10 space-y-8 ${showModal ? 'pt-48' : ''}`}>
        {/* Header */}
        <div className="text-center animate-fade-in">
          <div className="flex items-center justify-center mb-4">
            <div className="flex items-center">
              <BlurText
                text="Illusi"
                delay={150}
                animateBy="letters"
                direction="top"
                className="text-7xl font-black tracking-tight text-primary"
              />
              <span 
                className="mx-1 inline-block opacity-0 animate-eye-blur" 
                style={{ animationDelay: '0.9s' }}
              >
                <FiEye className="w-12 h-12 mt-4 text-[hsl(300,50%,80%)]" />
              </span>
              <BlurText
                text="n"
                delay={150}
                animateBy="letters"
                direction="top"
                className="text-7xl font-black tracking-tight text-primary"
                stepDuration={0.35}
              />
            </div>
          </div>
          <p
            className="text-xl mt-4 text-muted-foreground font-semibold max-w-2xl mx-auto"
            style={{ animationDelay: "0.1s" }}
          >
            Transparency
          </p>
        </div>

        {/* Input Section */}
        <div
          className="flex items-center justify-center animate-fade-in"
          style={{ animationDelay: "0.2s" }}
        >
          <div className="w-full max-w-3xl">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                  <div className="flex gap-3 items-center">
                  <div className="relative flex-1">
                    <FiFileText className="absolute left-5 top-1/2 -translate-y-1/2 h-5 w-5 text-primary" />
                    <Input
                      id="input"
                      type="text"
                      placeholder="Enter a company name or URL"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      className="pl-14 h-14 text-base rounded-2xl border-2 transition-all duration-300 font-medium bg-card border-border"
                      disabled={isLoading}
                    />
                  </div>
                  <Button
                    type="button"
                    onClick={toggleListening}
                    disabled={isLoading}
                    size="icon"
                    className={`h-14 w-14 rounded-2xl transition-all duration-500 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed ${
                      isListening ? 'bg-primary text-primary-foreground hover:bg-primary/90' : 'bg-secondary text-secondary-foreground hover:bg-secondary/90'
                    }`}
                  >
                    <Mic className="h-5 w-5" />
                  </Button>
                  <Button
                    type="submit"
                    disabled={isLoading || !input.trim()}
                    size="icon"
                    className="h-14 w-14 rounded-2xl transition-all duration-500 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed bg-primary text-primary-foreground hover:bg-primary/90"
                  >
                    <img src={updraftIcon} alt="Search" className="h-6 w-6 rotate-90" />
                  </Button>
                </div>
              </div>
            </form>
            {error && (
              <div className="mt-4 p-4 rounded-xl bg-destructive/10 border-2 border-destructive/30 animate-fade-in">
                <p className="text-destructive text-sm text-center font-medium">{error}</p>
              </div>
            )}
            <p className="text-center text-muted-foreground mt-4 text-sm">
              <strong>Illusion reveals how companies really use your data.</strong><br /><br />
              Enter any name or URL, and we surface hidden policies, assess risks, and give clear, AI-generated insights with trusted sources.
            </p>
          </div>
        </div>
      </div>

      {/* Results Box */}
      {showModal && (
        <div ref={resultsRef} className="w-full max-w-5xl px-4 pb-8 mt-96 relative z-10 animate-fade-in space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-1">
              <TransparencyScoreCircular score={digestionData.final_summary.summary.ratings.transparency_score} />
            </div>
            <div className="md:col-span-2">
              <RatingsBox 
                ratings={digestionData.final_summary.summary.ratings} 
                reasoning={digestionData.final_summary.summary.reasoning}
              />
            </div>
          </div>
          <SummaryBox 
            overview={digestionData.final_summary.summary.overview}
            key_findings={digestionData.final_summary.summary.key_findings}
            final_recommendation={digestionData.final_summary.summary.final_recommendation}
          />
          {digestionData.final_summary?.summary?.user_protection_advice && (
            <UserProtectionAdviceBox advice={digestionData.final_summary.summary.user_protection_advice} />
          )}
          {digestionData.timing && (
            <ModelTransparencyBox data={{
              token_usage: digestionData.timing.token_usage?.total_tokens || 0,
              total_cost: digestionData.timing.token_usage_detailed?.[0]?.total_cost_usd || 0,
              elapsed_time: (digestionData.timing.estimated_total_ms || 0) / 1000,
              tools_used: digestionData.trace?.tools_used || [],
              thoughts: digestionData.trace?.steps?.map((step: Record<string, unknown>) => (step as Record<string, unknown>).reasoning) || []
            }} />
          )}
          {digestionData.final_summary?.sources_used && (
            <SourcesBox sources={digestionData.final_summary.sources_used} />
          )}
        </div>
      )}

      {/* Scroll to Top Button */}
      <Button
        onClick={scrollToTop}
        size="icon"
        className="fixed bottom-8 right-8 h-12 w-12 rounded-full shadow-lg z-50 bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-300"
      >
        <ArrowUp className="h-5 w-5" />
      </Button>
    </div>
  );
};

export default Index;

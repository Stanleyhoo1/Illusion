import { useRef, useState, useEffect, ReactNode } from "react";

interface GlassSurfaceProps {
  children: ReactNode;
  width?: number;
  height?: number;
  borderRadius?: number;
  opacity?: number;
  brightness?: number;
  className?: string;
}

export const GlassSurface = ({
  children,
  width = 400,
  height = 300,
  borderRadius = 24,
  opacity = 0.85,
  brightness = 100,
  className = "",
}: GlassSurfaceProps) => {
  const surfaceRef = useRef<HTMLDivElement>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!surfaceRef.current) return;
    const rect = surfaceRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    setMousePosition({ x, y });
  };

  return (
    <div
      ref={surfaceRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`relative overflow-hidden ${className}`}
      style={{
        ...(width && width > 0 ? { width: `${width}px` } : {}),
        ...(height && height > 0 ? { height: `${height}px` } : {}),
        borderRadius: `${borderRadius}px`,
        background: `linear-gradient(135deg, hsl(var(--glass-bg) / ${opacity}) 0%, hsl(var(--glass-bg) / ${opacity * 0.95}) 100%)`,
        backdropFilter: `blur(40px) saturate(180%) brightness(${brightness}%)`,
        WebkitBackdropFilter: `blur(40px) saturate(180%) brightness(${brightness}%)`,
        border: "1.5px solid transparent",
        backgroundImage: `
          linear-gradient(135deg, hsl(var(--glass-bg) / ${opacity}), hsl(var(--glass-bg) / ${opacity * 0.95})),
          linear-gradient(135deg, hsl(var(--glass-border-start) / 0.6), hsl(var(--glass-border-end) / 0.6))
        `,
        backgroundOrigin: "border-box",
        backgroundClip: "padding-box, border-box",
        boxShadow: isHovered
          ? "var(--shadow-glass-lg)"
          : "var(--shadow-glass)",
        transform: isHovered ? "translateY(-2px)" : "translateY(0)",
        transition: "all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)",
      }}
    >
      {/* iOS-style inner glow border */}
      <div 
        className="absolute inset-0 rounded-[inherit] pointer-events-none"
        style={{
          background: `linear-gradient(135deg, 
            hsl(var(--glass-vibrant) / 0.15) 0%, 
            transparent 50%, 
            hsl(var(--secondary) / 0.1) 100%
          )`,
          opacity: isHovered ? 0.6 : 0.3,
          transition: "opacity 0.5s ease",
        }}
      />
      
      {/* Liquid shimmer effect */}
      <div
        className="absolute inset-0 transition-opacity duration-700 pointer-events-none rounded-[inherit]"
        style={{
          opacity: isHovered ? 0.15 : 0,
          background: `linear-gradient(135deg, 
            transparent 0%, 
            hsl(var(--glass-vibrant) / 0.4) 45%, 
            hsl(var(--secondary) / 0.4) 55%,
            transparent 100%
          )`,
          backgroundSize: "200% 200%",
          animation: isHovered ? "liquidFlow 3s ease-in-out infinite" : "none",
        }}
      />

      {/* Content */}
      <div className="relative z-10 h-full w-full p-6 flex flex-col justify-center">
        {children}
      </div>

      <style>{`
        @keyframes liquidFlow {
          0%, 100% { 
            background-position: 0% 0%;
            transform: scale(1);
          }
          50% { 
            background-position: 100% 100%;
            transform: scale(1.02);
          }
        }
      `}</style>
    </div>
  );
};

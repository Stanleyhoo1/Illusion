import React, { useState, useRef, useEffect, useCallback } from 'react';

interface GlassSurfaceProps {
  children: React.ReactNode;
  className?: string;
  width?: number;
  height?: number;
  borderRadius?: number;
  opacity?: number;
}

const GlassSurface: React.FC<GlassSurfaceProps> = ({
  children,
  className = '',
  width,
  height,
  borderRadius = 28,
}) => {
  const [mousePosition, setMousePosition] = useState({ x: -1000, y: -1000 });
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      setMousePosition({ x: e.clientX - rect.left, y: e.clientY - rect.top });
    }
  }, []);
  
  const handleMouseLeave = useCallback(() => {
    setMousePosition({ x: -1000, y: -1000 });
  }, []);

  useEffect(() => {
    const currentRef = containerRef.current;
    if (currentRef) {
      currentRef.addEventListener('mousemove', handleMouseMove);
      currentRef.addEventListener('mouseleave', handleMouseLeave);
    }

    return () => {
      if (currentRef) {
        currentRef.removeEventListener('mousemove', handleMouseMove);
        currentRef.removeEventListener('mouseleave', handleMouseLeave);
      }
    };
  }, [handleMouseMove, handleMouseLeave]);

  const style: React.CSSProperties = {
    width: width ? `${width}px` : undefined,
    height: height ? `${height}px` : undefined,
    borderRadius: `${borderRadius}px`,
    '--mouse-x': `${mousePosition.x}px`,
    '--mouse-y': `${mousePosition.y}px`,
  };

  return (
    <div
      ref={containerRef}
      style={style}
      className={`relative p-8 overflow-hidden transition-all duration-300 ease-out 
                  bg-white/40 backdrop-blur-xl
                  border border-white/50
                  shadow-lg
                  group ${className}`}
    >
      <div
        className="absolute inset-0 transition-opacity duration-500 opacity-0 group-hover:opacity-100"
        style={{
          background: `radial-gradient(400px circle at var(--mouse-x) var(--mouse-y), rgba(255, 255, 255, 0.3), transparent 40%)`,
        }}
      />
      <div className="relative z-10">{children}</div>
    </div>
  );
};

export default GlassSurface;
import React from 'react';

export interface GlassIconProps {
  icon: React.ReactElement;
  color?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const gradientMapping: Record<string, string> = {
  blue: 'linear-gradient(hsl(223, 90%, 50%), hsl(208, 90%, 50%))',
  purple: 'linear-gradient(hsl(283, 90%, 50%), hsl(268, 90%, 50%))',
  red: 'linear-gradient(hsl(3, 90%, 50%), hsl(348, 90%, 50%))',
  indigo: 'linear-gradient(hsl(253, 90%, 50%), hsl(238, 90%, 50%))',
  orange: 'linear-gradient(hsl(25, 100%, 80%), hsl(25, 100%, 75%))',
  green: 'linear-gradient(hsl(123, 90%, 40%), hsl(108, 90%, 40%))'
};

const sizeMapping = {
  sm: 'w-[3em] h-[3em]',
  md: 'w-[4.5em] h-[4.5em]',
  lg: 'w-[6em] h-[6em]'
};

export const GlassIcon: React.FC<GlassIconProps> = ({ 
  icon, 
  color = 'blue', 
  size = 'md',
  className = '' 
}) => {
  const getBackgroundStyle = (color: string): React.CSSProperties => {
    if (gradientMapping[color]) {
      return { background: gradientMapping[color] };
    }
    return { background: color };
  };

  return (
    <div
      className={`relative bg-transparent ${sizeMapping[size]} [perspective:24em] [transform-style:preserve-3d] group ${className}`}
    >
      <span
        className="absolute top-0 left-0 w-full h-full rounded-[1.25em] bg-[hsla(0,0%,100%,0.15)] transition-[opacity,transform] duration-300 ease-[cubic-bezier(0.83,0,0.17,1)] origin-[80%_50%] flex backdrop-blur-[0.75em] [-webkit-backdrop-filter:blur(0.75em)] transform group-hover:[transform:translateZ(2em)]"
        style={{
          boxShadow: '0 0 0 0.1em hsla(0, 0%, 100%, 0.3) inset'
        }}
      >
        <span className="m-auto w-[1.5em] h-[1.5em] flex items-center justify-center" aria-hidden="true">
          {icon}
        </span>
      </span>
    </div>
  );
};

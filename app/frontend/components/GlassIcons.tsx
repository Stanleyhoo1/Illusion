import React from 'react';
import { IconItem } from '../types';

interface GlassIconsProps {
  items: IconItem[];
}

const GlassIcons: React.FC<GlassIconsProps> = ({ items }) => {
  return (
    <div className="flex flex-wrap justify-center items-center gap-4">
      {items.map((item, index) => (
        <div key={index} className="flex flex-col items-center gap-2 group cursor-pointer">
          <div
            className={`relative w-16 h-16 flex items-center justify-center
                        rounded-2xl transition-all duration-300 ease-out
                        bg-white/40 backdrop-blur-md
                        border border-white/50
                        shadow-md group-hover:shadow-xl group-hover:scale-110 group-hover:-translate-y-1`}
          >
            <div className={`absolute inset-0 rounded-2xl opacity-50 group-hover:opacity-70 transition-opacity bg-gradient-to-br from-gray-200 to-gray-50`} />
            <div className="relative text-zinc-600 text-3xl drop-shadow-sm">
              {item.icon}
            </div>
          </div>
          <span className="text-sm font-medium text-zinc-500 opacity-80 group-hover:opacity-100 transition-opacity">
            {item.label}
          </span>
        </div>
      ))}
    </div>
  );
};

export default GlassIcons;
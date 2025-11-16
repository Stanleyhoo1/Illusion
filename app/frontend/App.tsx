import React from 'react';
import GlassSurface from './components/GlassSurface';
import GlassIcons from './components/GlassIcons';
import DecryptedText from './components/DecryptedText';
import Dock from './components/Dock';
import { FiFileText, FiBook, FiHeart, FiCloud, FiEdit, FiBarChart2, FiCpu } from 'react-icons/fi';
import { VscHome, VscArchive, VscAccount, VscSettingsGear } from 'react-icons/vsc';
import { IconItem } from './types';

const iconItems: IconItem[] = [
  { icon: <FiFileText />, color: 'gray', label: 'Files' },
  { icon: <FiBook />, color: 'gray', label: 'Docs' },
  { icon: <FiHeart />, color: 'gray', label: 'Health' },
  { icon: <FiCloud />, color: 'gray', label: 'Cloud' },
  { icon: <FiEdit />, color: 'gray', label: 'Notes' },
  { icon: <FiBarChart2 />, color: 'gray', label: 'Stats' },
];

const dockItems = [
  { icon: <VscHome size={18} className="text-gray-900" />, label: 'Home', onClick: () => alert('Home!') },
  { icon: <VscArchive size={18} className="text-gray-900" />, label: 'Archive', onClick: () => alert('Archive!') },
  { icon: <VscAccount size={18} className="text-gray-900" />, label: 'Profile', onClick: () => alert('Profile!') },
  { icon: <VscSettingsGear size={18} className="text-gray-900" />, label: 'Settings', onClick: () => alert('Settings!') },
];

const App: React.FC = () => {
  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-between p-4 md:p-8
                    bg-[#F8F8F8]
                    text-zinc-800
                    transition-colors duration-300">
      
      <div className="absolute inset-0 z-0 h-full w-full bg-white bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_24px]">
        <div className="absolute left-0 right-0 top-0 -z-10 m-auto h-[310px] w-[310px] rounded-full bg-gray-200 opacity-20 blur-[100px]"></div>
      </div>
      
      <main className="w-full max-w-7xl z-10 flex flex-col items-center mx-auto px-4 md:px-8">
        {/* Hero Section - Text Layout */}
        <section className="w-full min-h-[50vh] flex items-center justify-center pt-12 pb-8">
          <div className="text-6xl md:text-7xl lg:text-8xl xl:text-9xl font-bold tracking-tight text-black leading-none font-sans text-center">
            <DecryptedText 
              text="we unveil the fine-lines."
              animateOn="view"
              revealDirection="center"
            />
          </div>
        </section>

        <div className="w-full flex flex-col lg:flex-row gap-8 lg:gap-16 items-stretch justify-center mt-8">
          {/* Left Pane */}
          <section className="flex-1 flex flex-col gap-8 items-center lg:items-stretch">
            <GlassSurface width={480} height={280} borderRadius={28} className="w-full max-w-md lg:max-w-full xl:max-w-[480px] mx-auto lg:mx-0">
              <div className="flex flex-col justify-center h-full">
                <h2 className="text-2xl font-bold mb-3 bg-gradient-to-r from-zinc-800 via-zinc-600 to-zinc-500 bg-clip-text text-transparent">
                  Transparency Summary
                </h2>
                <p className="text-base font-medium text-zinc-600">
                  Every agent step, every memory, every decision—made traceable and explainable.
                </p>
              </div>
            </GlassSurface>

            <GlassSurface borderRadius={28} className="w-full max-w-md lg:max-w-full xl:max-w-[480px] mx-auto lg:mx-0">
                <GlassIcons items={iconItems} />
            </GlassSurface>
            
            <GlassSurface borderRadius={28} className="w-full max-w-md lg:max-w-full xl:max-w-[480px] mx-auto lg:mx-0">
               <div className="flex items-center gap-4">
                  <div className="w-12 h-12 flex items-center justify-center rounded-lg bg-gray-200/80 text-gray-500 text-2xl">
                    <FiCpu />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold bg-gradient-to-r from-zinc-700 to-zinc-500 bg-clip-text text-transparent">Agent Trajectory</h3>
                    <p className="text-sm font-medium text-zinc-500">Visualize the reasoning trace (coming soon).</p>
                  </div>
               </div>
            </GlassSurface>
          </section>

          {/* Right Pane */}
          <section className="flex-1 flex flex-col gap-8 items-center lg:items-stretch">
            <GlassSurface width={480} height={500} borderRadius={28} className="w-full max-w-md lg:max-w-full xl:max-w-[480px] mx-auto lg:mx-0">
               <div className="flex flex-col justify-center h-full items-center text-center">
                <div className="w-24 h-24 mb-6 flex items-center justify-center rounded-full bg-gray-200/50 border border-gray-300/40">
                  <FiFileText className="text-5xl text-gray-400" />
                </div>
                <h2 className="text-2xl font-bold mb-3 bg-gradient-to-r from-zinc-700 to-zinc-500 bg-clip-text text-transparent">
                  Document Preview
                </h2>
                <p className="text-base font-medium text-zinc-600">
                  Upload a document to visualize the agent's contextual reasoning.
                </p>
               </div>
            </GlassSurface>
          </section>
        </div>
      </main>

      <footer className="mt-16 py-8 w-full flex justify-center z-10">
        <GlassSurface borderRadius={16}>
          <div className="px-4 py-1">
            <span className="text-sm font-semibold text-zinc-500">
              © 2025 Agent Glass Box · Transparency Demo UI
            </span>
          </div>
        </GlassSurface>
      </footer>

      <Dock 
        items={dockItems}
        panelHeight={68}
        baseItemSize={50}
        magnification={70}
      />
    </div>
  );
};

export default App;
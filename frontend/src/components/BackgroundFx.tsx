import React from 'react';

export const BackgroundFx: React.FC = () => {
  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      {/* Subtle technical coordinate grid */}
      <div 
        className="absolute inset-0 opacity-[0.035]" 
        style={{
          backgroundImage: `
            linear-gradient(to right, #ffffff 1px, transparent 1px),
            linear-gradient(to bottom, #ffffff 1px, transparent 1px)
          `,
          backgroundSize: '48px 48px',
        }}
      />

      {/* Very faint radial glow centered at top */}
      <div 
        className="absolute -top-[250px] left-1/2 -translate-x-1/2 w-[900px] h-[500px] rounded-full opacity-[0.07] blur-[120px] pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse at center, #6366f1 0%, #38bdf8 50%, transparent 80%)',
        }}
      />

      {/* Ambient lower right subtle tint */}
      <div 
        className="absolute -bottom-[200px] -right-[100px] w-[600px] h-[500px] rounded-full opacity-[0.03] blur-[140px] pointer-events-none"
        style={{
          background: 'radial-gradient(circle, #38bdf8 0%, transparent 70%)',
        }}
      />

      {/* Decorative hairline accents */}
      <svg
        className="absolute top-0 left-0 w-full h-full opacity-[0.03] stroke-slate-400"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
      >
        <line x1="10%" y1="0" x2="10%" y2="100%" strokeDasharray="4 8" />
        <line x1="90%" y1="0" x2="90%" y2="100%" strokeDasharray="4 8" />
      </svg>
    </div>
  );
};

import React from 'react';
import { Shield } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full py-8 mt-auto border-t border-slate-800/60 text-center text-xs text-slate-400 font-mono">
      <div className="max-w-2xl mx-auto px-4 flex flex-col items-center gap-2">
        <div className="flex items-center gap-1.5 text-slate-400">
          <Shield className="w-3.5 h-3.5 text-slate-400" />
          <span>StreamForge Media Processing Utility</span>
        </div>
        <p className="text-[11px] leading-relaxed max-w-md text-slate-400">
          Please only download media content for which you have explicit rights or authorized permission. Respect creator copyrights and YouTube’s Terms of Service.
        </p>
      </div>
    </footer>
  );
};

import React from 'react';
import { motion } from 'framer-motion';
import { HardDrive, Zap, Clock } from 'lucide-react';
import { JobProgress } from '../types';

interface ProgressScreenProps {
  progressData: JobProgress;
}

export const ProgressScreen: React.FC<ProgressScreenProps> = ({ progressData }) => {
  const percent = Math.min(100, Math.max(0, progressData.progress));

  const isMerging = progressData.status === 'merging';
  const isFinalizing = progressData.status === 'finalizing';

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.98 }}
      transition={{ duration: 0.3 }}
      className="w-full max-w-2xl mx-auto mt-8 p-6 sm:p-8 rounded-2xl bg-[#11131b]/90 border border-slate-800 backdrop-blur-md shadow-2xl shadow-black/40"
    >
      {/* Top Header info */}
      <div className="flex items-center justify-between pb-6 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-indigo-500"></span>
          </span>
          <span className="font-mono text-xs uppercase tracking-wider text-indigo-400 font-semibold">
            {isMerging
              ? 'Processing Pipeline'
              : isFinalizing
              ? 'Finalizing Stream'
              : 'Active Stream Download'}
          </span>
        </div>

        <div className="text-xs font-mono text-slate-400 bg-slate-900/80 px-2.5 py-1 rounded-md border border-slate-800">
          JOB: {progressData.job_id}
        </div>
      </div>

      {/* Main Percentage Display */}
      <div className="py-8 flex flex-col items-center justify-center">
        <div className="flex items-baseline gap-1">
          <motion.span
            key={Math.floor(percent)}
            initial={{ opacity: 0.7, y: -2 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-6xl sm:text-7xl font-extrabold tracking-tight font-mono text-slate-100"
          >
            {percent.toFixed(0)}
          </motion.span>
          <span className="text-2xl sm:text-3xl font-bold text-indigo-400 font-mono">%</span>
        </div>

        {/* Human readable phase message */}
        <motion.p
          key={progressData.message}
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          className="mt-3 text-base sm:text-lg font-medium text-slate-200 text-center"
        >
          {progressData.message}
        </motion.p>
      </div>

      {/* Primary Progress Bar */}
      <div className="relative w-full h-3 bg-slate-900 rounded-full overflow-hidden border border-slate-800/80">
        <motion.div
          className={`h-full rounded-full transition-all duration-300 ${
            isMerging || isFinalizing
              ? 'bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 animate-pulse'
              : 'bg-gradient-to-r from-indigo-600 via-indigo-500 to-cyan-400'
          }`}
          style={{ width: `${percent}%` }}
        />
      </div>

      {/* Secondary Metrics Grid */}
      <div className="grid grid-cols-3 gap-3 sm:gap-4 mt-6 pt-6 border-t border-slate-800/80 text-center">
        
        {/* Metric 1: Downloaded / Total */}
        <div className="p-3 rounded-xl bg-slate-900/50 border border-slate-800/60">
          <div className="flex items-center justify-center gap-1.5 text-xs text-slate-400 mb-1">
            <HardDrive className="w-3.5 h-3.5 text-slate-500" />
            <span>Transferred</span>
          </div>
          <div className="font-mono text-xs sm:text-sm font-semibold text-slate-200 truncate">
            {progressData.formatted_downloaded}
            {progressData.formatted_total !== '--' && (
              <span className="text-slate-500 text-xs"> / {progressData.formatted_total}</span>
            )}
          </div>
        </div>

        {/* Metric 2: Speed */}
        <div className="p-3 rounded-xl bg-slate-900/50 border border-slate-800/60">
          <div className="flex items-center justify-center gap-1.5 text-xs text-slate-400 mb-1">
            <Zap className="w-3.5 h-3.5 text-slate-500" />
            <span>Speed</span>
          </div>
          <div className="font-mono text-xs sm:text-sm font-semibold text-slate-200">
            {isMerging || isFinalizing ? 'Local Mux' : progressData.formatted_speed}
          </div>
        </div>

        {/* Metric 3: ETA */}
        <div className="p-3 rounded-xl bg-slate-900/50 border border-slate-800/60">
          <div className="flex items-center justify-center gap-1.5 text-xs text-slate-400 mb-1">
            <Clock className="w-3.5 h-3.5 text-slate-500" />
            <span>Time Left</span>
          </div>
          <div className="font-mono text-xs sm:text-sm font-semibold text-slate-200">
            {isMerging || isFinalizing ? 'Finishing' : progressData.formatted_eta}
          </div>
        </div>

      </div>

    </motion.div>
  );
};

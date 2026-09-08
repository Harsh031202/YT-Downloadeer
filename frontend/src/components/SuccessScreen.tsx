import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, Download, FileVideo, FileAudio, RotateCcw, ShieldCheck } from 'lucide-react';
import confetti from 'canvas-confetti';
import { JobProgress } from '../types';
import { getDownloadUrl } from '../api/client';

interface SuccessScreenProps {
  progressData: JobProgress;
  onReset: () => void;
}

export const SuccessScreen: React.FC<SuccessScreenProps> = ({ progressData, onReset }) => {
  const isAudio = progressData.filename?.endsWith('.mp3') || progressData.filename?.endsWith('.m4a');
  const downloadUrl = getDownloadUrl(progressData.job_id);

  useEffect(() => {
    // Subtle, restrained celebratory micro-burst
    confetti({
      particleCount: 35,
      spread: 60,
      origin: { y: 0.7 },
      colors: ['#6366f1', '#38bdf8', '#10b981'],
      disableForReducedMotion: true,
    });
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, y: 15 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 120, damping: 16 }}
      className="w-full max-w-2xl mx-auto mt-8 p-6 sm:p-8 rounded-2xl bg-[#11131b]/90 border border-emerald-500/30 backdrop-blur-md shadow-2xl shadow-black/50"
    >
      {/* Animated Checkmark Badge */}
      <div className="flex flex-col items-center justify-center text-center">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 200, damping: 15, delay: 0.1 }}
          className="w-16 h-16 rounded-full bg-emerald-500/10 border-2 border-emerald-500 flex items-center justify-center text-emerald-400 mb-4 shadow-lg shadow-emerald-500/20"
        >
          <Check className="w-8 h-8 stroke-[3]" />
        </motion.div>

        <h2 className="text-2xl font-bold text-slate-100">
          {isAudio ? 'Your audio is ready' : 'Your video is ready'}
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          The file has been processed, merged, and packaged for instant download.
        </p>
      </div>

      {/* File Specs Card */}
      <div className="mt-6 p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-start gap-3.5">
        <div className="p-3 rounded-lg bg-indigo-950/60 text-indigo-400 flex-shrink-0">
          {isAudio ? <FileAudio className="w-6 h-6" /> : <FileVideo className="w-6 h-6" />}
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-medium text-slate-200 text-sm break-all leading-snug">
            {progressData.filename || 'media_output.mp4'}
          </div>
          <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-slate-400 font-mono">
            {progressData.formatted_filesize && (
              <span className="text-slate-300 font-semibold">
                Size: {progressData.formatted_filesize}
              </span>
            )}
            <span className="text-slate-600">•</span>
            <span>Format: {isAudio ? 'Audio (MP3/M4A)' : 'Video (MP4 / H.264)'}</span>
            <span className="text-slate-600">•</span>
            <span className="text-emerald-400 flex items-center gap-1">
              <ShieldCheck className="w-3 h-3" />
              <span>Verified</span>
            </span>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-6 flex flex-col sm:flex-row gap-3 items-center justify-between">
        <button
          type="button"
          onClick={onReset}
          className="w-full sm:w-auto px-4 py-3 rounded-xl text-xs font-mono text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-slate-800 flex items-center justify-center gap-1.5 transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Convert another</span>
        </button>

        {/* Primary Download Anchor */}
        <a
          href={downloadUrl}
          download={progressData.filename || true}
          className="w-full sm:w-auto flex-1 px-6 py-3.5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white shadow-xl shadow-emerald-600/25 transition-all transform active:scale-98 text-center"
        >
          <Download className="w-4 h-4" />
          <span>Save to Device</span>
        </a>
      </div>

      {/* Ephemeral Note */}
      <div className="mt-4 text-center">
        <span className="text-[11px] text-slate-400 font-mono">
          Note: Download files are temporary and will be safely purged from the server shortly after retrieval.
        </span>
      </div>
    </motion.div>
  );
};

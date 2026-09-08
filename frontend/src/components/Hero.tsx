import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface HeroProps {
  isTransformed: boolean;
  onTransitionComplete: () => void;
}

const FULL_TEXT = "Welcome to the best Youtube Downloader";

export const Hero: React.FC<HeroProps> = ({ isTransformed, onTransitionComplete }) => {
  const [displayText, setDisplayText] = useState("");
  const [isTypingDone, setIsTypingDone] = useState(false);

  useEffect(() => {
    // If already transformed, ensure text is locked to full and do not type
    if (isTransformed) {
      setDisplayText(FULL_TEXT);
      setIsTypingDone(true);
      return;
    }

    let currentIndex = 0;
    let timer: any = null;

    const step = () => {
      currentIndex++;
      if (currentIndex <= FULL_TEXT.length) {
        setDisplayText(FULL_TEXT.slice(0, currentIndex));
        const char = FULL_TEXT[currentIndex - 1];
        const delay = char === ' ' ? 60 : Math.floor(Math.random() * 20) + 25;
        timer = setTimeout(step, delay);
      } else {
        setIsTypingDone(true);
        timer = setTimeout(() => {
          onTransitionComplete();
        }, 600);
      }
    };

    // Small initial delay before typing begins
    timer = setTimeout(step, 200);

    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [isTransformed, onTransitionComplete]);

  return (
    <motion.div
      layout
      transition={{
        type: "spring",
        stiffness: 85,
        damping: 18,
        mass: 0.8,
      }}
      className={`w-full flex flex-col items-center justify-center transition-all ${
        isTransformed
          ? "pt-6 pb-2"
          : "min-h-[75vh]"
      }`}
    >
      {/* Top engine status badge (only appears once at top) */}
      <AnimatePresence>
        {isTransformed && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: 0.15 }}
            className="flex items-center gap-2 px-3 py-1 mb-2.5 rounded-full bg-indigo-950/40 border border-indigo-500/20 text-xs font-mono text-indigo-300"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>ENGINE: YT-DLP + FFMPEG</span>
            <span className="text-slate-600">/</span>
            <span className="text-slate-400">READY</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Heading - always centered, smoothly glides up and shrinks */}
      <motion.h1
        layout="position"
        className={`font-extrabold tracking-tight text-center text-slate-100 transition-all ${
          isTransformed
            ? "text-xl sm:text-2xl md:text-3xl max-w-3xl"
            : "text-3xl sm:text-5xl md:text-6xl max-w-4xl px-4"
        }`}
      >
        <span className="bg-gradient-to-b from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
          {displayText}
        </span>

        {/* Blinking cursor during typing only */}
        {!isTypingDone && (
          <motion.span
            animate={{ opacity: [1, 0] }}
            transition={{ repeat: Infinity, duration: 0.55, ease: "linear" }}
            className="inline-block ml-1.5 w-[3px] h-[0.9em] align-middle bg-indigo-400 rounded-sm"
          />
        )}
      </motion.h1>

      {/* Supporting description (fades in when moved to top) */}
      <AnimatePresence>
        {isTransformed && (
          <motion.p
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: 0.12 }}
            className="text-slate-400 text-xs sm:text-sm text-center mt-2 max-w-lg font-normal"
          >
            Direct high-bitrate media extraction with seamless server-side video & audio stream merging.
          </motion.p>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

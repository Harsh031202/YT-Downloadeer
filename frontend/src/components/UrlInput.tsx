import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Clipboard, Loader2, ArrowRight, AlertCircle } from 'lucide-react';

interface UrlInputProps {
  onAnalyze: (url: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

// Client-side quick check
const YT_REGEX = /^(https?:\/\/)?(www\.|m\.|music\.)?(youtube\.com\/(watch\?.*v=|shorts\/|live\/|embed\/)|youtu\.be\/)[a-zA-Z0-9_-]{11}/;

export const UrlInput: React.FC<UrlInputProps> = ({ onAnalyze, isLoading, disabled }) => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isFocused, setIsFocused] = useState(false);

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        setUrl(text.trim());
        setError(null);
      }
    } catch {
      // Clipboard permissions denied or unavailable
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const cleanUrl = url.trim();
    if (!cleanUrl) return;

    if (!YT_REGEX.test(cleanUrl)) {
      setError('Please enter a valid YouTube video link (e.g. youtube.com/watch?v=...)');
      return;
    }

    setError(null);
    onAnalyze(cleanUrl);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUrl(e.target.value);
    if (error) setError(null);
  };

  const isSubmitDisabled = !url.trim() || isLoading || disabled;

  return (
    <div className="w-full max-w-2xl mx-auto mt-6">
      <form onSubmit={handleSubmit} className="relative group">
        <motion.div
          animate={{
            boxShadow: isFocused
              ? '0 0 0 2px rgba(99, 102, 241, 0.4), 0 10px 25px -5px rgba(0, 0, 0, 0.5)'
              : '0 4px 20px -2px rgba(0, 0, 0, 0.4)',
          }}
          transition={{ duration: 0.2 }}
          className={`flex items-center gap-2 p-1.5 sm:p-2 rounded-xl bg-[#11131b]/90 border transition-colors ${
            error
              ? 'border-rose-500/60'
              : isFocused
              ? 'border-indigo-500/60'
              : 'border-slate-800/90 group-hover:border-slate-700/80'
          }`}
        >
          {/* Left search icon */}
          <div className="pl-3 text-slate-500">
            <Search className="w-5 h-5 transition-colors group-hover:text-slate-400" />
          </div>

          {/* URL Input */}
          <input
            type="url"
            value={url}
            onChange={handleChange}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Paste a YouTube video URL..."
            disabled={isLoading || disabled}
            className="flex-1 bg-transparent py-2.5 px-2 text-sm sm:text-base text-slate-100 placeholder-slate-500 focus:outline-none disabled:opacity-50"
            aria-label="YouTube video URL"
          />

          {/* Paste button if input is empty */}
          {!url && (
            <button
              type="button"
              onClick={handlePaste}
              disabled={isLoading || disabled}
              className="hidden sm:flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-mono text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 rounded-lg transition-colors"
              title="Paste from clipboard"
            >
              <Clipboard className="w-3.5 h-3.5" />
              <span>Paste</span>
            </button>
          )}

          {/* Analyze Button */}
          <motion.button
            type="submit"
            disabled={isSubmitDisabled}
            whileHover={isSubmitDisabled ? {} : { scale: 1.02 }}
            whileTap={isSubmitDisabled ? {} : { scale: 0.98 }}
            className={`flex items-center gap-2 px-4 sm:px-5 py-2.5 rounded-lg font-medium text-sm transition-all ${
              isSubmitDisabled
                ? 'bg-slate-800/60 text-slate-500 cursor-not-allowed border border-slate-700/30'
                : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/20 active:bg-indigo-700'
            }`}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" />
                <span>Fetching video...</span>
              </>
            ) : (
              <>
                <span>Analyze</span>
                <ArrowRight className="w-4 h-4 opacity-80" />
              </>
            )}
          </motion.button>
        </motion.div>
      </form>

      {/* Inline validation error */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-1.5 mt-2 px-3 text-xs text-rose-400 font-medium"
        >
          <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
          <span>{error}</span>
        </motion.div>
      )}
    </div>
  );
};

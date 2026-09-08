import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Clock, User, Film, Music, ChevronDown, ChevronUp } from 'lucide-react';
import { VideoInfo } from '../types';

interface VideoCardProps {
  video: VideoInfo | null;
  isLoading: boolean;
}

export const VideoCard: React.FC<VideoCardProps> = ({ video, isLoading }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [isTitleExpanded, setIsTitleExpanded] = useState(false);

  if (isLoading) {
    return (
      <div className="w-full max-w-2xl mx-auto mt-8 p-4 sm:p-5 rounded-2xl bg-[#11131b]/80 border border-slate-800/80 animate-pulse">
        <div className="flex flex-col sm:flex-row gap-4 sm:gap-5 items-start">
          {/* Thumbnail skeleton */}
          <div className="w-full sm:w-56 aspect-video bg-slate-800/60 rounded-xl" />
          {/* Content skeleton */}
          <div className="flex-1 w-full space-y-3 py-1">
            <div className="h-5 bg-slate-800/80 rounded w-3/4" />
            <div className="h-4 bg-slate-800/50 rounded w-1/2" />
            <div className="flex gap-2 pt-2">
              <div className="h-6 w-20 bg-slate-800/60 rounded-full" />
              <div className="h-6 w-24 bg-slate-800/60 rounded-full" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!video) return null;

  const isLongTitle = video.title.length > 70;

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className="w-full max-w-2xl mx-auto mt-8 p-4 sm:p-5 rounded-2xl bg-[#11131b]/80 border border-slate-800/80 backdrop-blur-sm shadow-xl shadow-black/20"
    >
      <div className="flex flex-col sm:flex-row gap-4 sm:gap-5 items-start">
        {/* Thumbnail with aspect ratio & rounded corners */}
        <div className="relative w-full sm:w-56 aspect-video rounded-xl overflow-hidden bg-slate-900 border border-slate-800 flex-shrink-0">
          {!imageLoaded && (
            <div className="absolute inset-0 bg-slate-800/60 animate-pulse" />
          )}
          <img
            src={video.thumbnail}
            alt={video.title}
            onLoad={() => setImageLoaded(true)}
            className={`w-full h-full object-cover transition-opacity duration-300 ${
              imageLoaded ? 'opacity-100' : 'opacity-0'
            }`}
          />
          {/* Duration overlay badge */}
          <div className="absolute bottom-2 right-2 px-1.5 py-0.5 rounded bg-black/80 text-[11px] font-mono font-medium text-white flex items-center gap-1 backdrop-blur-sm">
            <Clock className="w-3 h-3 text-slate-300" />
            <span>{video.formatted_duration}</span>
          </div>
        </div>

        {/* Video Details */}
        <div className="flex-1 min-w-0 flex flex-col justify-between self-stretch">
          <div>
            {/* Title with expand toggle */}
            <h2 
              className={`font-semibold text-slate-100 text-base sm:text-lg leading-snug cursor-pointer select-text ${
                !isTitleExpanded ? 'line-clamp-2' : ''
              }`}
              onClick={() => isLongTitle && setIsTitleExpanded(!isTitleExpanded)}
            >
              {video.title}
            </h2>

            {isLongTitle && (
              <button
                type="button"
                onClick={() => setIsTitleExpanded(!isTitleExpanded)}
                className="mt-1 flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
              >
                <span>{isTitleExpanded ? 'Show less' : 'Show full title'}</span>
                {isTitleExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </button>
            )}

            {/* Uploader / Channel */}
            <div className="flex items-center gap-1.5 mt-2 text-xs sm:text-sm text-slate-400">
              <User className="w-3.5 h-3.5 text-slate-500" />
              <span className="font-medium text-slate-300 truncate">{video.uploader}</span>
            </div>
          </div>

          {/* Badges: Top Video & Top Audio capabilities */}
          <div className="flex flex-wrap items-center gap-2 mt-4 pt-3 border-t border-slate-800/60">
            {video.best_video_quality && (
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-indigo-950/50 border border-indigo-500/30 text-indigo-300 text-xs font-mono">
                <Film className="w-3 h-3" />
                <span>Max Video: {video.best_video_quality}</span>
              </span>
            )}
            {video.best_audio_quality && (
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-cyan-950/50 border border-cyan-500/30 text-cyan-300 text-xs font-mono">
                <Music className="w-3 h-3" />
                <span>Max Audio: {video.best_audio_quality}</span>
              </span>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

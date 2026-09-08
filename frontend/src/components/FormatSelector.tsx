import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Film, Music, Download, Check, Info, Layers } from 'lucide-react';
import { FormatItem, VideoInfo, MediaType } from '../types';

interface FormatSelectorProps {
  video: VideoInfo;
  onStartDownload: (format: FormatItem) => void;
  isStarting: boolean;
}

export const FormatSelector: React.FC<FormatSelectorProps> = ({
  video,
  onStartDownload,
  isStarting,
}) => {
  const [activeTab, setActiveTab] = useState<MediaType>('video');
  const [selectedFormat, setSelectedFormat] = useState<FormatItem>(() => {
    // Default to best video format or first available
    return video.video_formats[0] || video.audio_formats[0];
  });

  const handleTabChange = (type: MediaType) => {
    setActiveTab(type);
    if (type === 'video' && video.video_formats.length > 0) {
      setSelectedFormat(video.video_formats[0]);
    } else if (type === 'audio' && video.audio_formats.length > 0) {
      setSelectedFormat(video.audio_formats[0]);
    }
  };

  const currentFormats = activeTab === 'video' ? video.video_formats : video.audio_formats;

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: 0.1 }}
      className="w-full max-w-2xl mx-auto mt-6"
    >
      <div className="p-5 sm:p-6 rounded-2xl bg-[#11131b]/80 border border-slate-800/80 backdrop-blur-sm shadow-xl shadow-black/20">
        
        {/* Section Header & Tabs */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
          <div>
            <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
              <Layers className="w-4 h-4 text-indigo-400" />
              <span>Select Format & Quality</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Choose your preferred media stream and resolution
            </p>
          </div>

          {/* Toggle Tabs: Video vs Audio */}
          <div className="flex items-center p-1 rounded-xl bg-slate-900/90 border border-slate-800">
            <button
              type="button"
              onClick={() => handleTabChange('video')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'video'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Film className="w-3.5 h-3.5" />
              <span>Video ({video.video_formats.length})</span>
            </button>
            <button
              type="button"
              onClick={() => handleTabChange('audio')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'audio'
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Music className="w-3.5 h-3.5" />
              <span>Audio ({video.audio_formats.length})</span>
            </button>
          </div>
        </div>

        {/* Formats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4 max-h-[300px] overflow-y-auto pr-1">
          {currentFormats.map((fmt) => {
            const isSelected = selectedFormat?.format_id === fmt.format_id;
            return (
              <motion.div
                key={fmt.format_id}
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => setSelectedFormat(fmt)}
                className={`relative flex items-center justify-between p-3.5 rounded-xl border cursor-pointer transition-all ${
                  isSelected
                    ? activeTab === 'video'
                      ? 'bg-indigo-950/40 border-indigo-500 shadow-md shadow-indigo-500/10'
                      : 'bg-cyan-950/40 border-cyan-500 shadow-md shadow-cyan-500/10'
                    : 'bg-[#141724]/60 border-slate-800 hover:border-slate-700 hover:bg-[#181c2b]/80'
                }`}
              >
                <div className="flex-1 min-w-0 pr-3">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-slate-100 text-sm">
                      {fmt.quality}
                    </span>
                    <span className="text-[11px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                      {fmt.codec}
                    </span>
                    {fmt.fps && fmt.fps > 30 && (
                      <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-indigo-900/60 text-indigo-300">
                        {fmt.fps}fps
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-slate-400 mt-1 flex items-center gap-2">
                    <span className="font-mono text-slate-300">{fmt.formatted_size}</span>
                    <span className="text-slate-600">•</span>
                    <span className="text-[11px] text-slate-400">{fmt.ext.toUpperCase()}</span>
                  </div>
                </div>

                {/* Selection Radio / Check icon */}
                <div
                  className={`w-5 h-5 rounded-full flex items-center justify-center transition-colors ${
                    isSelected
                      ? activeTab === 'video'
                        ? 'bg-indigo-600 text-white'
                        : 'bg-cyan-600 text-white'
                      : 'border border-slate-700'
                  }`}
                >
                  {isSelected && <Check className="w-3.5 h-3.5 stroke-[2.5]" />}
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Explicit Stream Explanation Box */}
        <div className="mt-4 p-3 rounded-xl bg-slate-900/70 border border-slate-800/80 flex items-start gap-2.5">
          <Info className="w-4 h-4 text-indigo-400 flex-shrink-0 mt-0.5" />
          <div className="text-xs text-slate-300 leading-relaxed">
            {activeTab === 'video' ? (
              <span>
                <strong className="text-slate-200">Server Merge:</strong> Audio will be downloaded separately and merged with this video stream into a universally playable MP4 via FFmpeg.
              </span>
            ) : (
              <span>
                <strong className="text-slate-200">Audio Only:</strong> Only the audio track will be extracted and saved in high-bitrate format.
              </span>
            )}
          </div>
        </div>

        {/* Prominent Action Button */}
        <div className="mt-5 pt-4 border-t border-slate-800/80 flex justify-end">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            disabled={isStarting || !selectedFormat}
            onClick={() => selectedFormat && onStartDownload(selectedFormat)}
            className="w-full sm:w-auto px-6 py-3 rounded-xl font-medium text-sm flex items-center justify-center gap-2 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white shadow-lg shadow-indigo-600/25 transition-all disabled:opacity-50"
          >
            <Download className="w-4 h-4" />
            <span>
              Start Download ({selectedFormat?.quality || 'Selected'})
            </span>
          </motion.button>
        </div>

      </div>
    </motion.div>
  );
};

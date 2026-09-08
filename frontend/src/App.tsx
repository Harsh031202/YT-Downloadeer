import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Hero } from './components/Hero';
import { UrlInput } from './components/UrlInput';
import { VideoCard } from './components/VideoCard';
import { FormatSelector } from './components/FormatSelector';
import { ProgressScreen } from './components/ProgressScreen';
import { SuccessScreen } from './components/SuccessScreen';
import { ErrorAlert } from './components/ErrorAlert';
import { BackgroundFx } from './components/BackgroundFx';
import { Footer } from './components/Footer';

import { analyzeVideo, startDownload, getProgress } from './api/client';
import { VideoInfo, FormatItem, JobProgress, AppPhase } from './types';

export const App: React.FC = () => {
  const [isTransformed, setIsTransformed] = useState(false);
  const [appPhase, setAppPhase] = useState<AppPhase>('initial');
  const [currentUrl, setCurrentUrl] = useState<string>('');
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null);
  const [progressData, setProgressData] = useState<JobProgress | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const pollIntervalRef = useRef<any>(null);

  // Clear polling on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, []);

  const handleAnalyze = async (url: string) => {
    setCurrentUrl(url);
    setErrorMessage(null);
    setAppPhase('analyzing');

    try {
      const data = await analyzeVideo(url);
      setVideoInfo(data);
      setAppPhase('ready');
    } catch (err: any) {
      setErrorMessage(err.message || 'Unable to retrieve video information.');
      setAppPhase('error');
    }
  };

  const handleStartDownload = async (format: FormatItem) => {
    if (!videoInfo || !currentUrl) return;

    setErrorMessage(null);
    setAppPhase('downloading');

    try {
      const { job_id } = await startDownload(
        currentUrl,
        format.format_id,
        format.type,
        format.quality
      );

      // Start progress polling
      startPolling(job_id);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to start download job.');
      setAppPhase('error');
    }
  };

  const startPolling = (jobId: string) => {
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);

    const poll = async () => {
      try {
        const data = await getProgress(jobId);
        setProgressData(data);

        if (data.status === 'complete') {
          if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
          setAppPhase('complete');
        } else if (data.status === 'error') {
          if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
          setErrorMessage(data.error || 'Download encountered an unexpected issue.');
          setAppPhase('error');
        } else if (data.status === 'merging' || data.status === 'finalizing') {
          setAppPhase('processing');
        }
      } catch (err: any) {
        // Network glitch during poll, continue polling
      }
    };

    // First immediate check
    poll();
    pollIntervalRef.current = setInterval(poll, 700);
  };

  const handleTransitionComplete = React.useCallback(() => {
    setIsTransformed(true);
  }, []);

  const handleReset = () => {
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    setVideoInfo(null);
    setProgressData(null);
    setErrorMessage(null);
    setAppPhase('initial');
  };

  return (
    <div className="relative min-h-screen flex flex-col justify-between selection:bg-indigo-500/30">
      {/* Background Graphic Grid and Radial Tints */}
      <BackgroundFx />

      {/* Main Content Area */}
      <main className={`relative z-10 flex-1 flex flex-col items-center px-4 sm:px-6 w-full max-w-4xl mx-auto transition-all ${
        isTransformed ? 'pb-16' : 'pb-0 justify-center'
      }`}>
        
        {/* Hero with typing animation + physical spring layout transition */}
        <Hero
          isTransformed={isTransformed}
          onTransitionComplete={handleTransitionComplete}
        />

        {/* Persistent URL input (fades in once Hero transition completes) */}
        <AnimatePresence>
          {isTransformed && (
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="w-full"
            >
              <UrlInput
                onAnalyze={handleAnalyze}
                isLoading={appPhase === 'analyzing'}
                disabled={appPhase === 'downloading' || appPhase === 'processing'}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error Alert Display */}
        <AnimatePresence>
          {errorMessage && (
            <ErrorAlert
              message={errorMessage}
              onRetry={() => currentUrl && handleAnalyze(currentUrl)}
              onDismiss={() => setErrorMessage(null)}
            />
          )}
        </AnimatePresence>

        {/* Video Information & Skeleton Loading */}
        <AnimatePresence>
          {(appPhase === 'analyzing' || (videoInfo && (appPhase === 'ready' || appPhase === 'downloading' || appPhase === 'processing'))) && (
            <VideoCard
              video={videoInfo}
              isLoading={appPhase === 'analyzing'}
            />
          )}
        </AnimatePresence>

        {/* Format Selection (Only visible in 'ready' state) */}
        <AnimatePresence>
          {appPhase === 'ready' && videoInfo && (
            <FormatSelector
              video={videoInfo}
              onStartDownload={handleStartDownload}
              isStarting={false}
            />
          )}
        </AnimatePresence>

        {/* Real-time Progress Interface (Downloading or Merging) */}
        <AnimatePresence>
          {(appPhase === 'downloading' || appPhase === 'processing') && progressData && (
            <ProgressScreen progressData={progressData} />
          )}
        </AnimatePresence>

        {/* Completion & Download Screen */}
        <AnimatePresence>
          {appPhase === 'complete' && progressData && (
            <SuccessScreen
              progressData={progressData}
              onReset={handleReset}
            />
          )}
        </AnimatePresence>

      </main>

      {/* Unobtrusive Legal & Compliance Footer */}
      {isTransformed && <Footer />}
    </div>
  );
};

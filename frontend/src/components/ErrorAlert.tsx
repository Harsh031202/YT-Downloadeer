import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, RefreshCw, X } from 'lucide-react';

interface ErrorAlertProps {
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({ message, onRetry, onDismiss }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="w-full max-w-2xl mx-auto mt-6 p-4 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-200 backdrop-blur-sm"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-semibold text-rose-100">Unable to complete request</h4>
            <p className="text-xs text-rose-300/90 mt-1 leading-relaxed">{message}</p>
            {onRetry && (
              <button
                type="button"
                onClick={onRetry}
                className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-900/50 hover:bg-rose-900/80 text-rose-200 text-xs font-medium border border-rose-700/40 transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Try Again</span>
              </button>
            )}
          </div>
        </div>

        {onDismiss && (
          <button
            type="button"
            onClick={onDismiss}
            className="text-rose-400 hover:text-rose-200 p-1 transition-colors"
            title="Dismiss error"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </motion.div>
  );
};

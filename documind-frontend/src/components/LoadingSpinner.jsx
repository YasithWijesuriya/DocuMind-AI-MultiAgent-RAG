import React from 'react';

export default function LoadingSpinner({ message = 'Processing...' }) {
  return (
    <div className="flex items-center justify-center gap-4">
      <div className="relative w-8 h-8">
        {/* Outer rotating ring */}
        <div className="absolute inset-0 border-2 border-transparent border-t-emerald-400 border-r-cyan-400 rounded-full animate-spin" />
        
        {/* Inner rotating ring (reverse) */}
        <div className="absolute inset-2 border-2 border-transparent border-b-emerald-400 border-l-cyan-400 rounded-full animate-spin" style={{animationDirection: 'reverse', animationDuration: '1.5s'}} />
        
        {/* Center dot */}
        <div className="absolute inset-3 bg-gradient-to-r from-emerald-400 to-cyan-400 rounded-full animate-pulse" />
      </div>
      <div className="flex flex-col gap-1">
        <span className="text-sm font-semibold text-emerald-300">{message}</span>
        <div className="flex gap-1">
          <span className="w-1 h-1 bg-emerald-400 rounded-full animate-bounce" style={{animationDelay: '0s'}} />
          <span className="w-1 h-1 bg-cyan-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}} />
          <span className="w-1 h-1 bg-emerald-400 rounded-full animate-bounce" style={{animationDelay: '0.4s'}} />
        </div>
      </div>
    </div>
  );
}

import { Zap, Globe, Brain } from 'lucide-react';

export default function Header({ topic }: { topic?: string }) {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 glass border-b border-slate-700/50">
      <div className="max-w-screen-2xl mx-auto px-6 h-14 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-indigo-600">
            <Zap size={16} className="text-white" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-white font-bold tracking-wider text-lg">CLARION</span>
            <span className="text-slate-400 text-xs font-medium hidden sm:block">
              Beyond the Headline
            </span>
          </div>
        </div>

        {/* Active topic pill */}
        {topic && (
          <div className="flex items-center gap-2 bg-indigo-900/40 border border-indigo-700/50 px-3 py-1 rounded-full">
            <Brain size={12} className="text-indigo-400" />
            <span className="text-indigo-300 text-xs font-medium truncate max-w-64">{topic}</span>
          </div>
        )}

        {/* Status */}
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-slate-400 text-xs hidden sm:block">Backend Live</span>
          <Globe size={14} className="text-slate-500 ml-1" />
        </div>
      </div>
    </header>
  );
}

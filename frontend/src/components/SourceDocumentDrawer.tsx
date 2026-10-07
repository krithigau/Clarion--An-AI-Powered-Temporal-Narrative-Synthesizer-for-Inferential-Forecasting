import { useState, useEffect, useRef } from 'react';
import { X, ExternalLink, Search, BookOpen } from 'lucide-react';
import type { RawArticle } from '../types/clarion';

interface Props {
  articles: RawArticle[];
  onClose: () => void;
}

export default function SourceDocumentDrawer({ articles, onClose }: Props) {
  const [query, setQuery] = useState('');
  const drawerRef = useRef<HTMLDivElement>(null);

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  // Prevent background scroll
  useEffect(() => { document.body.style.overflow = 'hidden'; return () => { document.body.style.overflow = ''; }; }, []);

  const filtered = articles.filter(a =>
    !query || a.title.toLowerCase().includes(query.toLowerCase()) ||
    a.publisher.toLowerCase().includes(query.toLowerCase())
  );

  function sentimentColor(score: number) {
    return score < -0.2 ? '#f87171' : score > 0.2 ? '#34d399' : '#94a3b8';
  }

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm" onClick={onClose} />

      {/* Drawer */}
      <div
        ref={drawerRef}
        className="fixed right-0 top-0 bottom-0 z-50 w-full max-w-md glass border-l border-slate-700/60 flex flex-col shadow-2xl"
        style={{ animation: 'slideIn 0.25s ease' }}
      >
        <style>{`@keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }`}</style>

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-700/50">
          <div className="flex items-center gap-2">
            <BookOpen size={15} className="text-indigo-400" />
            <h3 className="text-white font-semibold text-sm">Source Articles</h3>
            <span className="ml-1 bg-slate-700 text-slate-300 text-xs px-2 py-0.5 rounded-full">{articles.length}</span>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
            <X size={18} />
          </button>
        </div>

        {/* Search */}
        <div className="px-5 py-3 border-b border-slate-800">
          <div className="relative">
            <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Filter articles…"
              className="w-full bg-slate-800/60 text-white text-xs placeholder-slate-500 pl-8 pr-3 py-2 rounded-lg border border-slate-700/50 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        {/* Article list */}
        <div className="flex-1 overflow-y-auto px-5 py-3 space-y-3">
          {filtered.map((art, i) => (
            <div key={art.id ?? i} className="glass rounded-xl p-3 border border-slate-700/40 hover:border-slate-600/60 transition-all">
              <div className="flex items-start gap-2 justify-between mb-1">
                <p className="text-white text-xs font-medium leading-snug flex-1">{art.title}</p>
                {art.url && art.url !== '#' && (
                  <a href={art.url} target="_blank" rel="noreferrer" className="text-slate-500 hover:text-indigo-400 flex-shrink-0">
                    <ExternalLink size={12} />
                  </a>
                )}
              </div>
              <div className="flex flex-wrap items-center gap-2 mt-1">
                <span className="text-[10px] text-indigo-400 bg-indigo-900/30 px-2 py-0.5 rounded-full">{art.publisher}</span>
                <span className="text-[10px] text-slate-500 font-mono">{art.published_at?.slice(0, 10)}</span>
                {art.reach_score !== undefined && (
                  <span className="text-[10px] text-slate-500">Reach: {(art.reach_score * 100).toFixed(0)}%</span>
                )}
              </div>
              {art.summary && (
                <p className="text-[11px] text-slate-400 mt-1.5 leading-relaxed line-clamp-2">{art.summary}</p>
              )}
              {art.syndicated_publishers?.length > 0 && (
                <p className="text-[10px] text-slate-600 mt-1">
                  Also in: {art.syndicated_publishers.slice(0, 3).join(', ')}
                </p>
              )}
            </div>
          ))}
          {filtered.length === 0 && (
            <p className="text-slate-500 text-xs text-center py-8">No articles match your filter.</p>
          )}
        </div>
      </div>
    </>
  );
}

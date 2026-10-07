import { useState, type FormEvent } from 'react';
import { Search, Loader2, Sparkles } from 'lucide-react';

const SUGGESTIONS = [
  'NEET Exam Controversy',
  'Farm Laws & Agitation',
  'Silicon Valley Bank Collapse',
  'AI Copyright & Fair Use Battles',
];

interface Props {
  onSubmit: (topic: string) => void;
  loading: boolean;
}

export default function SearchBar({ onSubmit, loading }: Props) {
  const [value, setValue] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (trimmed && !loading) onSubmit(trimmed);
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <form onSubmit={handleSubmit} className="relative group">
        <div className="absolute inset-0 rounded-2xl bg-indigo-600/20 blur-xl group-focus-within:bg-indigo-500/30 transition-all duration-500" />
        <div className="relative flex items-center glass rounded-2xl border border-slate-600/60 group-focus-within:border-indigo-500/70 transition-colors overflow-hidden">
          <Search size={18} className="absolute left-5 text-slate-400 pointer-events-none" />
          <input
            type="text"
            value={value}
            onChange={e => setValue(e.target.value)}
            placeholder="Enter any news topic to investigate…"
            disabled={loading}
            className="w-full bg-transparent text-white placeholder-slate-500 pl-12 pr-4 py-4 text-base focus:outline-none disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !value.trim()}
            className="shrink-0 mr-2 flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-semibold px-5 py-2.5 rounded-xl transition-colors"
          >
            {loading ? (
              <><Loader2 size={15} className="animate-spin" /> Analyzing…</>
            ) : (
              <><Sparkles size={15} /> Analyze</>
            )}
          </button>
        </div>
      </form>

      {/* Quick suggestions */}
      <div className="flex flex-wrap items-center gap-2 mt-4 justify-center">
        <span className="text-slate-500 text-xs">Try:</span>
        {SUGGESTIONS.map(s => (
          <button
            key={s}
            onClick={() => { setValue(s); if (!loading) onSubmit(s); }}
            disabled={loading}
            className="text-xs text-indigo-400 hover:text-indigo-300 border border-indigo-800/50 hover:border-indigo-600/60 bg-indigo-950/40 hover:bg-indigo-900/40 px-3 py-1 rounded-full transition-all disabled:opacity-40"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}

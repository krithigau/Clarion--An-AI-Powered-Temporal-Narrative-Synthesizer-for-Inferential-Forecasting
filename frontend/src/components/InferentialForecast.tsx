import type { InferentialForecast, HistoricalPrecedent } from '../types/clarion';

function ProbabilityBar({ pct }: { pct: number }) {
  const color =
    pct >= 75 ? '#22d3ee'
    : pct >= 55 ? '#818cf8'
    : '#94a3b8';
  return (
    <div className="flex items-center gap-3 mt-2">
      <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
        <div
          className="prob-bar h-full rounded-full"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
      <span className="text-sm font-bold font-mono" style={{ color }}>{pct}%</span>
    </div>
  );
}

interface Props {
  forecasts: InferentialForecast[];
  precedents: HistoricalPrecedent[];
}

export default function InferentialForecastPanel({ forecasts, precedents }: Props) {
  return (
    <div className="space-y-4">
      {/* Forecast cards */}
      <div className="grid gap-3">
        {forecasts.map((fc, i) => (
          <div
            key={fc.id ?? i}
            className="glass rounded-xl p-4 border border-slate-700/50 hover:border-indigo-600/40 transition-all fade-up"
            style={{ animationDelay: `${i * 80}ms` }}
          >
            <div className="flex items-start justify-between gap-2 mb-1">
              <p className="text-white text-sm font-semibold leading-snug flex-1">{fc.implication}</p>
              <span className="text-[10px] text-slate-400 font-mono shrink-0 mt-0.5">{fc.timeframe}</span>
            </div>
            <ProbabilityBar pct={fc.probability_pct} />
            <div className="mt-2.5 flex flex-wrap gap-3 text-[11px] text-slate-400">
              <span className="bg-slate-800/60 px-2 py-0.5 rounded-full">
                📚 {fc.matched_precedent}
              </span>
            </div>
            <p className="mt-2 text-[11px] text-slate-500 leading-relaxed">{fc.causal_rationale}</p>
          </div>
        ))}
      </div>

      {/* Historical precedents matched */}
      {precedents.length > 0 && (
        <div className="mt-6">
          <h4 className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-3">
            ChromaDB Precedents Matched
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {precedents.map((pr, i) => (
              <div key={i} className="glass border border-slate-700/40 rounded-xl p-3 fade-up" style={{ animationDelay: `${i * 60}ms` }}>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-indigo-400 font-mono text-xs font-bold">{pr.year}</span>
                  <span className="w-1 h-1 bg-slate-600 rounded-full" />
                  <span className="text-emerald-400 text-[10px] font-semibold">
                    {Math.round(pr.similarity_score * 100)}% match
                  </span>
                </div>
                <p className="text-white text-xs font-medium leading-snug">{pr.title}</p>
                <p className="text-slate-400 text-[11px] mt-1 line-clamp-2">{pr.trajectory_summary}</p>
                <p className="text-amber-400/80 text-[10px] mt-1.5 line-clamp-1">
                  Resolution: {pr.ultimate_resolution}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

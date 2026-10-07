import type { NarrativePhase } from '../types/clarion';

const PHASE_CONFIG: Record<string, { color: string; icon: string; bg: string }> = {
  Origin:           { color: '#818cf8', icon: '🌱', bg: 'bg-indigo-900/20 border-indigo-700/40' },
  Escalation:       { color: '#fb923c', icon: '📈', bg: 'bg-orange-900/20 border-orange-700/40' },
  Peak:             { color: '#f87171', icon: '🔥', bg: 'bg-rose-900/20 border-rose-700/40' },
  'Current State':  { color: '#34d399', icon: '🎯', bg: 'bg-emerald-900/20 border-emerald-700/40' },
  'Projected Future': { color: '#a78bfa', icon: '🔮', bg: 'bg-violet-900/20 border-violet-700/40' },
};

interface Props {
  phases: NarrativePhase[];
}

function SentimentBadge({ score }: { score: number }) {
  const pct = Math.abs(score) * 100;
  const label = score < -0.3 ? 'Negative' : score > 0.3 ? 'Positive' : 'Neutral';
  const color = score < -0.3 ? 'text-rose-400' : score > 0.3 ? 'text-emerald-400' : 'text-amber-400';
  return (
    <span className={`text-[10px] font-medium ${color}`}>
      {label} ({score > 0 ? '+' : ''}{score.toFixed(2)} / {pct.toFixed(0)}% intensity)
    </span>
  );
}

export default function NarrativeArcTimeline({ phases }: Props) {
  return (
    <div className="space-y-1">
      {/* Progress bar across top */}
      <div className="flex h-1.5 rounded-full overflow-hidden mb-6">
        {phases.map((p, i) => {
          const cfg = PHASE_CONFIG[p.phase] ?? PHASE_CONFIG['Origin'];
          return (
            <div
              key={i}
              className="transition-all duration-700"
              style={{ flex: 1, backgroundColor: cfg.color, opacity: i < phases.length - 1 ? 0.85 : 0.5 }}
            />
          );
        })}
      </div>

      <div className="relative">
        {/* Vertical spine */}
        <div className="absolute left-[22px] top-4 bottom-4 w-0.5 bg-gradient-to-b from-indigo-600/50 via-rose-600/30 to-violet-600/50 rounded-full" />

        <div className="space-y-5">
          {phases.map((phase, idx) => {
            const cfg = PHASE_CONFIG[phase.phase] ?? PHASE_CONFIG['Origin'];
            return (
              <div key={idx} className="flex gap-4 items-start fade-up" style={{ animationDelay: `${idx * 80}ms` }}>
                {/* Icon bubble */}
                <div
                  className="shrink-0 w-11 h-11 rounded-full flex items-center justify-center text-xl z-10 border-2"
                  style={{ borderColor: cfg.color + '70', backgroundColor: cfg.color + '22' }}
                >
                  {cfg.icon}
                </div>

                {/* Card */}
                <div className={`flex-1 rounded-xl border p-4 ${cfg.bg} transition-all hover:scale-[1.01]`}>
                  <div className="flex flex-wrap items-start gap-2 justify-between mb-1">
                    <div>
                      <span className="text-[10px] font-semibold uppercase tracking-widest" style={{ color: cfg.color }}>
                        {idx + 1}. {phase.phase}
                      </span>
                      <h4 className="text-white font-semibold text-sm mt-0.5">{phase.headline}</h4>
                    </div>
                    <div className="text-right shrink-0">
                      <span className="text-[10px] text-slate-400 font-mono">{phase.date_range}</span>
                      <div className="mt-0.5">
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                          phase.significance_level === 'critical'
                            ? 'bg-rose-900/40 text-rose-300'
                            : phase.significance_level === 'high'
                              ? 'bg-amber-900/40 text-amber-300'
                              : 'bg-slate-800 text-slate-400'
                        }`}>
                          {phase.significance_level?.toUpperCase()}
                        </span>
                      </div>
                    </div>
                  </div>

                  <p className="text-slate-300 text-xs leading-relaxed mb-2">{phase.summary}</p>
                  <SentimentBadge score={phase.dominant_sentiment} />

                  {phase.key_events.length > 0 && (
                    <ul className="mt-2 space-y-1">
                      {phase.key_events.map((ev, i) => (
                        <li key={i} className="text-[11px] text-slate-400 flex gap-1.5">
                          <span className="text-slate-600 shrink-0 mt-0.5">•</span>
                          <span>{ev}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

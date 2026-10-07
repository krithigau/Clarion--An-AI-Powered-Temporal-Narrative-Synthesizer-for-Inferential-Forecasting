import type { CrossSourceBiasReport, OutletBiasProfile } from '../types/clarion';

const OUTLET_COLORS: Record<string, string> = {
  NDTV: '#22d3ee',
  'Republic TV': '#f87171',
  'The Hindu': '#34d399',
  'Indian Express': '#fb923c',
};

function BiasBar({ score, label }: { score: number; label: string }) {
  // score is -1..+1; map to 0..100% with center at 50
  const pct = ((score + 1) / 2) * 100;
  const color = score < -0.3 ? '#f87171' : score > 0.3 ? '#34d399' : '#fbbf24';
  return (
    <div className="flex items-center gap-2 text-xs mb-1">
      <span className="w-24 text-slate-400 shrink-0">{label}</span>
      <div className="relative flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
        {/* Center marker */}
        <div className="absolute left-1/2 top-0 w-0.5 h-full bg-slate-600 z-10" />
        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
      <span className="w-10 text-right font-mono" style={{ color }}>
        {score > 0 ? '+' : ''}{score.toFixed(2)}
      </span>
    </div>
  );
}

function OutletCard({ outlet }: { outlet: OutletBiasProfile }) {
  const color = OUTLET_COLORS[outlet.outlet] ?? '#818cf8';
  const biasWidth = Math.abs(outlet.bias_index) * 100;
  return (
    <div className="glass rounded-xl border border-slate-700/50 p-4 hover:border-slate-600/60 transition-all">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-bold text-sm" style={{ color }}>{outlet.outlet}</h4>
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-slate-400">Bias index</span>
          <div className="flex items-center gap-1">
            <div className="w-12 h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full rounded-full" style={{ width: `${biasWidth}%`, backgroundColor: color }} />
            </div>
            <span className="text-[10px] font-mono" style={{ color }}>{outlet.bias_index.toFixed(2)}</span>
          </div>
        </div>
      </div>

      <div className="text-[11px] text-slate-300 mb-2 leading-relaxed">
        <span className="text-slate-500">Focus: </span>{outlet.framing_focus}
      </div>

      <BiasBar score={outlet.sentiment_score} label="Sentiment" />

      <div className="mt-3 grid grid-cols-2 gap-2">
        <div>
          <p className="text-[9px] font-semibold uppercase tracking-widest text-emerald-500/80 mb-1">Emphasized</p>
          {outlet.key_emphases.slice(0, 2).map((e, i) => (
            <p key={i} className="text-[10px] text-slate-400 flex gap-1 mb-0.5">
              <span className="text-emerald-600">▲</span>{e}
            </p>
          ))}
        </div>
        <div>
          <p className="text-[9px] font-semibold uppercase tracking-widest text-rose-500/80 mb-1">Omitted</p>
          {outlet.key_omissions.slice(0, 2).map((o, i) => (
            <p key={i} className="text-[10px] text-slate-400 flex gap-1 mb-0.5">
              <span className="text-rose-600">▼</span>{o}
            </p>
          ))}
        </div>
      </div>
    </div>
  );
}

interface Props {
  report: CrossSourceBiasReport;
}

export default function CrossSourceBias({ report }: Props) {
  const divPct = Math.round(report.divergence_score * 100);
  const divColor = divPct > 60 ? '#f87171' : divPct > 35 ? '#fbbf24' : '#34d399';

  return (
    <div className="space-y-5">
      {/* Divergence score header */}
      <div className="flex items-center justify-between p-4 rounded-xl border border-slate-700/50 bg-slate-900/50">
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-widest mb-0.5">Overall Framing Divergence</p>
          <p className="text-xs text-slate-500">Across {report.outlets.length} major outlets</p>
        </div>
        <div className="text-right">
          <p className="text-3xl font-bold font-mono" style={{ color: divColor }}>{divPct}%</p>
          <p className="text-[10px]" style={{ color: divColor }}>
            {divPct > 60 ? 'HIGH divergence' : divPct > 35 ? 'MODERATE divergence' : 'LOW divergence'}
          </p>
        </div>
      </div>

      {/* Outlet cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {report.outlets.map((outlet, i) => (
          <div key={i} className="fade-up" style={{ animationDelay: `${i * 70}ms` }}>
            <OutletCard outlet={outlet} />
          </div>
        ))}
      </div>

      {/* Objective middle ground */}
      <div className="glass rounded-xl p-4 border border-violet-700/30 bg-violet-950/20">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-violet-400 text-sm">⚖️</span>
          <h4 className="text-violet-300 text-xs font-semibold uppercase tracking-widest">
            CLARION Objective Synthesis
          </h4>
        </div>
        <p className="text-slate-300 text-sm leading-relaxed">{report.objective_middle_ground}</p>
      </div>
    </div>
  );
}

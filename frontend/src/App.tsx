import { useState, useRef, useCallback } from 'react';
import { BookOpen, Network, Clock, TrendingUp, BarChart3, FileText, ChevronDown } from 'lucide-react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import PipelineTracker from './components/PipelineTracker';
import KnowledgeGraph from './components/KnowledgeGraph';
import NarrativeArcTimeline from './components/NarrativeArcTimeline';
import InferentialForecastPanel from './components/InferentialForecast';
import CrossSourceBias from './components/CrossSourceBias';
import SourceDocumentDrawer from './components/SourceDocumentDrawer';
import { analyzeTopic } from './api/client';
import type { ClarionReport, RawArticle } from './types/clarion';

type Tab = 'graph' | 'timeline' | 'forecast' | 'bias';

const TABS: { id: Tab; label: string; icon: React.ReactNode }[] = [
  { id: 'graph',    label: 'Knowledge Graph',   icon: <Network size={14} /> },
  { id: 'timeline', label: 'Narrative Arc',      icon: <Clock size={14} /> },
  { id: 'forecast', label: 'Forecasting',        icon: <TrendingUp size={14} /> },
  { id: 'bias',     label: 'Bias Matrix',        icon: <BarChart3 size={14} /> },
];

// Simulated harvested articles accumulate in memory during analysis
// (Agent 1 output is not directly returned by /api/analyze in current backend,
//  so we reconstruct from canonical events' source info)
function reconstructArticles(report: ClarionReport): RawArticle[] {
  const seen = new Set<string>();
  const arts: RawArticle[] = [];
  report.narrative_arc.forEach(phase => {
    phase.key_events.forEach((ev, i) => {
      const id = `${phase.phase}-${i}`;
      if (!seen.has(id)) {
        seen.add(id);
        arts.push({
          id,
          title: ev,
          publisher: 'Various',
          published_at: phase.date_range.split(' to ')[0] ?? '',
          url: '#',
          content: ev,
          summary: ev,
          reach_score: 0.5,
          syndicated_publishers: [],
          is_duplicate_merged: false,
        });
      }
    });
  });
  return arts;
}

export default function App() {
  const [report, setReport] = useState<ClarionReport | null>(null);
  const [articles, setArticles] = useState<RawArticle[]>([]);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>('graph');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [currentTopic, setCurrentTopic] = useState('');
  const resultsRef = useRef<HTMLDivElement>(null);

  const handleAnalyze = useCallback(async (topic: string) => {
    setLoading(true);
    setError(null);
    setReport(null);
    setStep(1);
    setCurrentTopic(topic);
    setActiveTab('graph');

    // Simulate per-agent progress (each ~1.5s apart in offline mode)
    const timers = [1500, 3000, 4500].map((ms, i) =>
      setTimeout(() => setStep(i + 2), ms)
    );

    try {
      const data = await analyzeTopic(topic);
      timers.forEach(clearTimeout);
      setStep(5);
      setReport(data);
      setArticles(reconstructArticles(data));
      setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 200);
    } catch (err) {
      timers.forEach(clearTimeout);
      setError(err instanceof Error ? err.message : 'Unexpected error. Is the backend running?');
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <div className="min-h-screen bg-[#050a14]">
      <Header topic={currentTopic || undefined} />

      {/* Hero search section */}
      <section className="pt-24 pb-10 px-6">
        <div className="max-w-screen-xl mx-auto text-center mb-10">
          <h1 className="text-4xl sm:text-5xl font-bold text-white mb-3 tracking-tight">
            Temporal Narrative<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-violet-400">
              Intelligence Engine
            </span>
          </h1>
          <p className="text-slate-400 text-base max-w-xl mx-auto">
            4-agent AI pipeline that harvests news, builds causal knowledge graphs,
            and forecasts future implications from any topic.
          </p>
        </div>

        <SearchBar onSubmit={handleAnalyze} loading={loading} />
      </section>

      {/* Pipeline tracker */}
      <div className="px-6 pb-8 max-w-screen-xl mx-auto">
        <PipelineTracker currentStep={step} error={error} />
      </div>

      {/* Results */}
      {report && (
        <div ref={resultsRef} className="px-6 pb-16 max-w-screen-xl mx-auto fade-up space-y-6">

          {/* Executive summary card */}
          <div className="glass rounded-2xl p-6 border border-indigo-700/30">
            <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
              <div>
                <p className="text-xs uppercase tracking-widest text-indigo-400 font-semibold mb-1">
                  CLARION Intelligence Dossier
                </p>
                <h2 className="text-white text-xl font-bold">{report.topic}</h2>
                <p className="text-slate-400 text-xs mt-1">
                  Generated {new Date(report.synthesized_at).toLocaleString()} ·{' '}
                  {report.total_pipeline_duration_ms?.toFixed(0)}ms pipeline time
                </p>
              </div>

              {/* Stats row */}
              <div className="flex flex-wrap gap-4">
                {[
                  { label: 'Articles', value: report.article_corpus_count },
                  { label: 'Events',   value: report.canonical_events_count },
                  { label: 'Nodes',    value: report.ontology_nodes_count },
                  { label: 'Edges',    value: report.ontology_edges_count },
                ].map(s => (
                  <div key={s.label} className="text-center">
                    <p className="text-2xl font-bold text-white font-mono">{s.value}</p>
                    <p className="text-xs text-slate-500">{s.label}</p>
                  </div>
                ))}
              </div>
            </div>
            <p className="text-slate-300 text-sm leading-relaxed">{report.executive_summary}</p>

            {/* Source documents button */}
            <button
              onClick={() => setDrawerOpen(true)}
              className="mt-4 flex items-center gap-2 text-xs text-indigo-400 hover:text-indigo-300 border border-indigo-800/50 hover:border-indigo-600/50 bg-indigo-950/40 px-3 py-1.5 rounded-full transition-all"
            >
              <BookOpen size={12} /> View {articles.length} Source Articles
            </button>
          </div>

          {/* Tab navigation */}
          <div className="flex gap-1 glass rounded-xl p-1 border border-slate-700/40 w-fit">
            {TABS.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-indigo-600 text-white shadow-lg'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                }`}
              >
                {tab.icon}
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            ))}
          </div>

          {/* Tab panels */}
          <div className="glass rounded-2xl border border-slate-700/40 overflow-hidden">

            {/* Knowledge Graph */}
            {activeTab === 'graph' && (
              <div className="p-1">
                <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700/40">
                  <div>
                    <h3 className="text-white font-semibold text-sm">Causal Knowledge Graph</h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {report.ontology_nodes_count} nodes · {report.ontology_edges_count} edges · click a node to inspect
                    </p>
                  </div>
                  <span className="text-xs text-slate-500 font-mono">
                    Density: {report.graph?.density?.toFixed(4) ?? 'N/A'}
                  </span>
                </div>
                <div style={{ height: '560px' }}>
                  {report.graph ? (
                    <KnowledgeGraph graph={report.graph} />
                  ) : (
                    <div className="flex items-center justify-center h-full text-slate-500 text-sm">
                      Graph data not available. Ensure the backend returns <code className="mx-1 text-xs bg-slate-800 px-1 rounded">graph</code> in the report.
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Narrative Arc */}
            {activeTab === 'timeline' && (
              <div className="p-6">
                <div className="flex items-center justify-between mb-5">
                  <h3 className="text-white font-semibold text-sm">Narrative Arc — 5 Phase Timeline</h3>
                  <span className="text-xs text-slate-500">{report.narrative_arc.length} phases identified</span>
                </div>
                <NarrativeArcTimeline phases={report.narrative_arc} />
              </div>
            )}

            {/* Inferential Forecasting */}
            {activeTab === 'forecast' && (
              <div className="p-6">
                <div className="flex items-center justify-between mb-5">
                  <h3 className="text-white font-semibold text-sm">Inferential Forecast — ChromaDB RAG</h3>
                  <span className="text-xs text-slate-500">
                    {report.historical_precedents_matched.length} precedents matched
                  </span>
                </div>
                <InferentialForecastPanel
                  forecasts={report.forecasts}
                  precedents={report.historical_precedents_matched}
                />
              </div>
            )}

            {/* Cross-Source Bias */}
            {activeTab === 'bias' && (
              <div className="p-6">
                <div className="flex items-center justify-between mb-5">
                  <h3 className="text-white font-semibold text-sm">Cross-Source Bias & Divergence Matrix</h3>
                </div>
                <CrossSourceBias report={report.bias_analysis} />
              </div>
            )}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!report && !loading && step === 0 && (
        <div className="max-w-screen-xl mx-auto px-6 py-12 text-center text-slate-600 text-sm">
          <div className="text-6xl mb-4">🔭</div>
          <p>Enter any topic above to generate your intelligence dossier.</p>
        </div>
      )}

      {/* Source drawer */}
      {drawerOpen && (
        <SourceDocumentDrawer articles={articles} onClose={() => setDrawerOpen(false)} />
      )}
    </div>
  );
}

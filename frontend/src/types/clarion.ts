// All TypeScript types mirroring backend Pydantic schemas

export type EntityType = 'Person' | 'Organization' | 'Policy' | 'Location' | 'Event';
export type NodeType = 'NewsEvent' | 'Person' | 'Organization' | 'Policy' | 'Location';
export type CausalRelationType = 'CAUSED' | 'TRIGGERED' | 'ESCALATED' | 'INFLUENCED' | 'RESOLVED' | 'INVOLVED';
export type NarrativePhaseType = 'Origin' | 'Escalation' | 'Peak' | 'Current State' | 'Projected Future';

export interface NamedEntity {
  name: string;
  type: EntityType;
  mention_count: number;
}

export interface RawArticle {
  id: string;
  title: string;
  publisher: string;
  published_at: string;
  url: string;
  content: string;
  summary?: string;
  reach_score: number;
  syndicated_publishers: string[];
  is_duplicate_merged: boolean;
}

export interface CanonicalNewsEvent {
  id: string;
  title: string;
  date: string;
  location: string;
  description: string;
  entities: NamedEntity[];
  sentiment_score: number;
  significance_score: number;
  source_articles: string[];
  source_publishers: string[];
  source_urls: string[];
  coverage_count: number;
}

export interface GraphNode {
  id: string;
  label: string;
  node_type: NodeType;
  date?: string;
  sentiment?: number;
  significance?: number;
  properties: Record<string, unknown>;
  // D3 simulation fields added at runtime
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
}

export interface GraphEdge {
  source: string;
  target: string;
  relation: CausalRelationType;
  confidence: number;
  reasoning: string;
}

export interface OntologyGraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  node_count: number;
  edge_count: number;
  causal_edges_count: number;
  density: number;
}

export interface NarrativePhase {
  phase: NarrativePhaseType;
  date_range: string;
  headline: string;
  summary: string;
  key_events: string[];
  dominant_sentiment: number;
  significance_level: string;
}

export interface HistoricalPrecedent {
  case_id: string;
  title: string;
  year: number;
  domain: string;
  similarity_score: number;
  trajectory_summary: string;
  ultimate_resolution: string;
}

export interface InferentialForecast {
  id: string;
  implication: string;
  probability_pct: number;
  confidence_score: number;
  timeframe: string;
  matched_precedent: string;
  causal_rationale: string;
}

export interface OutletBiasProfile {
  outlet: string;
  framing_focus: string;
  key_emphases: string[];
  key_omissions: string[];
  sentiment_score: number;
  bias_index: number;
  article_count: number;
}

export interface CrossSourceBiasReport {
  outlets: OutletBiasProfile[];
  divergence_score: number;
  objective_middle_ground: string;
}

export interface ClarionReport {
  topic: string;
  synthesized_at: string;
  article_corpus_count: number;
  canonical_events_count: number;
  ontology_nodes_count: number;
  ontology_edges_count: number;
  narrative_arc: NarrativePhase[];
  forecasts: InferentialForecast[];
  historical_precedents_matched: HistoricalPrecedent[];
  bias_analysis: CrossSourceBiasReport;
  executive_summary: string;
  total_pipeline_duration_ms: number;
  // Included separately but attached for graph rendering
  graph?: OntologyGraphData;
}

export type AgentStep = {
  id: number;
  name: string;
  description: string;
  status: 'idle' | 'running' | 'done' | 'error';
};

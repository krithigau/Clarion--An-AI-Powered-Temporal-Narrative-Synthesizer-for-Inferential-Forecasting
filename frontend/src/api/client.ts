import type { ClarionReport, OntologyGraphData } from '../types/clarion';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export async function analyzeTopic(topic: string): Promise<ClarionReport> {
  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, max_articles: 25 }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? 'Backend error');
  }
  return res.json();
}

export async function buildOntology(topic: string): Promise<OntologyGraphData> {
  const res = await fetch(`${API_BASE}/api/pipeline/harvest-extract-ontology`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, max_articles: 25 }),
  });
  if (!res.ok) throw new Error('Ontology pipeline failed');
  const data = await res.json();
  return data.graph as OntologyGraphData;
}

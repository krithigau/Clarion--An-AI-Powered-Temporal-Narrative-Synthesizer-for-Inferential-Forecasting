import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { X, ExternalLink, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import type { OntologyGraphData, GraphNode, GraphEdge } from '../types/clarion';

// Color palette keyed by node type
const NODE_COLORS: Record<string, string> = {
  NewsEvent: '#f59e0b',
  Person: '#22d3ee',
  Organization: '#a78bfa',
  Policy: '#34d399',
  Location: '#fb7185',
};

const EDGE_COLORS: Record<string, string> = {
  CAUSED: '#f87171',
  TRIGGERED: '#fb923c',
  ESCALATED: '#fbbf24',
  INFLUENCED: '#818cf8',
  RESOLVED: '#34d399',
  INVOLVED: '#334155',
};

interface D3Node extends GraphNode {
  x: number;
  y: number;
  vx: number;
  vy: number;
}

interface D3Link {
  source: D3Node;
  target: D3Node;
  relation: string;
  confidence: number;
  reasoning: string;
}

interface InspectPanel {
  node: D3Node;
}

interface Props {
  graph: OntologyGraphData;
}

export default function KnowledgeGraph({ graph }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [inspect, setInspect] = useState<InspectPanel | null>(null);
  const [filterType, setFilterType] = useState<string | null>(null);
  const nodeTypes = [...new Set(graph.nodes.map(n => n.node_type))];

  useEffect(() => {
    if (!svgRef.current || !graph.nodes.length) return;
    const el = svgRef.current;
    const width = el.clientWidth || 900;
    const height = el.clientHeight || 500;

    d3.select(el).selectAll('*').remove();

    const svg = d3.select(el)
      .attr('viewBox', `0 0 ${width} ${height}`)
      .attr('preserveAspectRatio', 'xMidYMid meet');

    // Zoom & pan
    const g = svg.append('g');
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.15, 4])
      .on('zoom', ev => g.attr('transform', ev.transform));
    svg.call(zoom);

    // Arrow markers for each relation type
    const defs = svg.append('defs');
    Object.entries(EDGE_COLORS).forEach(([rel, color]) => {
      defs.append('marker')
        .attr('id', `arrow-${rel}`)
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 20)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', color)
        .attr('opacity', 0.85);
    });

    // Filter visible nodes
    const visibleNodes: D3Node[] = (
      filterType
        ? graph.nodes.filter(n => n.node_type === filterType)
        : graph.nodes
    ).map(n => ({ ...n, x: width / 2, y: height / 2, vx: 0, vy: 0 }));

    const visibleIds = new Set(visibleNodes.map(n => n.id));
    const visibleEdges = graph.edges.filter(
      e => visibleIds.has(e.source) && visibleIds.has(e.target) && e.relation !== 'INVOLVED'
    );

    // Force simulation
    const sim = d3.forceSimulation<D3Node>(visibleNodes)
      .force('link', d3.forceLink<D3Node, D3Link>(
        visibleEdges.map(e => ({
          source: e.source,
          target: e.target,
          relation: e.relation,
          confidence: e.confidence,
          reasoning: e.reasoning,
        } as unknown as D3Link))
          .id(d => d.id)
          .distance(d => 90 + (1 - d.confidence) * 80)
      )
      .force('charge', d3.forceManyBody().strength(-280))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide(30));

    // Draw edges
    const linkGroup = g.append('g').attr('class', 'links');
    const linkSel = linkGroup.selectAll('line')
      .data(visibleEdges)
      .join('line')
      .attr('stroke', d => EDGE_COLORS[d.relation] ?? '#475569')
      .attr('stroke-width', d => 1 + d.confidence)
      .attr('stroke-opacity', 0.65)
      .attr('marker-end', d => `url(#arrow-${d.relation})`);

    // Edge labels
    const edgeLabelSel = g.append('g').selectAll('text')
      .data(visibleEdges.filter(e => e.relation !== 'INVOLVED'))
      .join('text')
      .attr('font-size', 7)
      .attr('fill', d => EDGE_COLORS[d.relation] ?? '#64748b')
      .attr('text-anchor', 'middle')
      .attr('dy', -3)
      .text(d => `${d.relation} ${Math.round(d.confidence * 100)}%`)
      .style('pointer-events', 'none');

    // Draw nodes
    const nodeGroup = g.append('g').attr('class', 'nodes');
    const nodeSel = nodeGroup.selectAll<SVGGElement, D3Node>('g')
      .data(visibleNodes)
      .join('g')
      .attr('cursor', 'pointer')
      .on('click', (_, d) => setInspect({ node: d }))
      .call(
        d3.drag<SVGGElement, D3Node>()
          .on('start', (ev, d) => { if (!ev.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
          .on('drag', (ev, d) => { d.fx = ev.x; d.fy = ev.y; })
          .on('end', (ev, d) => { if (!ev.active) sim.alphaTarget(0); d.fx = null; d.fy = null; })
      );

    nodeSel.append('circle')
      .attr('r', d => d.node_type === 'NewsEvent' ? 12 : 8)
      .attr('fill', d => NODE_COLORS[d.node_type] ?? '#64748b')
      .attr('fill-opacity', 0.85)
      .attr('stroke', d => NODE_COLORS[d.node_type] ?? '#64748b')
      .attr('stroke-width', 2)
      .attr('stroke-opacity', 0.5);

    nodeSel.append('text')
      .text(d => d.label.length > 18 ? d.label.slice(0, 16) + '…' : d.label)
      .attr('dy', 22)
      .attr('text-anchor', 'middle')
      .attr('font-size', 9)
      .attr('fill', '#cbd5e1')
      .style('pointer-events', 'none');

    // Simulation tick
    sim.on('tick', () => {
      linkSel
        .attr('x1', d => (d as unknown as { source: D3Node }).source.x)
        .attr('y1', d => (d as unknown as { source: D3Node }).source.y)
        .attr('x2', d => (d as unknown as { target: D3Node }).target.x)
        .attr('y2', d => (d as unknown as { target: D3Node }).target.y);

      nodeSel.attr('transform', d => `translate(${d.x},${d.y})`);

      edgeLabelSel
        .attr('x', d => {
          const src = visibleNodes.find(n => n.id === (typeof d.source === 'string' ? d.source : (d.source as D3Node).id));
          const tgt = visibleNodes.find(n => n.id === (typeof d.target === 'string' ? d.target : (d.target as D3Node).id));
          return src && tgt ? (src.x + tgt.x) / 2 : 0;
        })
        .attr('y', d => {
          const src = visibleNodes.find(n => n.id === (typeof d.source === 'string' ? d.source : (d.source as D3Node).id));
          const tgt = visibleNodes.find(n => n.id === (typeof d.target === 'string' ? d.target : (d.target as D3Node).id));
          return src && tgt ? (src.y + tgt.y) / 2 : 0;
        });
    });

    // Center on load
    setTimeout(() => {
      svg.transition().duration(600).call(
        zoom.transform,
        d3.zoomIdentity.translate(width / 2, height / 2).scale(0.75).translate(-width / 2, -height / 2)
      );
    }, 800);

    return () => sim.stop();
  }, [graph, filterType]);

  return (
    <div className="relative w-full h-full">
      {/* Legend + filter row */}
      <div className="absolute top-3 left-3 z-10 flex flex-wrap gap-1.5">
        <button
          onClick={() => setFilterType(null)}
          className={`text-[10px] px-2 py-0.5 rounded-full border transition-all ${!filterType ? 'bg-slate-600 border-slate-500 text-white' : 'border-slate-700 text-slate-400 hover:border-slate-600'}`}
        >
          All
        </button>
        {nodeTypes.map(t => (
          <button
            key={t}
            onClick={() => setFilterType(filterType === t ? null : t)}
            className={`text-[10px] px-2 py-0.5 rounded-full border transition-all ${filterType === t ? 'text-white border-transparent' : 'border-slate-700 text-slate-400 hover:border-slate-600'}`}
            style={filterType === t ? { backgroundColor: NODE_COLORS[t] + 'cc', borderColor: NODE_COLORS[t] } : {}}
          >
            <span className="inline-block w-2 h-2 rounded-full mr-1 align-middle" style={{ backgroundColor: NODE_COLORS[t] }} />
            {t}
          </button>
        ))}
      </div>

      {/* Edge relation legend */}
      <div className="absolute top-3 right-3 z-10 glass rounded-xl p-2.5 hidden lg:block">
        {Object.entries(EDGE_COLORS).filter(([k]) => k !== 'INVOLVED').map(([rel, color]) => (
          <div key={rel} className="flex items-center gap-1.5 mb-1 last:mb-0">
            <div className="w-5 h-0.5 rounded" style={{ backgroundColor: color }} />
            <span className="text-[9px] text-slate-400">{rel}</span>
          </div>
        ))}
      </div>

      <svg ref={svgRef} className="graph-canvas" />

      {/* Zoom controls */}
      <div className="absolute bottom-4 right-4 z-10 flex flex-col gap-1">
        {[
          { icon: <ZoomIn size={14} />, action: 'in' },
          { icon: <ZoomOut size={14} />, action: 'out' },
          { icon: <Maximize2 size={14} />, action: 'fit' },
        ].map(({ icon, action }) => (
          <button
            key={action}
            onClick={() => {
              const svg = d3.select(svgRef.current!);
              const zoom = d3.zoom<SVGSVGElement, unknown>().scaleExtent([0.15, 4]).on('zoom', ev => svg.select('g').attr('transform', ev.transform));
              if (action === 'in') svg.transition().call(zoom.scaleBy as never, 1.4);
              else if (action === 'out') svg.transition().call(zoom.scaleBy as never, 0.7);
              else svg.transition().call(zoom.transform as never, d3.zoomIdentity.scale(0.75));
            }}
            className="w-8 h-8 glass rounded-lg flex items-center justify-center text-slate-400 hover:text-white border border-slate-700 hover:border-slate-500 transition-all"
          >
            {icon}
          </button>
        ))}
      </div>

      {/* Inspect panel */}
      {inspect && (
        <div className="absolute top-3 left-1/2 -translate-x-1/2 z-20 w-80 glass rounded-xl border border-slate-600/60 p-4 shadow-2xl fade-up">
          <div className="flex items-start justify-between gap-2 mb-2">
            <div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full text-xs font-medium"
                style={{ backgroundColor: NODE_COLORS[inspect.node.node_type] + '33', color: NODE_COLORS[inspect.node.node_type] }}>
                {inspect.node.node_type}
              </span>
              <h4 className="text-white font-semibold text-sm mt-1">{inspect.node.label}</h4>
            </div>
            <button onClick={() => setInspect(null)} className="text-slate-400 hover:text-white flex-shrink-0">
              <X size={14} />
            </button>
          </div>
          {inspect.node.date && <p className="text-xs text-slate-400 mb-1">📅 {inspect.node.date}</p>}
          {inspect.node.sentiment !== null && inspect.node.sentiment !== undefined && (
            <p className="text-xs text-slate-400 mb-1">
              Sentiment: <span className={inspect.node.sentiment < 0 ? 'text-rose-400' : 'text-emerald-400'}>
                {inspect.node.sentiment > 0 ? '+' : ''}{inspect.node.sentiment.toFixed(2)}
              </span>
            </p>
          )}
          {inspect.node.properties?.description && (
            <p className="text-xs text-slate-300 mt-2 line-clamp-3">
              {String(inspect.node.properties.description)}
            </p>
          )}
          {Array.isArray(inspect.node.properties?.source_urls) &&
            (inspect.node.properties.source_urls as string[]).length > 0 && (
              <a
                href={(inspect.node.properties.source_urls as string[])[0]}
                target="_blank" rel="noreferrer"
                className="inline-flex items-center gap-1 text-[10px] text-indigo-400 hover:text-indigo-300 mt-2"
              >
                <ExternalLink size={10} /> View Source Article
              </a>
            )}
        </div>
      )}
    </div>
  );
}

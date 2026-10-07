import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import asyncio
from app.agents.harvester import DiscourseHarvesterAgent
from app.agents.extractor import SemanticEventExtractorAgent
from app.agents.ontology import KnowledgeOntologyBuilderAgent
from app.schemas.models import HarvestRequest, ExtractionRequest, OntologyBuildRequest


async def main():
    print("==================================================")
    print("Testing CLARION Agent 3: Knowledge Ontology Builder")
    print("==================================================")

    harvester = DiscourseHarvesterAgent()
    extractor = SemanticEventExtractorAgent()
    builder = KnowledgeOntologyBuilderAgent()

    try:
        # Step 1: Harvest
        print("[1/3] Harvesting article corpus with Agent 1...")
        harvest_res = await harvester.harvest(HarvestRequest(topic="NEET Exam Controversy", max_articles=25))
        print(f"      Harvested {harvest_res.unique_articles_count} unique articles.")

        # Step 2: Extract canonical events
        print("\n[2/3] Extracting canonical events & entities with Agent 2...")
        extract_res = await extractor.extract_events(ExtractionRequest(
            articles=harvest_res.articles,
            topic=harvest_res.topic
        ))
        print(f"      Extracted {extract_res.canonical_events_count} canonical event nodes.")

        # Step 3: Build Knowledge Ontology
        print("\n[3/3] Constructing Knowledge Ontology Graph with Agent 3...")
        ontology_res = await builder.build_ontology(OntologyBuildRequest(
            events=extract_res.events,
            topic=extract_res.topic,
            confidence_threshold=0.60
        ))

        graph = ontology_res.graph
        print(f"\n[OK] Knowledge Ontology Construction Complete!")
        print(f"[*] Processing Duration: {ontology_res.duration_ms} ms")
        print(f"[*] Active Storage Backend: {ontology_res.storage_backend}")
        print(f"[*] Total Ontology Nodes: {graph.node_count}")
        print(f"[*] Total Edges: {graph.edge_count}")
        print(f"[*] Causal/Relational Edges: {graph.causal_edges_count}")
        print(f"[*] Graph Density: {graph.density}")

        # Breakdown by node type
        node_types = {}
        for n in graph.nodes:
            node_types[n.node_type] = node_types.get(n.node_type, 0) + 1
        print("\n--- Ontology Node Type Distribution ---")
        for nt, cnt in sorted(node_types.items()):
            print(f"  - {nt}: {cnt} nodes")

        # Breakdown by edge relation
        edge_relations = {}
        for e in graph.edges:
            edge_relations[e.relation] = edge_relations.get(e.relation, 0) + 1
        print("\n--- Typed Edge Relationship Distribution ---")
        for rel, cnt in sorted(edge_relations.items()):
            print(f"  - {rel}: {cnt} edges")

        print("\n--- Primary Narrative Causal Chains (Topological Paths) ---")
        for i, chain in enumerate(ontology_res.key_causal_chains, 1):
            print(f"  {i}. {chain}")

        print("\n--- Sample Causal Edges with Confidence & Reasoning ---")
        causal_edges = [e for e in graph.edges if e.relation != "INVOLVED"]
        for ce in causal_edges[:6]:
            print(f"  [{ce.relation}] ({int(ce.confidence*100)}% conf): {ce.reasoning}")

        # Validation Assertions
        assert graph.node_count >= extract_res.canonical_events_count, "Node count should be at least event count"
        assert graph.causal_edges_count >= 5, f"Expected at least 5 causal edges, got {graph.causal_edges_count}"
        assert all(e.confidence >= 0.60 for e in graph.edges), "All edges must meet >= 0.60 confidence threshold"
        assert "NewsEvent" in node_types, "Must contain NewsEvent nodes"
        assert "Organization" in node_types or "Policy" in node_types, "Must contain entity nodes"

        print("\n>>> AGENT 3 TESTS PASSED SUCCESSFULLY! <<<")

    finally:
        await harvester.close()
        builder.close()


if __name__ == "__main__":
    asyncio.run(main())

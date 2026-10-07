import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import asyncio
from app.agents.harvester import DiscourseHarvesterAgent
from app.agents.extractor import SemanticEventExtractorAgent
from app.agents.ontology import KnowledgeOntologyBuilderAgent
from app.agents.synthesis import SynthesisAgent
from app.schemas.models import (
    HarvestRequest,
    ExtractionRequest,
    OntologyBuildRequest,
    SynthesisRequest
)


async def main():
    print("==========================================================")
    print("Testing CLARION Agent 4: Synthesis & Forecasting Agent")
    print("==========================================================")

    harvester = DiscourseHarvesterAgent()
    extractor = SemanticEventExtractorAgent()
    builder = KnowledgeOntologyBuilderAgent()
    synthesizer = SynthesisAgent()

    try:
        # Step 1: Harvest
        print("[1/4] Harvesting news articles with Agent 1...")
        harvest_res = await harvester.harvest(HarvestRequest(topic="NEET Exam Controversy", max_articles=25))
        print(f"      Harvested {harvest_res.unique_articles_count} unique articles.")

        # Step 2: Extract canonical events
        print("\n[2/4] Extracting canonical events & entities with Agent 2...")
        extract_res = await extractor.extract_events(ExtractionRequest(
            articles=harvest_res.articles,
            topic=harvest_res.topic
        ))
        print(f"      Extracted {extract_res.canonical_events_count} canonical event nodes.")

        # Step 3: Build ontology graph
        print("\n[3/4] Constructing Knowledge Ontology Graph with Agent 3...")
        ontology_res = await builder.build_ontology(OntologyBuildRequest(
            events=extract_res.events,
            topic=extract_res.topic,
            confidence_threshold=0.60
        ))
        print(f"      Built graph: {ontology_res.graph.node_count} nodes, {ontology_res.graph.edge_count} edges.")

        # Step 4: Synthesize full intelligence report with Agent 4
        print("\n[4/4] Executing Synthesis, RAG Forecasting, and Bias Analysis with Agent 4...")
        report = await synthesizer.synthesize(SynthesisRequest(
            topic=harvest_res.topic,
            events=extract_res.events,
            articles=harvest_res.articles,
            graph=ontology_res.graph
        ))

        print("\n" + "="*58)
        print("CLARION MASTER INTELLIGENCE DOSSIER GENERATED")
        print("="*58)
        print(f"[*] Topic: {report.topic}")
        print(f"[*] Synthesized Timestamp: {report.synthesized_at}")
        print(f"[*] Total Articles Analyzed: {report.article_corpus_count}")
        print(f"[*] Canonical Milestone Events: {report.canonical_events_count}")
        print(f"[*] Ontology Structure: {report.ontology_nodes_count} nodes, {report.ontology_edges_count} edges")
        print(f"[*] Pipeline Duration: {report.total_pipeline_duration_ms} ms")

        # 1. Narrative Arc Breakdown
        print("\n--- 1. NARRATIVE ARC PHASES ---")
        for phase in report.narrative_arc:
            print(f"\n[{phase.phase.upper()}] ({phase.date_range}) | Sentiment: {phase.dominant_sentiment:+0.2f}")
            print(f"  Headline: {phase.headline}")
            print(f"  Summary:  {phase.summary}")
            print(f"  Key Milestones ({len(phase.key_events)}):")
            for ke in phase.key_events[:2]:
                print(f"    - {ke}")

        # 2. Historical Precedents & Inferential Forecasts
        print("\n--- 2. HISTORICAL PRECEDENTS RETRIEVED (ChromaDB RAG) ---")
        for prec in report.historical_precedents_matched:
            print(f"  - [{prec.year}] {prec.title} (Match: {int(prec.similarity_score*100)}%)")
            print(f"    Resolution: {prec.ultimate_resolution[:120]}...")

        print("\n--- 3. INFERENTIAL PREDICTIVE FORECASTS ---")
        for fc in report.forecasts:
            print(f"\n  [{fc.probability_pct}% PROBABILITY] {fc.implication}")
            print(f"    Timeframe: {fc.timeframe} | Confidence: {int(fc.confidence_score*100)}%")
            print(f"    Precedent: {fc.matched_precedent}")
            print(f"    Rationale: {fc.causal_rationale}")

        # 3. Cross-Source Bias & Divergence Analysis
        print("\n--- 4. CROSS-SOURCE BIAS & NARRATIVE DIVERGENCE ---")
        print(f"Overall Divergence Score: {report.bias_analysis.divergence_score:0.2f} / 1.00\n")
        for ob in report.bias_analysis.outlets:
            print(f"[{ob.outlet}] (Sentiment: {ob.sentiment_score:+0.2f}, Bias Index: {ob.bias_index:0.2f}, Articles: {ob.article_count})")
            print(f"  Focus:     {ob.framing_focus}")
            print(f"  Emphases:  {'; '.join(ob.key_emphases[:2])}")
            print(f"  Omissions: {'; '.join(ob.key_omissions[:2])}\n")

        print("--- 5. OBJECTIVE FACTUAL MIDDLE GROUND SYNTHESIS ---")
        print(report.bias_analysis.objective_middle_ground)

        print("\n--- 6. EXECUTIVE SUMMARY ---")
        print(report.executive_summary)

        # Assertions
        assert len(report.narrative_arc) == 5, f"Expected 5 narrative phases, got {len(report.narrative_arc)}"
        assert len(report.forecasts) >= 3, "Expected at least 3 forecasts"
        assert len(report.historical_precedents_matched) >= 1, "Expected historical precedents"
        assert len(report.bias_analysis.outlets) >= 3, "Expected at least 3 outlets in bias report"
        assert len(report.bias_analysis.objective_middle_ground) > 50, "Objective middle ground required"

        print("\n>>> ALL AGENT 4 & FULL PIPELINE TESTS PASSED SUCCESSFULLY! <<<")

    finally:
        await harvester.close()
        builder.close()


if __name__ == "__main__":
    asyncio.run(main())

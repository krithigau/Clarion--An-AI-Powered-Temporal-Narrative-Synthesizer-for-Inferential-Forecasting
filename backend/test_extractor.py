import sys
import io
# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import asyncio
from app.agents.harvester import DiscourseHarvesterAgent
from app.agents.extractor import SemanticEventExtractorAgent
from app.schemas.models import HarvestRequest, ExtractionRequest


async def main():
    print("==================================================")
    print("Testing CLARION Agent 2: Semantic Event Extractor")
    print("==================================================")

    # 1. Harvest articles with Agent 1
    harvester = DiscourseHarvesterAgent()
    extractor = SemanticEventExtractorAgent()

    try:
        harvest_req = HarvestRequest(
            topic="NEET Exam Controversy",
            max_articles=25
        )
        print("[1/2] Harvesting raw article corpus with Agent 1...")
        harvest_res = await harvester.harvest(harvest_req)
        print(f"      Harvested {harvest_res.unique_articles_count} unique articles.")

        # 2. Extract structured events with Agent 2
        print("\n[2/2] Extracting events, NER entities, sentiment, and significance with Agent 2...")
        extract_req = ExtractionRequest(
            articles=harvest_res.articles,
            topic=harvest_res.topic
        )
        extraction_res = await extractor.extract_events(extract_req)

        print(f"\n[OK] Semantic Event Extraction Complete!")
        print(f"[*] Processing Duration: {extraction_res.processing_duration_ms} ms")
        print(f"[*] Articles Processed: {extraction_res.total_articles_processed}")
        print(f"[*] Raw Events Extracted: {extraction_res.raw_events_extracted}")
        print(f"[*] Canonical NewsEvent Nodes: {extraction_res.canonical_events_count}")

        print("\n--- Entities Discovered by Category ---")
        for etype, count in extraction_res.entities_discovered.items():
            print(f"  - {etype}: {count}")

        print("\n--- Sample Canonical NewsEvent Nodes (Oldest to Newest) ---")
        for i, ev in enumerate(extraction_res.events[:5], 1):
            ent_summary = ", ".join([f"{e.name} ({e.type})" for e in ev.entities[:3]])
            pubs = ", ".join(ev.source_publishers)
            print(f"\nEvent {i}: [{ev.date}] {ev.title}")
            print(f"  Location: {ev.location}")
            print(f"  Coverage: {ev.coverage_count} source(s) [{pubs}]")
            print(f"  Scores:   Sentiment={ev.sentiment_score:+0.2f}, Significance={ev.significance_score:0.2f}")
            print(f"  Entities: {ent_summary}")
            print(f"  Summary:  {ev.description[:140]}...")

        if len(extraction_res.events) > 5:
            last_ev = extraction_res.events[-1]
            print(f"\n... ({len(extraction_res.events) - 6} more canonical events) ...")
            print(f"\nLatest Event: [{last_ev.date}] {last_ev.title}")
            print(f"  Coverage: {last_ev.coverage_count} source(s) [{', '.join(last_ev.source_publishers)}]")
            print(f"  Scores:   Sentiment={last_ev.sentiment_score:+0.2f}, Significance={last_ev.significance_score:0.2f}")

        # Assertions
        assert extraction_res.canonical_events_count > 0, "Should generate canonical event nodes"
        assert extraction_res.canonical_events_count <= extraction_res.raw_events_extracted, "Deduplication should merge or preserve count"
        assert sum(extraction_res.entities_discovered.values()) > 0, "Entities should be discovered"

        # Check multi-source coverage merge
        multi_covered = [e for e in extraction_res.events if e.coverage_count > 1]
        print(f"\n[*] Canonical events with multi-source coverage: {len(multi_covered)}")
        for mc in multi_covered:
            print(f"    - [{mc.date}] '{mc.title[:50]}' confirmed by {mc.coverage_count} outlets: {', '.join(mc.source_publishers)}")

        print("\n>>> AGENT 2 TESTS PASSED SUCCESSFULLY! <<<")

    finally:
        await harvester.close()


if __name__ == "__main__":
    asyncio.run(main())

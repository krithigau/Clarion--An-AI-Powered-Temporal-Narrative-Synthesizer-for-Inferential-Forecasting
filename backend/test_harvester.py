import sys
import io
# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import asyncio
from app.agents.harvester import DiscourseHarvesterAgent
from app.schemas.models import HarvestRequest


async def main():
    print("==================================================")
    print("Testing CLARION Agent 1: Discourse Harvester")
    print("==================================================")

    agent = DiscourseHarvesterAgent()
    request = HarvestRequest(
        topic="NEET Exam Controversy",
        max_articles=25
    )

    try:
        response = await agent.harvest(request)
        print(f"\n[OK] Harvesting Complete for Topic: '{response.topic}'")
        print(f"[*] Harvest Duration: {response.harvest_duration_ms} ms")
        print(f"[*] Total Raw Harvested: {response.total_harvested}")
        print(f"[*] Merged Near-Duplicates: {response.deduplication_stats.merged_count}")
        print(f"[*] Unique Canonical Articles: {response.unique_articles_count}")
        print(f"[*] Deduplication Ratio: {response.deduplication_stats.dedup_ratio_pct}%")
        print(f"[*] Timeline Span: {response.earliest_date} -> {response.latest_date}")
        print(f"[*] Sources Represented ({len(response.sources_represented)}): {', '.join(response.sources_represented)}")

        print("\n--- Chronological Sample Corpus (Oldest to Newest) ---")
        for i, article in enumerate(response.articles[:5], 1):
            merged_info = f" [Merged with: {', '.join(article.syndicated_publishers)}]" if article.is_duplicate_merged else ""
            print(f"{i}. [{article.published_at}] ({article.publisher}) {article.title}{merged_info}")

        if len(response.articles) > 5:
            print(f"\n... ({len(response.articles) - 6} more articles in middle) ...\n")
            latest = response.articles[-1]
            print(f"Latest: [{latest.published_at}] ({latest.publisher}) {latest.title}")

        # Assertions for validation
        assert response.unique_articles_count > 0, "Should have extracted articles"
        assert response.earliest_date <= response.latest_date, "Articles should be sorted chronologically"
        print("\n>>> ALL TESTS PASSED SUCCESSFULLY! <<<")

    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())

import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from app.agents.harvester import DiscourseHarvesterAgent
from app.schemas.models import RawArticle


def test_deduplication():
    print("Testing Semantic Deduplication Logic in Agent 1...")
    agent = DiscourseHarvesterAgent()

    # Create synthetic articles: one original, one wire duplicate from another outlet, one different
    art1 = RawArticle(
        id="art-1",
        title="CBI Arrests Key Mastermind in Paper Leak Case in Patna",
        publisher="The Hindu",
        published_at="2024-06-27",
        content="The Central Bureau of Investigation on Thursday arrested the primary suspect behind the organized solver gang in Patna. Officials recovered encrypted phones and payment receipts.",
        url="https://thehindu.com/1"
    )
    art2 = RawArticle(
        id="art-2",
        title="CBI Arrests Mastermind in Paper Leak Case from Patna",  # Near identical headline & content from syndicated wire
        publisher="NDTV",
        published_at="2024-06-27",
        content="The Central Bureau of Investigation on Thursday arrested the primary suspect behind the organized solver gang in Patna. Officials recovered encrypted mobile devices and transaction receipts.",
        url="https://ndtv.com/1"
    )
    art3 = RawArticle(
        id="art-3",
        title="Supreme Court Refuses to Stay Medical Counseling",
        publisher="Republic TV",
        published_at="2024-06-11",
        content="A vacation bench of the Supreme Court declined to stay the ongoing counseling process, observing that admission schedules cannot be disrupted.",
        url="https://republicworld.com/1"
    )

    articles = [art1, art2, art3]
    unique, merged_count = agent._semantic_deduplicate(articles)

    print(f"Initial: {len(articles)}, Merged: {merged_count}, Unique: {len(unique)}")
    assert merged_count == 1, f"Expected 1 merged duplicate, got {merged_count}"
    assert len(unique) == 2, f"Expected 2 unique articles, got {len(unique)}"
    assert "NDTV" in unique[0].syndicated_publishers or "The Hindu" in unique[0].syndicated_publishers
    print("[OK] Near-duplicate wire report successfully identified and syndicated publishers merged!")


if __name__ == "__main__":
    test_deduplication()

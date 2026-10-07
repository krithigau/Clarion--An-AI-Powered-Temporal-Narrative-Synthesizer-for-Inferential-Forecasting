import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_endpoints():
    print("Testing FastAPI Endpoints...")

    # 1. Health endpoint
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    print(f"[OK] Health check passed: {data['app']} (v{data['version']})")

    # 2. Benchmark topics endpoint
    res = client.get("/api/benchmark-topics")
    assert res.status_code == 200
    topics = res.json()
    assert len(topics) >= 1
    print(f"[OK] Benchmark topics passed: {len(topics)} topics loaded")

    # 3. Harvester API endpoint
    payload = {
        "topic": "NEET Exam Controversy",
        "max_articles": 20
    }
    res = client.post("/api/harvester/harvest", json=payload)
    assert res.status_code == 200
    harvest_data = res.json()
    assert harvest_data["unique_articles_count"] > 0
    print(f"[OK] Harvester endpoint passed: harvested {harvest_data['unique_articles_count']} unique articles")

    # 4. Extractor API endpoint
    extract_payload = {
        "articles": harvest_data["articles"],
        "topic": harvest_data["topic"]
    }
    res = client.post("/api/extractor/extract", json=extract_payload)
    assert res.status_code == 200
    extract_data = res.json()
    assert extract_data["canonical_events_count"] > 0
    print(f"[OK] Extractor endpoint passed: generated {extract_data['canonical_events_count']} canonical events")

    # 5. Full Pipeline endpoint (Agent 1 + Agent 2 chained)
    pipe_res = client.post("/api/pipeline/harvest-and-extract", json=payload)
    assert pipe_res.status_code == 200
    pipe_data = pipe_res.json()
    assert pipe_data["canonical_events_count"] > 0
    print(f"[OK] Chained harvest-extract endpoint passed: {pipe_data['canonical_events_count']} canonical events created")

    # 6. Ontology Builder API endpoint (Agent 3)
    ontology_payload = {
        "events": extract_data["events"],
        "topic": extract_data["topic"],
        "confidence_threshold": 0.60
    }
    ont_res = client.post("/api/ontology/build", json=ontology_payload)
    assert ont_res.status_code == 200
    ont_data = ont_res.json()
    assert ont_data["graph"]["node_count"] > 0
    assert ont_data["graph"]["causal_edges_count"] > 0
    print(f"[OK] Ontology builder endpoint passed: {ont_data['graph']['node_count']} nodes and {ont_data['graph']['causal_edges_count']} causal edges")

    # 7. Tri-Agent Chained Pipeline endpoint (Agent 1 -> Agent 2 -> Agent 3)
    tri_res = client.post("/api/pipeline/harvest-extract-ontology", json=payload)
    assert tri_res.status_code == 200
    tri_data = tri_res.json()
    assert tri_data["graph"]["node_count"] > 0
    print(f"[OK] Full 3-Agent pipeline endpoint passed: {tri_data['graph']['node_count']} nodes, {tri_data['graph']['edge_count']} total edges built in {tri_data['duration_ms']}ms")

    print("\n>>> ALL API TESTS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    test_endpoints()



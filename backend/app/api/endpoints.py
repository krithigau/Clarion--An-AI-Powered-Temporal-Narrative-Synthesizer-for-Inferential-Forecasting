from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.schemas.models import (
    HarvestRequest,
    HarvestResponse,
    ExtractionRequest,
    ExtractionResponse,
    OntologyBuildRequest,
    OntologyBuildResponse,
    SynthesisRequest,
    ClarionReport
)
from app.agents.harvester import DiscourseHarvesterAgent
from app.agents.extractor import SemanticEventExtractorAgent
from app.agents.ontology import KnowledgeOntologyBuilderAgent
from app.agents.synthesis import SynthesisAgent
from app.core.config import settings

router = APIRouter(prefix="/api", tags=["CLARION Core"])


def get_harvester() -> DiscourseHarvesterAgent:
    return DiscourseHarvesterAgent()


def get_extractor() -> SemanticEventExtractorAgent:
    return SemanticEventExtractorAgent()


@router.get("/health")
async def health_check():
    """System health and agent readiness check."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "gemini_model": settings.GEMINI_MODEL,
        "has_gemini_key": bool(settings.GEMINI_API_KEY),
        "has_newsapi_key": bool(settings.NEWS_API_KEY),
        "use_neo4j": settings.USE_NEO4J,
    }


@router.get("/benchmark-topics")
async def get_benchmark_topics():
    """Provides recommended canonical benchmark queries from the CLARION specification."""
    return [
        {
            "id": "neet-controversy",
            "title": "NEET Exam Controversy",
            "domain": "Education Policy & Testing Integrity",
            "timeframe": "2017 – 2024",
            "description": "Comprehensive causal arc tracing from Supreme Court centralization in 2017 to the 2024 mass paper leak and CBI investigation."
        },
        {
            "id": "farm-laws-protest",
            "title": "Farm Laws & Agitation",
            "domain": "Agrarian Policy & Mass Mobilization",
            "timeframe": "2020 – 2021",
            "description": "Traces parliamentary passage of three agriculture ordinances, escalating border blockades, to executive repeal."
        },
        {
            "id": "svb-collapse",
            "title": "Silicon Valley Bank Run & Collapse",
            "domain": "Financial Markets & Bank Contagion",
            "timeframe": "2022 – 2023",
            "description": "Interest rate hikes, bond portfolio mark-to-market depreciation, tech depositor flight, and FDIC emergency systemic risk exception."
        }
    ]


@router.post("/harvester/harvest", response_model=HarvestResponse)
async def harvest_discourse(
    request: HarvestRequest,
    harvester: DiscourseHarvesterAgent = Depends(get_harvester)
):
    """
    Agent 1: Harvests temporal news articles, executes semantic deduplication,
    and returns chronologically ordered discourse corpus.
    """
    try:
        response = await harvester.harvest(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discourse harvesting failed: {str(e)}")
    finally:
        await harvester.close()


@router.post("/extractor/extract", response_model=ExtractionResponse)
async def extract_semantic_events(
    request: ExtractionRequest,
    extractor: SemanticEventExtractorAgent = Depends(get_extractor)
):
    """
    Agent 2: Semantic Event Extractor.
    Extracts structured milestone events, classifies NER entities (Person, Org, Policy, Location, Event),
    computes sentiment and significance scores, and merges co-occurring events into canonical NewsEvent nodes.
    """
    try:
        response = await extractor.extract_events(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic event extraction failed: {str(e)}")


@router.post("/pipeline/harvest-and-extract", response_model=ExtractionResponse)
async def harvest_and_extract(
    request: HarvestRequest,
    harvester: DiscourseHarvesterAgent = Depends(get_harvester),
    extractor: SemanticEventExtractorAgent = Depends(get_extractor)
):
    """
    Chains Agent 1 (Discourse Harvester) directly into Agent 2 (Semantic Event Extractor).
    """
    try:
        harvest_res = await harvester.harvest(request)
        extract_req = ExtractionRequest(articles=harvest_res.articles, topic=request.topic)
        extraction_res = await extractor.extract_events(extract_req)
        return extraction_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Harvest and Extract pipeline failed: {str(e)}")
    finally:
        await harvester.close()


def get_ontology_builder() -> KnowledgeOntologyBuilderAgent:
    return KnowledgeOntologyBuilderAgent()


@router.post("/ontology/build", response_model=OntologyBuildResponse)
async def build_knowledge_ontology(
    request: OntologyBuildRequest,
    builder: KnowledgeOntologyBuilderAgent = Depends(get_ontology_builder)
):
    """
    Agent 3: Knowledge Ontology Builder.
    Constructs the typed entity-relationship knowledge graph with pairwise causal reasoning
    (CAUSED, TRIGGERED, ESCALATED, INFLUENCED, RESOLVED, INVOLVED) and confidence filtering >= 0.6.
    """
    try:
        response = await builder.build_ontology(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge ontology construction failed: {str(e)}")
    finally:
        builder.close()


@router.post("/pipeline/harvest-extract-ontology", response_model=OntologyBuildResponse)
async def harvest_extract_ontology(
    request: HarvestRequest,
    harvester: DiscourseHarvesterAgent = Depends(get_harvester),
    extractor: SemanticEventExtractorAgent = Depends(get_extractor),
    builder: KnowledgeOntologyBuilderAgent = Depends(get_ontology_builder)
):
    """
    Chains Agent 1 (Harvester) -> Agent 2 (Extractor) -> Agent 3 (Ontology Builder).
    Returns complete D3/Cytoscape-compatible Knowledge Ontology Graph with causal chains.
    """
    try:
        harvest_res = await harvester.harvest(request)
        extract_req = ExtractionRequest(articles=harvest_res.articles, topic=request.topic)
        extract_res = await extractor.extract_events(extract_req)
        ontology_req = OntologyBuildRequest(events=extract_res.events, topic=request.topic)
        ontology_res = await builder.build_ontology(ontology_req)
        return ontology_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Full ontology pipeline failed: {str(e)}")
    finally:
        await harvester.close()
        builder.close()


def get_synthesis_agent() -> SynthesisAgent:
    return SynthesisAgent()


@router.post("/synthesis/analyze", response_model=ClarionReport)
async def analyze_synthesis(
    request: SynthesisRequest,
    synthesizer: SynthesisAgent = Depends(get_synthesis_agent)
):
    """
    Agent 4: Synthesis & Forecasting Agent.
    Generates Narrative Arc phases, ChromaDB RAG-grounded inferential forecasts,
    and cross-source narrative bias divergence.
    """
    try:
        report = await synthesizer.synthesize(request)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synthesis analysis failed: {str(e)}")


@router.post("/analyze", response_model=ClarionReport)
async def analyze_full_topic(
    request: HarvestRequest,
    harvester: DiscourseHarvesterAgent = Depends(get_harvester),
    extractor: SemanticEventExtractorAgent = Depends(get_extractor),
    builder: KnowledgeOntologyBuilderAgent = Depends(get_ontology_builder),
    synthesizer: SynthesisAgent = Depends(get_synthesis_agent)
):
    """
    Master CLARION End-to-End Pipeline:
    Executes all 4 autonomous agents in sequence:
    Agent 1 (Harvester) -> Agent 2 (Extractor) -> Agent 3 (Ontology Builder) -> Agent 4 (Synthesizer)
    Yields the complete Master Intelligence Dossier.
    """
    try:
        # 1. Harvest Discourse
        harvest_res = await harvester.harvest(request)

        # 2. Extract Events & NER Entities
        extract_req = ExtractionRequest(articles=harvest_res.articles, topic=request.topic)
        extract_res = await extractor.extract_events(extract_req)

        # 3. Build Knowledge Ontology Graph
        ontology_req = OntologyBuildRequest(events=extract_res.events, topic=request.topic)
        ontology_res = await builder.build_ontology(ontology_req)

        # 4. Synthesize Narrative Arc, RAG Forecasts, and Bias Report
        synthesis_req = SynthesisRequest(
            topic=request.topic,
            events=extract_res.events,
            articles=harvest_res.articles,
            graph=ontology_res.graph
        )
        report = await synthesizer.synthesize(synthesis_req)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CLARION master pipeline failed: {str(e)}")
    finally:
        await harvester.close()
        builder.close()



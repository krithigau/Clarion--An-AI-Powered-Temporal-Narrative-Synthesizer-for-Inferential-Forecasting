from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class RawArticle(BaseModel):
    """Normalized news article entity harvested across timelines."""
    id: str = Field(description="Unique article identifier or hash")
    title: str = Field(description="Headline of the article")
    publisher: str = Field(description="Publishing outlet or source name (e.g. NDTV, The Hindu, Reuters)")
    published_at: str = Field(description="ISO formatted publication timestamp YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS")
    url: str = Field(default="", description="Original article canonical URL")
    content: str = Field(description="Full text or high-fidelity body excerpt")
    summary: Optional[str] = Field(default=None, description="Short summary/lede of the article")
    author: Optional[str] = Field(default=None, description="Author or wire byline")
    reach_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Estimated readership or outlet reach score")
    syndicated_publishers: List[str] = Field(default_factory=list, description="Other outlets that syndicated or republished this story")
    is_duplicate_merged: bool = Field(default=False, description="Flag indicating if near-duplicates were collapsed into this record")


class DeduplicationStats(BaseModel):
    initial_count: int = Field(description="Raw articles retrieved before deduplication")
    merged_count: int = Field(description="Number of near-duplicate articles identified and collapsed")
    final_unique_count: int = Field(description="Unique canonical articles remaining")
    dedup_ratio_pct: float = Field(description="Percentage reduction achieved via deduplication")


class HarvestRequest(BaseModel):
    topic: str = Field(..., description="Query topic or issue to investigate across time")
    from_date: Optional[str] = Field(default=None, description="Earliest date to harvest from (YYYY-MM-DD)")
    to_date: Optional[str] = Field(default=None, description="Latest date to harvest to (YYYY-MM-DD)")
    max_articles: int = Field(default=30, ge=5, le=100, description="Max canonical articles to harvest")
    preferred_sources: Optional[List[str]] = Field(default=None, description="Specific news outlets to prioritize")


class HarvestResponse(BaseModel):
    topic: str
    total_harvested: int
    unique_articles_count: int
    earliest_date: Optional[str] = None
    latest_date: Optional[str] = None
    sources_represented: List[str] = Field(default_factory=list)
    articles: List[RawArticle]
    deduplication_stats: DeduplicationStats
    harvest_duration_ms: float


# ==============================================================================
# Agent 2: Semantic Event Extraction Models
# ==============================================================================

EntityType = Literal["Person", "Organization", "Policy", "Location", "Event"]


class NamedEntity(BaseModel):
    """Named Entity Recognition (NER) item associated with an event."""
    name: str = Field(description="Entity proper name, e.g., 'CBI', 'Subodh Kumar Singh', 'NEET Regulation'")
    type: EntityType = Field(description="Classification: Person, Organization, Policy, Location, Event")
    mention_count: int = Field(default=1, description="Frequency of mentions")


class ExtractedEvent(BaseModel):
    """Raw structured event extracted from an article by Gemini API."""
    title: str = Field(description="Concise event title describing the action or occurrence")
    date: str = Field(description="Event occurrence date (YYYY-MM-DD)")
    location: str = Field(default="National", description="Geographic location or venue")
    description: str = Field(description="Detailed factual description of what occurred")
    entities: List[NamedEntity] = Field(default_factory=list, description="NER entities extracted from the event")
    sentiment_score: float = Field(default=0.0, ge=-1.0, le=1.0, description="Tone/sentiment from -1.0 (strongly negative/crisis) to +1.0 (positive)")
    significance_score: float = Field(default=0.7, ge=0.0, le=1.0, description="Estimated historical or systemic impact (0.0 to 1.0)")
    source_article_id: str = Field(default="", description="Originating article ID")
    source_publisher: str = Field(default="", description="Originating publisher")
    source_url: str = Field(default="", description="Article reference URL")


class CanonicalNewsEvent(BaseModel):
    """
    Canonical NewsEvent node representing a unique real-world milestone.
    Constructed by semantically deduplicating and merging multiple articles covering the same event.
    """
    id: str = Field(description="Unique node identifier, e.g., 'evt-2017-05-07-sc-verdict'")
    title: str = Field(description="Canonical event title")
    date: str = Field(description="Standardized occurrence date (YYYY-MM-DD)")
    location: str = Field(description="Primary geographic location")
    description: str = Field(description="Unified comprehensive description of the event")
    entities: List[NamedEntity] = Field(default_factory=list, description="Merged and deduplicated entity list")
    sentiment_score: float = Field(description="Averaged or synthesized sentiment score (-1.0 to 1.0)")
    significance_score: float = Field(description="Systemic impact rating (0.0 to 1.0)")
    source_articles: List[str] = Field(default_factory=list, description="IDs of articles reporting this event")
    source_publishers: List[str] = Field(default_factory=list, description="List of outlets that covered this event")
    source_urls: List[str] = Field(default_factory=list, description="Traceable original article URLs")
    coverage_count: int = Field(default=1, description="Number of independent reports confirming this event")


class ExtractionRequest(BaseModel):
    articles: List[RawArticle] = Field(..., description="Corpus of chronologically sorted articles from Agent 1")
    topic: Optional[str] = Field(default="News Discourse", description="Topic of the investigation")


class ExtractionResponse(BaseModel):
    topic: str
    total_articles_processed: int
    raw_events_extracted: int
    canonical_events_count: int
    entities_discovered: Dict[str, int] = Field(default_factory=dict, description="Counts broken down by entity type")
    events: List[CanonicalNewsEvent] = Field(default_factory=list, description="Chronologically sorted canonical events")
    processing_duration_ms: float


# ==============================================================================
# Agent 3: Temporal Knowledge Ontology Models
# ==============================================================================

CausalRelationType = Literal["CAUSED", "TRIGGERED", "ESCALATED", "INFLUENCED", "RESOLVED", "INVOLVED"]
NodeType = Literal["NewsEvent", "Person", "Organization", "Policy", "Location"]


class GraphNode(BaseModel):
    """Node in the Temporal Knowledge Ontology."""
    id: str = Field(description="Unique node ID")
    label: str = Field(description="Display label / name of the node")
    node_type: NodeType = Field(description="Typed ontology category")
    date: Optional[str] = Field(default=None, description="Date for NewsEvent nodes (YYYY-MM-DD)")
    sentiment: Optional[float] = Field(default=None, description="Sentiment score for events")
    significance: Optional[float] = Field(default=None, description="Significance rating")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary typed metadata")


class GraphEdge(BaseModel):
    """Directional, typed, weighted edge in the ontology."""
    source: str = Field(description="Source node ID")
    target: str = Field(description="Target node ID")
    relation: CausalRelationType = Field(description="CAUSED | TRIGGERED | ESCALATED | INFLUENCED | RESOLVED | INVOLVED")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0 (>= 0.6 kept)")
    reasoning: str = Field(description="Explanatory causal or relational reasoning")


class OntologyGraphData(BaseModel):
    """Graph structure compatible with D3.js, Cytoscape, and Neo4j Cypher exports."""
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    node_count: int = 0
    edge_count: int = 0
    causal_edges_count: int = 0
    density: float = 0.0


class OntologyBuildRequest(BaseModel):
    events: List[CanonicalNewsEvent] = Field(..., description="Canonical events from Agent 2")
    topic: Optional[str] = Field(default="News Topic", description="Topic of analysis")
    confidence_threshold: float = Field(default=0.60, ge=0.0, le=1.0, description="Minimum confidence score for edges")


class OntologyBuildResponse(BaseModel):
    topic: str
    graph: OntologyGraphData
    key_causal_chains: List[str] = Field(default_factory=list, description="Primary narrative causal pathways")
    storage_backend: str = Field(description="Active backend: NetworkX (In-Memory) or Neo4j")
    duration_ms: float


# ==============================================================================
# Agent 4: Synthesis, Forecasting & Cross-Source Bias Models
# ==============================================================================

NarrativePhaseType = Literal["Origin", "Escalation", "Peak", "Current State", "Projected Future"]


class NarrativePhase(BaseModel):
    """One of the 5 chronological narrative arc stages."""
    phase: NarrativePhaseType = Field(description="Origin | Escalation | Peak | Current State | Projected Future")
    date_range: str = Field(description="Temporal interval (e.g., '2017-05-07 to 2018-05-06')")
    headline: str = Field(description="Concise phase summary headline")
    summary: str = Field(description="Executive narrative summary grounded in article corpus via RAG")
    key_events: List[str] = Field(default_factory=list, description="Key milestone titles belonging to this phase")
    dominant_sentiment: float = Field(description="Average sentiment polarity across this phase (-1.0 to 1.0)")
    significance_level: str = Field(description="Critical | High | Moderate | Formative")


class HistoricalPrecedent(BaseModel):
    """Similar historical crisis/policy case retrieved from ChromaDB."""
    case_id: str
    title: str
    year: int
    domain: str
    similarity_score: float = Field(ge=0.0, le=1.0)
    trajectory_summary: str
    ultimate_resolution: str


class InferentialForecast(BaseModel):
    """Predictive forward-looking implication grounded in historical precedents."""
    id: str
    implication: str = Field(description="Projected institutional or societal outcome")
    probability_pct: int = Field(ge=0, le=100, description="Estimated outcome probability percentage")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Calibration confidence score")
    timeframe: str = Field(description="Expected emergence window (e.g., '3 - 6 Months', '1 - 2 Years')")
    matched_precedent: str = Field(description="Historical precedent that justifies this projection")
    causal_rationale: str = Field(description="Analogical and causal justification")


class OutletBiasProfile(BaseModel):
    """Framing analysis and slant breakdown for a specific news source."""
    outlet: str = Field(description="Publisher name (e.g. NDTV, Republic TV, The Hindu, Indian Express)")
    framing_focus: str = Field(description="Primary editorial angle / narrative posture")
    key_emphases: List[str] = Field(default_factory=list, description="Aspects prominently highlighted")
    key_omissions: List[str] = Field(default_factory=list, description="Context or facts downplayed or omitted")
    sentiment_score: float = Field(ge=-1.0, le=1.0, description="Average reporting sentiment")
    bias_index: float = Field(ge=0.0, le=1.0, description="Degree of divergence from neutral center")
    article_count: int = Field(default=1)


class CrossSourceBiasReport(BaseModel):
    """Comparative framing matrix across multiple outlets."""
    outlets: List[OutletBiasProfile] = Field(default_factory=list)
    divergence_score: float = Field(ge=0.0, le=1.0, description="Overall cross-source narrative divergence metric")
    objective_middle_ground: str = Field(description="Synthesized unbiased factual ground truth")


class SynthesisRequest(BaseModel):
    topic: str
    events: List[CanonicalNewsEvent]
    articles: List[RawArticle]
    graph: Optional[OntologyGraphData] = None


class ClarionReport(BaseModel):
    """The Complete CLARION Master Intelligence Dossier."""
    topic: str
    synthesized_at: str
    article_corpus_count: int
    canonical_events_count: int
    ontology_nodes_count: int
    ontology_edges_count: int
    narrative_arc: List[NarrativePhase] = Field(default_factory=list)
    forecasts: List[InferentialForecast] = Field(default_factory=list)
    historical_precedents_matched: List[HistoricalPrecedent] = Field(default_factory=list)
    bias_analysis: CrossSourceBiasReport
    executive_summary: str
    total_pipeline_duration_ms: float
    graph: Optional[OntologyGraphData] = Field(default=None, description="Knowledge graph for frontend visualization")

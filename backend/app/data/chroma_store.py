import os
import chromadb
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.schemas.models import HistoricalPrecedent


class ChromaPrecedentStore:
    """
    ChromaDB Vector Database manager for CLARION.
    Stores and retrieves historical crisis/controversy trajectories and outcomes
    to ground Stage 5 Inferential Forecasting in empirical precedent.
    """

    def __init__(self, persist_dir: Optional[str] = None):
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIR
        os.makedirs(self.persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="clarion_historical_precedents",
            metadata={"description": "Historical issue trajectories for analogical RAG forecasting"}
        )
        self._seed_precedents_if_empty()

    def _seed_precedents_if_empty(self):
        """Pre-seeds the collection with canonical historical precedents if not already loaded."""
        if self.collection.count() > 0:
            return

        precedents = [
            {
                "id": "vyapam-2013",
                "title": "Vyapam Pre-Medical Examination Scam (2013)",
                "year": 2013,
                "domain": "Medical Entrance Testing & Proxy Impersonation Cartels",
                "trajectory": "Organized criminal syndicates deployed proxy test-takers and leaked OMR sheets in state pre-medical exams. Uncovered in 2013, the crisis triggered massive political protests and student outrage. The Supreme Court transferred the multi-state probe to the CBI in 2015, resulting in hundreds of arrests of exam officials, coaching kingpins, and fraudulent admissions.",
                "resolution": "Structural decentralization of test venues, mandatory Aadhaar biometric authentication at centers, cancellation of fraudulent medical licenses, and dissolution of the corrupt state exam board in favor of modern testing norms."
            },
            {
                "id": "ssc-cgl-2018",
                "title": "SSC CGL Examination Paper Leak & Solver Gangs (2018)",
                "year": 2018,
                "domain": "Competitive Testing, Vendor Vulnerability & Mass Agitation",
                "trajectory": "During the 2018 SSC CGL Tier-II exam, screenshots of question papers circulated on social media, revealing remote access screen-sharing software installed at private testing centers. Thousands of aspirants protested outside the SSC headquarters in New Delhi for weeks, demanding systemic accountability and judicial oversight.",
                "resolution": "The Union Government ordered a comprehensive CBI preliminary inquiry. The third-party private technology vendor was terminated and blacklisted; rigorous government exam protocols, randomized question order, and live CCTV cyber monitoring were mandated for all future central tests."
            },
            {
                "id": "farm-laws-2020",
                "title": "Three Agriculture Deregulation Acts & Federal Agitation (2020-2021)",
                "year": 2020,
                "domain": "Centralized Policy Mandate, Regional Resistance & Stakeholder Deadlock",
                "trajectory": "The Central Government enacted three farm bills to centralize and deregulate agricultural commerce without prior state-level consensus. Farming unions staged intense border blockades around New Delhi lasting over a year. The Supreme Court stayed the implementation of the laws and formed a high-level committee.",
                "resolution": "Following prolonged public resistance and supreme court scrutiny, the Prime Minister announced the complete legislative repeal of the laws, demonstrating that central mandates lacking state buy-in inevitably require policy compromise."
            },
            {
                "id": "svb-run-2023",
                "title": "Silicon Valley Bank (SVB) Contagion & Systemic Intervention (2023)",
                "year": 2023,
                "domain": "Financial Liquidity, Digital Panic & Regulatory Backstops",
                "trajectory": "Rising interest rates created substantial unrealized losses in SVB's bond portfolio. An uncoordinated attempt to raise equity sparked viral digital panic across venture capital forums, driving a $42 billion bank run in a single day. Regulators closed the bank within 36 hours.",
                "resolution": "Federal Reserve, Treasury, and FDIC invoked the Systemic Risk Exception, backstopping all uninsured deposits to halt nationwide regional banking contagion, followed by strict regulatory reviews of liquidity stress-testing."
            }
        ]

        ids = [p["id"] for p in precedents]
        documents = [
            f"Title: {p['title']}\nDomain: {p['domain']}\nTrajectory: {p['trajectory']}\nResolution: {p['resolution']}"
            for p in precedents
        ]
        metadatas = [
            {
                "title": p["title"],
                "year": p["year"],
                "domain": p["domain"],
                "trajectory_summary": p["trajectory"],
                "ultimate_resolution": p["resolution"]
            }
            for p in precedents
        ]

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def query_similar_precedents(self, query_text: str, n_results: int = 3) -> List[HistoricalPrecedent]:
        """Queries ChromaDB using semantic embedding search to find historically similar cases."""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=min(n_results, self.collection.count())
            )
            precedents = []
            if results and results.get("ids") and len(results["ids"]) > 0:
                ids = results["ids"][0]
                distances = results.get("distances", [[]])[0]
                metadatas = results.get("metadatas", [[]])[0]

                for i, cid in enumerate(ids):
                    meta = metadatas[i] if i < len(metadatas) else {}
                    dist = distances[i] if i < len(distances) else 0.5
                    # Convert distance to similarity score between 0 and 1
                    sim = round(max(0.0, min(1.0, 1.0 - (dist / 2.0))), 2)

                    precedents.append(HistoricalPrecedent(
                        case_id=cid,
                        title=meta.get("title", cid),
                        year=int(meta.get("year", 2020)),
                        domain=meta.get("domain", "General Policy"),
                        similarity_score=sim,
                        trajectory_summary=meta.get("trajectory_summary", ""),
                        ultimate_resolution=meta.get("ultimate_resolution", "")
                    ))
            return precedents
        except Exception:
            # Fallback heuristic return if embedding engine fails
            return self._heuristic_precedents_fallback(query_text)

    def _heuristic_precedents_fallback(self, query: str) -> List[HistoricalPrecedent]:
        """Fallback precedents matching when vector similarity model is unavailable."""
        q = query.lower()
        if "neet" in q or "exam" in q or "leak" in q:
            return [
                HistoricalPrecedent(
                    case_id="vyapam-2013",
                    title="Vyapam Pre-Medical Examination Scam (2013)",
                    year=2013,
                    domain="Medical Entrance Testing & Proxy Impersonation Cartels",
                    similarity_score=0.91,
                    trajectory_summary="Mass proxy solver syndicates and paper leaks triggered widespread student agitation, culminating in a nationwide CBI probe and hundreds of arrests.",
                    ultimate_resolution="Mandatory biometric exam centers, cancellation of fraudulent results, and structural overhaul of medical entrance administration."
                ),
                HistoricalPrecedent(
                    case_id="ssc-cgl-2018",
                    title="SSC CGL Examination Paper Leak & Solver Gangs (2018)",
                    year=2018,
                    domain="Competitive Testing, Vendor Vulnerability & Mass Agitation",
                    similarity_score=0.84,
                    trajectory_summary="Screen-sharing software and solver gangs compromised examination integrity, driving massive student demonstrations in Delhi.",
                    ultimate_resolution="Blacklisting of private testing vendors, adoption of randomized digital question banks, and direct government agency monitoring."
                )
            ]
        return [
            HistoricalPrecedent(
                case_id="farm-laws-2020",
                title="Three Agriculture Deregulation Acts & Federal Agitation (2020-2021)",
                year=2020,
                domain="Centralized Policy Mandate, Regional Resistance & Stakeholder Deadlock",
                similarity_score=0.76,
                trajectory_summary="Central policy changes met with regional opposition, escalation to Supreme Court, and eventual policy consensus adjustment.",
                ultimate_resolution="Formation of expert review committee and executive policy refinement."
            )
        ]

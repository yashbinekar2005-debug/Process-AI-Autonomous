import logging
from config import settings

logger = logging.getLogger("enterprise_agent.memory.long_term")

class LongTermMemory:
    """
    Manages vector database storage for enterprise knowledge base documents (RAG).
    Provides semantic search over company documents using ChromaDB,
    falling back to standard text matching if ChromaDB is unavailable.
    """
    def __init__(self):
        self.client = None
        self.collection = None
        self.fallback_db = []
        self._init_db()

    def _init_db(self):
        try:
            import chromadb
            # Initialize persistent client
            self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
            # Create/load collection
            self.collection = self.client.get_or_create_collection(
                name="enterprise_knowledge_base"
            )
            logger.info(f"ChromaDB initialized at path: {settings.CHROMA_DB_PATH}")
            
            # Seed sample database
            if self.collection.count() == 0:
                self.add_documents(
                    documents=[
                        "Enterprise Support SLA: Priority P0 issues must be resolved within 2 hours. P1 issues within 4 hours. P2 issues within 24 hours.",
                        "Competitor SaaS pricing: Alpha Co charges $49/user/month. Beta Inc charges $79/user/month. Gamma Solutions charges $120/user/month.",
                        "Billing Refund Policy: Customers can request a full refund within 14 days of subscription activation. No refunds after 14 days.",
                        "Security Incident Procedure: Any database breach must be reported to security-alerts@enterprise.com within 30 minutes of detection."
                    ],
                    metadatas=[
                        {"source": "sla_policy.txt", "category": "support"},
                        {"source": "market_research.txt", "category": "competitors"},
                        {"source": "refunds.txt", "category": "finance"},
                        {"source": "security_handbook.txt", "category": "compliance"}
                    ],
                    ids=["doc_1", "doc_2", "doc_3", "doc_4"]
                )
                logger.info("ChromaDB seeded with default enterprise files.")
        except Exception as e:
            logger.warning(
                f"Failed to initialize ChromaDB ({str(e)}). "
                f"Activating embedding-free keyword matching memory fallback."
            )
            # Populate fallback
            self.add_documents(
                documents=[
                    "Enterprise Support SLA: Priority P0 issues must be resolved within 2 hours. P1 issues within 4 hours. P2 issues within 24 hours.",
                    "Competitor SaaS pricing: Alpha Co charges $49/user/month. Beta Inc charges $79/user/month. Gamma Solutions charges $120/user/month.",
                    "Billing Refund Policy: Customers can request a full refund within 14 days of subscription activation. No refunds after 14 days.",
                    "Security Incident Procedure: Any database breach must be reported to security-alerts@enterprise.com within 30 minutes of detection."
                ],
                metadatas=[
                    {"source": "sla_policy.txt", "category": "support"},
                    {"source": "market_research.txt", "category": "competitors"},
                    {"source": "refunds.txt", "category": "finance"},
                    {"source": "security_handbook.txt", "category": "compliance"}
                ],
                ids=["doc_1", "doc_2", "doc_3", "doc_4"]
            )

    def add_documents(self, documents: list[str], metadatas: list[dict], ids: list[str]):
        """
        Adds text documents into the memory storage.
        """
        if self.collection:
            try:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
            except Exception as e:
                logger.error(f"Error adding to ChromaDB collection: {str(e)}")
        
        # Always mirror in fallback in case vector DB hits runtime errors
        for d, m, i in zip(documents, metadatas, ids):
            # Avoid duplicate inserts
            if not any(item["id"] == i for item in self.fallback_db):
                self.fallback_db.append({"document": d, "metadata": m, "id": i})

    def search(self, query: str, n_results: int = 2) -> list[str]:
        """
        Searches memory store using semantic similarity or keyword fallback.
        """
        if self.collection:
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results
                )
                if results and "documents" in results and results["documents"]:
                    # Return flat list
                    return [doc for doc_list in results["documents"] for doc in doc_list]
            except Exception as e:
                logger.error(f"ChromaDB search failed, running fallback search. Error: {str(e)}")
        
        # Simple text containment scoring as fallback
        query_words = set(query.lower().split())
        matched = []
        for item in self.fallback_db:
            doc = item["document"]
            doc_lower = doc.lower()
            # Score based on keyword overlaps
            score = sum(1.5 for w in query_words if w in doc_lower)
            if score > 0:
                matched.append((score, doc))
        
        matched.sort(reverse=True, key=lambda x: x[0])
        return [doc for score, doc in matched[:n_results]]

# Export singleton instance
long_term_mem = LongTermMemory()

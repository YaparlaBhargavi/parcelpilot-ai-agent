# src/tools/document_search.py
import logging
from typing import Optional

from src.rag.vector_store import VectorStoreManager


class DocumentSearchTool:
    """Tool for searching documents with priority-based retrieval."""

    def __init__(self):
        print("📚 Initializing DocumentSearchTool...")
        self.vector_store = VectorStoreManager()
        self.vector_store.load_or_create()
        self.document_priority = {
            "customer_agreement": 100,
            "current_policy": 90,
            "current_sop": 85,
            "product_guide": 70,
            "deprecated_policy": 20,
            "historical_ticket": 10,
        }
        self.logger = logging.getLogger(__name__)
        print(f"   ✅ Vector store loaded: {self.vector_store.vectorstore is not None}")

    def search(
        self,
        query: str,
        account_name: Optional[str] = None,
        include_sources: bool = True,
    ) -> dict:
        """Search documents with priority filtering.

        Args:
            query: the search text.
            account_name: if the caller already knows which customer
                account this question concerns (e.g. extracted from the
                user's message), pass it here. When set:
                  - customer_agreement chunks belonging to a *different*
                    customer are dropped entirely, so a highly-similar
                    but wrong-customer agreement can never crowd out or
                    outrank the correct one.
                  - customer_agreement chunks belonging to *this*
                    customer get a relevance boost.
                This is generic (not hardcoded to any specific customer
                name) — it just string-matches account_name against the
                document's source filename / content.
        """
        print(
            f"🔍 DocumentSearchTool.search() called with: '{query}' (account_name={account_name!r})"
        )

        try:
            if not self.vector_store.vectorstore:
                print("   ⚠️ Vector store not initialized, attempting to load...")
                self.vector_store.load_or_create()

                if not self.vector_store.vectorstore:
                    print("   ❌ Vector store still not available")
                    return {"results": [], "conflicts": [], "sources": []}

            print(f"   🔍 Searching vector store...")
            results = self.vector_store.search(query, k=10)

            if not results:
                print(f"   ⚠️ No results found for: {query}")
                return {"results": [], "conflicts": [], "sources": []}

            print(f"   ✅ Found {len(results)} results")

            account_key = account_name.strip().lower() if account_name else None

            prioritized = []
            for doc, score in results:
                priority = doc.metadata.get("priority", 50)
                doc_type = doc.metadata.get("type", "unknown")
                source = doc.metadata.get("source", "Unknown")
                content = doc.page_content

                is_customer_agreement = (
                    doc_type == "customer_agreement" or "agreement" in source.lower()
                )

                if account_key and is_customer_agreement:
                    matches_account = (
                        account_key in source.lower() or account_key in content.lower()
                    )
                    # A customer agreement that clearly belongs to a
                    # DIFFERENT named account than the one being asked
                    # about is not just lower-priority, it's irrelevant
                    # (and actively misleading) — drop it rather than
                    # let vector-similarity smuggle it into the top-3.
                    if not matches_account:
                        continue

                priority_boost = priority / 100
                if account_key and is_customer_agreement:
                    # We already filtered out non-matches above, so any
                    # customer_agreement chunk left here matches the
                    # requested account — boost it further.
                    priority_boost *= 1.5

                adjusted_score = score * (0.8 + 0.2 * priority_boost)

                prioritized.append(
                    {
                        "content": content,
                        "source": source,
                        "type": doc_type,
                        "priority": priority,
                        "score": adjusted_score,
                    }
                )

            # Sort by adjusted score
            prioritized = sorted(prioritized, key=lambda x: x["score"], reverse=True)

            # De-duplicate by source, keeping the highest-scoring chunk
            # per document. Without this, the same source can appear
            # multiple times in the top results (once per matching
            # chunk), crowding out other relevant documents.
            deduped = []
            seen_sources = set()
            for item in prioritized:
                if item["source"] in seen_sources:
                    continue
                seen_sources.add(item["source"])
                deduped.append(item)

            # Check for conflicts
            conflicts = self._detect_conflicts(deduped[:5])

            result_dict = {
                "results": deduped[:3],
                "conflicts": conflicts,
                "sources": [r["source"] for r in deduped[:3]],
            }

            print(f"   📤 Returning {len(result_dict['results'])} results")
            return result_dict

        except Exception as e:
            print(f"   ❌ Search error: {e}")
            import traceback

            traceback.print_exc()
            return {"results": [], "conflicts": [], "sources": []}

    def _detect_conflicts(self, results: list) -> list:
        """Detect policy conflicts between documents."""
        conflicts = []

        if len(results) >= 2:
            for i in range(len(results)):
                for j in range(i + 1, len(results)):
                    if results[i]["type"] != results[j][
                        "type"
                    ] and self._texts_contradict(
                        results[i]["content"], results[j]["content"]
                    ):
                        conflicts.append(
                            {
                                "doc1": results[i]["source"],
                                "doc2": results[j]["source"],
                                "priority1": results[i]["priority"],
                                "priority2": results[j]["priority"],
                                "resolution": self._resolve_conflict(
                                    results[i], results[j]
                                ),
                            }
                        )

        return conflicts

    def _texts_contradict(self, text1: str, text2: str) -> bool:
        """Simple contradiction detection."""
        positive_indicators = [
            "allows",
            "permit",
            "can",
            "yes",
            "allowed",
            "no fee",
            "free",
            "waived",
            "without fee",
        ]
        negative_indicators = [
            "prohibits",
            "cannot",
            "no",
            "restricted",
            "forbidden",
            "fee applies",
            "charge",
        ]

        text1_lower = text1.lower()
        text2_lower = text2.lower()

        has_positive1 = any(word in text1_lower for word in positive_indicators)
        has_negative1 = any(word in text1_lower for word in negative_indicators)
        has_positive2 = any(word in text2_lower for word in positive_indicators)
        has_negative2 = any(word in text2_lower for word in negative_indicators)

        return (has_positive1 and has_negative2) or (has_negative1 and has_positive2)

    def _resolve_conflict(self, doc1: dict, doc2: dict) -> str:
        """Resolve conflicts based on priority."""
        if doc1["priority"] > doc2["priority"]:
            return f"Document {doc1['source']} takes precedence (priority {doc1['priority']})"
        else:
            return f"Document {doc2['source']} takes precedence (priority {doc2['priority']})"

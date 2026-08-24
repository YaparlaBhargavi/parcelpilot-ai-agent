# src/rag/vector_store.py
import shutil
import os
from pathlib import Path
from typing import Optional

try:
    from langchain_community.vectorstores import FAISS
except ImportError:
    from langchain.vectorstores import FAISS

from langchain_core.documents import Document
from langchain.embeddings.base import Embeddings


class DeterministicEmbeddings(Embeddings):
    """Last-resort fallback embeddings — NOT semantic, hash-based only.

    Only used if every real embedding backend (local HuggingFace model,
    optionally OpenAI) fails to initialize. This will not produce
    meaningful similarity search results; it exists purely so the app
    doesn't crash outright.
    """

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        results = []
        for text in texts:
            # Generate deterministic pseudo-embedding vector of dimension 384
            vec = [(hash(text + str(i)) % 1000) / 1000.0 for i in range(384)]
            results.append(vec)
        return results

    def embed_query(self, text: str) -> list[float]:
        return [(hash(text + str(i)) % 1000) / 1000.0 for i in range(384)]


class VectorStoreManager:
    """Manages vector store operations for document retrieval.

    Embedding backend selection (in order):
      1. If use_openai=True is explicitly passed AND OPENAI_API_KEY is set,
         try OpenAIEmbeddings.
      2. Otherwise (the default), use a local HuggingFace sentence-transformer
         model. This runs on your machine, costs nothing, and has no rate
         limits or quota.
      3. If even the local model fails to load (e.g. package not installed),
         fall back to DeterministicEmbeddings as a last resort so the app
         doesn't crash — but note this gives poor-quality, non-semantic
         search results and should be treated as a signal to fix your
         environment (install the missing package), not a real solution.

    IMPORTANT: embeddings from different models are NOT compatible with
    each other. If you previously built vectorstore/faiss_index using
    OpenAIEmbeddings (1536-dim) and now switch to the local model
    (384-dim), you must delete the old index and rebuild it — call
    delete_all() then load_or_create(documents=...) again, or just
    delete the vectorstore/faiss_index folder by hand.
    """

    def __init__(
        self, persist_path: str = "vectorstore/faiss_index", use_openai: bool = False
    ):
        self.persist_path = Path(persist_path)
        self.embeddings = self._init_embeddings(use_openai)
        self.vectorstore = None
        self.documents = []

    def _init_embeddings(self, use_openai: bool) -> Embeddings:
        if use_openai and os.getenv("OPENAI_API_KEY"):
            try:
                try:
                    from langchain_openai import OpenAIEmbeddings
                except ImportError:
                    from langchain_community.embeddings import OpenAIEmbeddings
                print("🔑 Using OpenAI embeddings (subject to quota/rate limits)")
                return OpenAIEmbeddings()
            except Exception as e:
                print(
                    f"⚠️ Could not initialize OpenAI embeddings ({e}); "
                    "falling back to local embeddings"
                )

        try:
            try:
                from langchain_huggingface import HuggingFaceEmbeddings
            except ImportError:
                from langchain_community.embeddings import HuggingFaceEmbeddings
            print(
                "📦 Using local HuggingFace embeddings (all-MiniLM-L6-v2) — "
                "no API calls, no quota limits"
            )
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        except Exception as e:
            print(
                f"❌ Could not load local embeddings ({e}); falling back to "
                "DETERMINISTIC (non-semantic) embeddings"
            )
            print(
                "   ⚠️ Install with: pip install langchain-huggingface sentence-transformers"
            )
            return DeterministicEmbeddings()

    def load_or_create(
        self, documents: Optional[list[Document]] = None
    ) -> Optional[FAISS]:
        """Load existing vector store or create new one."""
        try:
            # Try to load existing vector store
            if self.persist_path.exists():
                self.vectorstore = FAISS.load_local(
                    str(self.persist_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True,
                )
                print(f"✅ Loaded existing vector store from {self.persist_path}")
            else:
                # Create new vector store
                if documents:
                    self.vectorstore = FAISS.from_documents(documents, self.embeddings)
                    self._save()
                    print(
                        f"✅ Created new vector store with {len(documents)} documents"
                    )
                else:
                    print("⚠️ No documents provided and no existing vector store found")
                    self.vectorstore = None
        except (OSError, ValueError, RuntimeError) as e:
            print(f"❌ Error loading vector store: {e}")
            print(
                "   ℹ️ If you recently changed the embedding model, this is likely a "
                "dimension mismatch with the old index. Delete the vectorstore folder "
                "and rebuild it."
            )
            # Create new vector store if loading fails
            if documents:
                self.vectorstore = FAISS.from_documents(documents, self.embeddings)
                self._save()
                print(f"✅ Created new vector store with {len(documents)} documents")
            else:
                self.vectorstore = None

        return self.vectorstore

    def _save(self):
        """Save vector store to disk."""
        if self.vectorstore:
            # Ensure directory exists
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)
            self.vectorstore.save_local(str(self.persist_path))
            print(f"💾 Saved vector store to {self.persist_path}")

    def search(self, query: str, k: int = 5) -> list[tuple[Document, float]]:
        """Search for similar documents."""
        if not self.vectorstore:
            print("⚠️ Vector store not initialized")
            return []

        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            return results
        except (OSError, ValueError, RuntimeError) as e:
            print(f"❌ Error searching vector store: {e}")
            return []

    def search_with_metadata(
        self, query: str, k: int = 5, filter_priority: Optional[int] = None
    ) -> list[tuple[Document, float]]:
        """Search with optional priority filtering."""
        results = self.search(query, k=k * 2)  # Get more results for filtering

        if filter_priority is not None:
            # Filter by priority
            filtered_results = []
            for doc, score in results:
                priority = doc.metadata.get("priority", 0)
                if priority >= filter_priority:
                    filtered_results.append((doc, score))
            results = filtered_results

        # Sort by score and return top k
        results = sorted(results, key=lambda x: x[1], reverse=True)[:k]
        return results

    def add_documents(self, documents: list[Document]):
        """Add new documents to existing vector store."""
        if not self.vectorstore:
            # Create new if doesn't exist
            self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        else:
            # Add to existing
            self.vectorstore.add_documents(documents)

        # Save updated vector store
        self._save()
        print(f"✅ Added {len(documents)} documents to vector store")

    def delete_all(self):
        """Delete all documents from vector store."""
        if self.persist_path.exists():
            shutil.rmtree(self.persist_path)
            print(f"🗑️ Deleted vector store at {self.persist_path}")

        self.vectorstore = None

    def get_stats(self) -> dict:
        """Get statistics about the vector store."""
        stats = {
            "exists": self.persist_path.exists(),
            "path": str(self.persist_path),
            "initialized": self.vectorstore is not None,
        }

        if self.vectorstore and hasattr(self.vectorstore, "index"):
            try:
                stats["index_size"] = (
                    self.vectorstore.index.ntotal
                    if hasattr(self.vectorstore.index, "ntotal")
                    else "unknown"
                )
            except AttributeError:
                stats["index_size"] = "unknown"

        return stats

# test_vectorstore.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("🔍 TESTING VECTOR STORE")
print("=" * 60)

# Test 1: Check imports
print("\n📦 1. Checking imports...")
try:
    import faiss

    print(f"   ✅ FAISS version: {faiss.__version__}")
except ImportError as e:
    print(f"   ❌ FAISS error: {e}")

try:
    from src.rag.vector_store import VectorStoreManager

    print("   ✅ VectorStoreManager imported")
except ImportError as e:
    print(f"   ❌ VectorStoreManager error: {e}")

# Test 2: Load vector store
print("\n📊 2. Loading vector store...")
vs = VectorStoreManager()
vs.load_or_create()

if vs.vectorstore:
    print("   ✅ Vector store loaded successfully")

    # Test 3: Search
    print("\n🔍 3. Testing search...")
    results = vs.search("cancellation policy", k=3)

    if results:
        print(f"   ✅ Found {len(results)} results")
        for doc, score in results[:3]:
            print(f"\n   Score: {score:.3f}")
            print(f"   Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"   Priority: {doc.metadata.get('priority', 'N/A')}")
            print(f"   Preview: {doc.page_content[:100]}...")
    else:
        print("   ❌ No results found - vector store may be empty")
else:
    print("   ❌ Vector store failed to load")

print("\n" + "=" * 60)

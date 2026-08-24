# debug_search.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.tools.document_search import DocumentSearchTool
from src.rag.vector_store import VectorStoreManager

print("=" * 60)
print("🔍 DEBUGGING DOCUMENT SEARCH")
print("=" * 60)

# 1. Check vector store directly
print("\n📊 1. Checking Vector Store directly...")
vs = VectorStoreManager()
vs.load_or_create()

if vs.vectorstore:
    print("   ✅ Vector store is loaded")

    # Test direct search
    print("\n🔍 2. Testing direct search on vector store...")
    results = vs.search("cancellation", k=3)
    if results:
        print(f"   ✅ Found {len(results)} results directly")
        for doc, score in results:
            print(
                f"      • {doc.metadata.get('source', 'Unknown')} (Score: {score:.3f})"
            )
    else:
        print("   ❌ No results from direct search")
else:
    print("   ❌ Vector store is NOT loaded")

# 2. Test DocumentSearchTool
print("\n🔍 3. Testing DocumentSearchTool...")
search_tool = DocumentSearchTool()

# Check if vectorstore is available
if search_tool.vector_store.vectorstore:
    print("   ✅ DocumentSearchTool has vector store")
else:
    print("   ❌ DocumentSearchTool does NOT have vector store")
    # Force load
    search_tool.vector_store.load_or_create()

# Test search
print("\n🔍 4. Testing search through DocumentSearchTool...")
test_queries = ["cancellation", "policy", "Northstar", "SLA"]

for query in test_queries:
    print(f"\n📝 Query: '{query}'")
    results = search_tool.search(query)

    if results and results.get("results"):
        print(f"   ✅ Found {len(results['results'])} results")
        for result in results["results"]:
            print(f"      • {result['source']} (Priority: {result['priority']})")
    else:
        print("   ❌ No results")
        print(f"   Results dict: {results}")

print("\n" + "=" * 60)

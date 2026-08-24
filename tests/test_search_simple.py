# test_search_simple.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.rag.vector_store import VectorStoreManager
from src.tools.document_search import DocumentSearchTool

print("=" * 60)
print("🔍 TESTING DOCUMENT SEARCH")
print("=" * 60)

# 1. Check vector store
print("\n📊 1. Checking Vector Store...")
vs = VectorStoreManager()
vs.load_or_create()

if vs.vectorstore:
    print("✅ Vector store loaded successfully")

    # Try direct search
    print("\n🔍 2. Testing Direct Search...")
    results = vs.search("cancellation policy", k=3)

    if results:
        print(f"✅ Found {len(results)} results")
        for doc, score in results:
            print(f"\n   Score: {score:.3f}")
            print(f"   Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"   Priority: {doc.metadata.get('priority', 'N/A')}")
            print(f"   Preview: {doc.page_content[:100]}...")
    else:
        print("❌ No results found")
else:
    print("❌ Vector store failed to load")

# 3. Test DocumentSearchTool
print("\n🔍 3. Testing DocumentSearchTool...")
search_tool = DocumentSearchTool()

query = "cancellation policy"
print(f"\n📝 Query: '{query}'")
results = search_tool.search(query)

if results and results.get("results"):
    print(f"✅ Found {len(results['results'])} results")
    for result in results["results"]:
        print(f"\n   Source: {result['source']}")
        print(f"   Priority: {result['priority']}")
        print(f"   Preview: {result['content'][:150]}...")
else:
    print("❌ No results from DocumentSearchTool")
    if results:
        print(f"   Results dict: {results}")

print("\n" + "=" * 60)

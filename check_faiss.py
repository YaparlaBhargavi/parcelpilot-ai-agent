# check_faiss.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pickle
import faiss
import numpy as np

print("=" * 60)
print("🔍 CHECKING FAISS INDEX")
print("=" * 60)

faiss_path = Path("vectorstore/faiss_index")

# Check files
print("\n📁 Files in vectorstore:")
for f in faiss_path.parent.glob("*"):
    print(f"   • {f.name} ({f.stat().st_size} bytes)")

# Try loading FAISS directly
print("\n🔍 Attempting to load FAISS index...")
try:
    index = faiss.read_index(str(faiss_path / "index.faiss"))
    print(f"✅ FAISS index loaded")
    print(f"   • Total vectors: {index.ntotal}")
    print(f"   • Dimension: {index.d}")
except Exception as e:
    print(f"❌ Error loading FAISS: {e}")

# Try loading pickle
print("\n🔍 Attempting to load pickle...")
try:
    with open(faiss_path / "index.pkl", "rb") as f:
        data = pickle.load(f)
        print(f"✅ Pickle loaded")
        if isinstance(data, dict):
            print(f"   • Keys: {list(data.keys())}")
        else:
            print(f"   • Type: {type(data)}")
except Exception as e:
    print(f"❌ Error loading pickle: {e}")

print("\n" + "=" * 60)

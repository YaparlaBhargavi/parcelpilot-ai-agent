# src/rag/ingest.py

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.rag.vector_store import VectorStoreManager


class DocumentIngestor:
    """Ingests documents into the vector store."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""],
            length_function=len,
        )
        self.vector_store = VectorStoreManager()

    def process_documents(self, pdf_dir: str = "data/documents") -> list[Document]:
        """Process all PDF documents in the directory."""
        pdf_path = Path(pdf_dir)
        if not pdf_path.exists():
            print(f"❌ Directory not found: {pdf_path}")
            return []

        pdf_files = list(pdf_path.glob("*.pdf"))
        if not pdf_files:
            print(f"❌ No PDF files found in {pdf_path}")
            return []

        print(f"📄 Found {len(pdf_files)} PDF files")

        all_chunks = []

        for pdf_file in sorted(pdf_files):
            print(f"  Processing: {pdf_file.name}")
            try:
                # Check if file size is 0
                if pdf_file.stat().st_size == 0:
                    print(
                        f"    ⚠️ File is empty (0 bytes): {pdf_file.name}. Creating document content placeholder."
                    )
                    documents = [
                        Document(
                            page_content=f"Document: {pdf_file.name}\nType: {self._get_document_type(pdf_file.name)}\nPolicy & SOP documentation details for ParcelPilot logistics.",
                            metadata={"source": pdf_file.name},
                        )
                    ]
                else:
                    # Load PDF
                    loader = PyPDFLoader(str(pdf_file))
                    documents = loader.load()

                # Get document metadata
                priority = self._get_document_priority(pdf_file.name)
                doc_type = self._get_document_type(pdf_file.name)

                # Split into chunks
                chunks = self.text_splitter.split_documents(documents)

                # Add metadata to each chunk
                for chunk in chunks:
                    chunk.metadata.update(
                        {
                            "source": pdf_file.name,
                            "priority": priority,
                            "type": doc_type,
                            "page": chunk.metadata.get("page", 0),
                        }
                    )

                all_chunks.extend(chunks)
                print(f"    ✅ Created {len(chunks)} chunks")

            except Exception as e:
                print(f"    ❌ Error processing {pdf_file.name}: {e}")

        print(f"\n📊 Total chunks created: {len(all_chunks)}")
        return all_chunks

    def _get_document_priority(self, filename: str) -> int:
        """Get priority level based on document type."""
        filename_lower = filename.lower()

        if (
            "enterprise_agreement" in filename_lower
            or "service_agreement" in filename_lower
        ):
            return 100  # Highest priority - customer agreement
        elif "_current" in filename_lower:
            return 90  # Current policy
        elif "sop" in filename_lower:
            return 85  # Standard Operating Procedure
        elif (
            "operations_guide" in filename_lower
            or "product_operations" in filename_lower
        ):
            return 70  # Product/Operations Guide
        elif "_deprecated" in filename_lower:
            return 20  # Deprecated policy
        else:
            return 50  # Default priority

    def _get_document_type(self, filename: str) -> str:
        """Get document type from filename."""
        filename_lower = filename.lower()

        if (
            "enterprise_agreement" in filename_lower
            or "service_agreement" in filename_lower
        ):
            return "customer_agreement"
        elif "_current" in filename_lower:
            return "current_policy"
        elif "sop" in filename_lower:
            return "current_sop"
        elif (
            "operations_guide" in filename_lower
            or "product_operations" in filename_lower
        ):
            return "product_guide"
        elif "_deprecated" in filename_lower:
            return "deprecated_policy"
        else:
            return "other"

    def ingest_all(self, pdf_dir: str = "data/documents") -> bool:
        """Ingest all documents into vector store."""
        chunks = self.process_documents(pdf_dir)

        if not chunks:
            print("❌ No chunks created")
            return False

        # Store in vector database
        self.vector_store.load_or_create(chunks)
        print(f"✅ Successfully ingested {len(chunks)} chunks into vector store")
        return True

    def get_priority_order(self) -> list[str]:
        """Get document priority order for reference."""
        return [
            "customer_agreement (100)",
            "current_policy (90)",
            "current_sop (85)",
            "product_guide (70)",
            "other (50)",
            "deprecated_policy (20)",
        ]


def main():
    """Main function to run ingestion."""
    print("=" * 60)
    print("📚 PARCELPILOT DOCUMENT INGESTION")
    print("=" * 60)

    # Check if data directory exists
    data_dir = Path("data/documents")
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        print("Please create data/documents/ and place your PDF files there")
        return

    # Create ingestor and process
    ingestor = DocumentIngestor()

    # Show document priorities
    print("\n📋 Document Priority Order:")
    for priority in ingestor.get_priority_order():
        print(f"  • {priority}")
    print()

    # Ingest documents
    success = ingestor.ingest_all()

    if success:
        # Show stats
        stats = ingestor.vector_store.get_stats()
        print("\n📊 Vector Store Statistics:")
        for key, value in stats.items():
            print(f"  • {key}: {value}")

    print("\n" + "=" * 60)
    print("✅ Ingestion complete!" if success else "❌ Ingestion failed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

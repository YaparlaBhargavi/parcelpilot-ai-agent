# src/data_explorer.py
from pathlib import Path

import pandas as pd
import pypdf


def explore_data():
    """Explore and understand the data files."""
    print("=" * 60)
    print("📊 PARCELPILOT DATA EXPLORER")
    print("=" * 60)

    # 1. Explore Excel file
    print("\n📁 1. EXPLORING EXCEL DATA")
    print("-" * 40)

    excel_path = Path("data/ParcelPilot_Assessment_Data.xlsx")
    if excel_path.exists():
        try:
            excel_file = pd.ExcelFile(excel_path, engine="openpyxl")
            print(f"✅ Excel file found: {excel_path}")
            print(f"📋 Sheets found: {excel_file.sheet_names}")
            print()

            for sheet_name in excel_file.sheet_names:
                print(f"\n📄 Sheet: {sheet_name}")
                print("-" * 30)
                df = pd.read_excel(excel_path, sheet_name=sheet_name, engine="openpyxl")
                print(f"  • Rows: {len(df)}")
                print(f"  • Columns: {len(df.columns)}")
                print(f"  • Column names: {df.columns.tolist()}")
                print("  • First 3 rows:")
                print(df.head(3).to_string())
                print()
        except Exception as e:
            print(f"❌ Error reading Excel file: {e}")
            print("   Make sure the file is a valid Excel file (.xlsx)")
    else:
        print(f"❌ Excel file not found at: {excel_path}")
        print("   Please place ParcelPilot_Assessment_Data.xlsx in the data/ folder")

    # 2. Explore PDF files
    print("\n📁 2. EXPLORING PDF DOCUMENTS")
    print("-" * 40)

    pdf_dir = Path("data/documents")
    if pdf_dir.exists():
        pdf_files = list(pdf_dir.glob("*.pdf"))
        print(f"📄 Found {len(pdf_files)} PDF files")
        print()

        for pdf_path in sorted(pdf_files):
            print(f"\n📄 PDF: {pdf_path.name}")
            print("-" * 30)
            try:
                with open(pdf_path, "rb") as file:
                    pdf_reader = pypdf.PdfReader(file)
                    num_pages = len(pdf_reader.pages)
                    print(f"  • Pages: {num_pages}")

                    # Extract first page text preview
                    if num_pages > 0:
                        first_page = pdf_reader.pages[0]
                        text = first_page.extract_text()
                        preview = text[:500].replace("\n", " ")
                        print(f"  • First page preview: {preview}...")

                        # Try to identify document type
                        doc_type = identify_document_type(pdf_path.name, text[:1000])
                        print(f"  • Document type: {doc_type}")
            except (OSError, pypdf.errors.PdfReadError) as e:
                print(f"  ❌ Error reading PDF: {e}")
    else:
        print(f"❌ PDF directory not found at: {pdf_dir}")
        print("   Please place PDF files in data/documents/")

    print("\n" + "=" * 60)
    print("✅ Data exploration complete!")
    print("=" * 60)


def identify_document_type(filename, text_sample):
    """Identify document type based on filename and content."""
    filename_lower = filename.lower()
    text_lower = text_sample.lower()

    # Check filename patterns
    if (
        "enterprise_agreement" in filename_lower
        or "service_agreement" in filename_lower
    ):
        return "Customer Agreement"
    elif "_current" in filename_lower:
        return "Current Policy"
    elif "sop" in filename_lower:
        return "SOP (Standard Operating Procedure)"
    elif "operations_guide" in filename_lower:
        return "Product/Operations Guide"
    elif "_deprecated" in filename_lower:
        return "Deprecated Policy"

    # Check content patterns
    if "agreement" in text_lower or "contract" in text_lower:
        return "Customer Agreement"
    elif "policy" in text_lower:
        return "Policy Document"
    elif "sop" in text_lower or "procedure" in text_lower:
        return "SOP"
    elif "guide" in text_lower or "operations" in text_lower:
        return "Guide"

    return "Unknown"


def list_data_structure():
    """Print the expected data structure."""
    print("\n📁 EXPECTED DATA STRUCTURE")
    print("-" * 40)
    print(
        """
parcelpilot-ai-agent/
│
├── data/
│   ├── documents/
│   │   ├── 01_Support_Policy_v3_CURRENT.pdf
│   │   ├── 02_Support_Policy_v2_DEPRECATED.pdf
│   │   ├── 03_Cancellation_and_Service_Credit_SOP_v4.pdf
│   │   ├── 04_Product_Operations_Guide_and_Known_Issues.pdf
│   │   ├── 05_Northstar_Logistics_Enterprise_Agreement.pdf
│   │   └── 06_LumenWorks_Service_Agreement.pdf
│   │
│   └── ParcelPilot_Assessment_Data.xlsx
│
└── vectorstore/
    """
    )

    print("\n📋 EXPECTED EXCEL SHEETS")
    print("-" * 40)
    print(
        """
Common sheet names might include:
• accounts
• orders
• tickets
• customers
• sla (Service Level Agreements)
• contracts
    """
    )


def check_data_files():
    """Check if all required data files exist."""
    print("\n🔍 CHECKING DATA FILES")
    print("-" * 40)

    required_pdfs = [
        "01_Support_Policy_v3_CURRENT.pdf",
        "02_Support_Policy_v2_DEPRECATED.pdf",
        "03_Cancellation_and_Service_Credit_SOP_v4.pdf",
        "04_Product_Operations_Guide_and_Known_Issues.pdf",
        "05_Northstar_Logistics_Enterprise_Agreement.pdf",
        "06_LumenWorks_Service_Agreement.pdf",
    ]

    pdf_dir = Path("data/documents")
    if pdf_dir.exists():
        existing_pdfs = [f.name for f in pdf_dir.glob("*.pdf")]

        print("\n📄 PDF Files:")
        for required_pdf in required_pdfs:
            if required_pdf in existing_pdfs:
                print(f"  ✅ {required_pdf}")
            else:
                print(f"  ❌ {required_pdf} - MISSING")
    else:
        print("❌ data/documents/ directory not found")

    # Check Excel file
    excel_path = Path("data/ParcelPilot_Assessment_Data.xlsx")
    if excel_path.exists():
        print(f"\n📊 Excel file: ✅ {excel_path.name}")
    else:
        print("\n📊 Excel file: ❌ ParcelPilot_Assessment_Data.xlsx - MISSING")


if __name__ == "__main__":
    # Run all checks
    list_data_structure()
    check_data_files()
    explore_data()

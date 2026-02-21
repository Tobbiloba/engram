#!/usr/bin/env python3
"""
Project Engram - The Omni-Reader (ingest.py)

Phase 2: Universal, multi-modal memory system with OCR support.

This script converts documents and images into a "Memory Cartridge" -
a portable vector database that can be plugged into an AI Agent via MCP.

Supported formats:
    - PDF (text-based and scanned/image PDFs with OCR)
    - Text files (.txt, .md)
    - Images (.png, .jpg, .jpeg) - extracts text via OCR

Usage:
    python ingest.py <path_to_file_or_folder>

Examples:
    python ingest.py manual.pdf              # Single PDF
    python ingest.py screenshot.png          # Single image (OCR)
    python ingest.py ./my_documents/         # Entire folder (recursive)
    python ingest.py ./folder -o my_brain    # Custom output name
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

# ============================================================
# GPU DETECTION - Phase 5
# ============================================================

def get_best_device() -> str:
    """Auto-detect the best available device for embeddings."""
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
    except ImportError:
        pass
    return "cpu"

DEVICE = get_best_device()

# ============================================================
# STEP 1: Parse command-line arguments
# ============================================================

parser = argparse.ArgumentParser(
    description="Convert files or folders into a Memory Cartridge (vector database)"
)
parser.add_argument(
    "input_path",
    type=str,
    help="Path to a file or folder to process recursively"
)
parser.add_argument(
    "-o", "--output",
    type=str,
    default=None,
    help="Custom name for the output engram folder (optional)"
)
parser.add_argument(
    "--no-ocr",
    action="store_true",
    help="Disable OCR for scanned PDFs and images (faster but less thorough)"
)
args = parser.parse_args()

# Validate the path exists
input_path = Path(args.input_path)
if not input_path.exists():
    print(f"Error: Path not found: {input_path}")
    sys.exit(1)

# Supported file extensions
TEXT_EXTENSIONS = [".txt", ".md"]
PDF_EXTENSIONS = [".pdf"]
IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]
ALL_EXTENSIONS = TEXT_EXTENSIONS + PDF_EXTENSIONS + IMAGE_EXTENSIONS

# ============================================================
# STEP 2: OCR Helper Functions
# ============================================================

def check_ocr_available() -> bool:
    """Check if OCR dependencies are available."""
    try:
        import pytesseract
        from PIL import Image
        # Test tesseract is installed
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False

def extract_text_from_image(image_path: Path) -> Tuple[str, bool]:
    """
    Extract text from an image using OCR.
    Returns (text, success).
    """
    try:
        import pytesseract
        from PIL import Image

        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip(), True
    except Exception as e:
        return f"OCR failed: {str(e)}", False

def is_pdf_page_scanned(page_text: str) -> bool:
    """
    Detect if a PDF page is likely a scanned image (no selectable text).
    Returns True if the page appears to be scanned/image-based.
    """
    # If page has very little text, it's likely a scan
    stripped = page_text.strip()
    # Less than 50 chars is suspicious for a full page
    if len(stripped) < 50:
        return True
    # If mostly whitespace/special chars, likely OCR garbage or scan
    alphanumeric = sum(c.isalnum() for c in stripped)
    if len(stripped) > 0 and alphanumeric / len(stripped) < 0.5:
        return True
    return False

def ocr_pdf_page(pdf_path: Path, page_num: int) -> Tuple[str, bool]:
    """
    Extract text from a specific PDF page using OCR.
    Returns (text, success).
    """
    try:
        from pdf2image import convert_from_path
        import pytesseract

        # Convert just this page to image
        images = convert_from_path(
            pdf_path,
            first_page=page_num + 1,  # pdf2image is 1-indexed
            last_page=page_num + 1,
            dpi=200  # Balance between quality and speed
        )

        if images:
            text = pytesseract.image_to_string(images[0])
            return text.strip(), True
        return "", False
    except Exception as e:
        return f"OCR failed: {str(e)}", False

# ============================================================
# STEP 3: Collect all files to process
# ============================================================

files_to_process = []

if input_path.is_file():
    # Single file mode
    if input_path.suffix.lower() not in ALL_EXTENSIONS:
        print(f"Error: Unsupported file type '{input_path.suffix}'.")
        print(f"Supported types: {', '.join(ALL_EXTENSIONS)}")
        sys.exit(1)
    files_to_process.append(input_path)
    print(f"Processing single file: {input_path.name}")

elif input_path.is_dir():
    # Folder mode - recursively find all supported files
    print(f"Scanning folder: {input_path}")
    print("-" * 50)

    ext_counts = {}
    for ext in ALL_EXTENSIONS:
        found = list(input_path.rglob(f"*{ext}"))
        # Also check uppercase
        found.extend(list(input_path.rglob(f"*{ext.upper()}")))
        if found:
            ext_counts[ext] = len(found)
            files_to_process.extend(found)

    # Print summary by type
    for ext, count in sorted(ext_counts.items()):
        print(f"   Found {count} {ext} files")

    # Remove duplicates and sort
    files_to_process = sorted(set(files_to_process))

    if not files_to_process:
        print(f"\nError: No supported files found in {input_path}")
        print(f"Supported types: {', '.join(ALL_EXTENSIONS)}")
        sys.exit(1)

    print(f"\nTotal files to process: {len(files_to_process)}")

print("-" * 50)

# Check OCR availability
OCR_ENABLED = not args.no_ocr and check_ocr_available()
if OCR_ENABLED:
    print("OCR: Enabled (can read scanned documents and images)")
else:
    if args.no_ocr:
        print("OCR: Disabled by user (--no-ocr flag)")
    else:
        print("OCR: Not available (install pytesseract and tesseract)")
    print("     Scanned PDFs and images will be skipped or have limited text.")

print("-" * 50)

# ============================================================
# STEP 4: Load all documents
# ============================================================

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

all_documents = []
successful_files = 0
failed_files = []
ocr_pages = 0
image_files_processed = 0

print("\nLoading documents...")

for i, file_path in enumerate(files_to_process, 1):
    file_ext = file_path.suffix.lower()
    relative_path = file_path.name

    try:
        # --------------------------------------------------------
        # Handle PDF files (with OCR fallback for scanned pages)
        # --------------------------------------------------------
        if file_ext in PDF_EXTENSIONS:
            loader = PyPDFLoader(str(file_path))
            docs = loader.load()

            processed_docs = []
            pages_ocrd = 0

            for page_idx, doc in enumerate(docs):
                # Check if this page needs OCR
                if OCR_ENABLED and is_pdf_page_scanned(doc.page_content):
                    # Try OCR on this page
                    ocr_text, success = ocr_pdf_page(file_path, page_idx)
                    if success and len(ocr_text.strip()) > 50:
                        doc.page_content = ocr_text
                        doc.metadata["source_type"] = "scanned_pdf"
                        doc.metadata["ocr_applied"] = True
                        pages_ocrd += 1
                    else:
                        doc.metadata["source_type"] = "pdf_low_text"
                        doc.metadata["ocr_applied"] = False
                else:
                    doc.metadata["source_type"] = "pdf_text"
                    doc.metadata["ocr_applied"] = False

                doc.metadata["source_file"] = str(file_path)
                processed_docs.append(doc)

            all_documents.extend(processed_docs)
            ocr_pages += pages_ocrd

            status = f"{len(docs)} pages"
            if pages_ocrd > 0:
                status += f", {pages_ocrd} OCR'd"
            print(f"   [{i}/{len(files_to_process)}] {relative_path} ({status})")

        # --------------------------------------------------------
        # Handle text files (.txt, .md)
        # --------------------------------------------------------
        elif file_ext in TEXT_EXTENSIONS:
            loader = TextLoader(str(file_path), encoding="utf-8")
            docs = loader.load()

            for doc in docs:
                doc.metadata["source_file"] = str(file_path)
                doc.metadata["source_type"] = "text"
                doc.metadata["ocr_applied"] = False

            all_documents.extend(docs)
            char_count = sum(len(d.page_content) for d in docs)
            print(f"   [{i}/{len(files_to_process)}] {relative_path} ({char_count} chars)")

        # --------------------------------------------------------
        # Handle image files (.png, .jpg, etc.) - OCR required
        # --------------------------------------------------------
        elif file_ext in IMAGE_EXTENSIONS:
            if not OCR_ENABLED:
                print(f"   [{i}/{len(files_to_process)}] {relative_path} - SKIPPED (OCR disabled)")
                continue

            text, success = extract_text_from_image(file_path)

            if success and len(text.strip()) > 10:
                doc = Document(
                    page_content=text,
                    metadata={
                        "source_file": str(file_path),
                        "source_type": "image",
                        "ocr_applied": True
                    }
                )
                all_documents.append(doc)
                image_files_processed += 1
                print(f"   [{i}/{len(files_to_process)}] {relative_path} (OCR: {len(text)} chars)")
            else:
                print(f"   [{i}/{len(files_to_process)}] {relative_path} - NO TEXT FOUND")
                continue

        successful_files += 1

    except Exception as e:
        failed_files.append((file_path, str(e)))
        print(f"   [{i}/{len(files_to_process)}] {relative_path} - FAILED: {str(e)[:50]}")

print(f"\nLoaded {successful_files} files successfully")
if ocr_pages > 0:
    print(f"   OCR applied to {ocr_pages} scanned PDF pages")
if image_files_processed > 0:
    print(f"   Extracted text from {image_files_processed} images")
if failed_files:
    print(f"Failed to load {len(failed_files)} files")

if not all_documents:
    print("Error: No documents were loaded successfully.")
    sys.exit(1)

# ============================================================
# STEP 5: Split text into chunks
# ============================================================

print("\nSplitting text into chunks...")

from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

# Split all documents into chunks
chunks = text_splitter.split_documents(all_documents)

print(f"   Created {len(chunks)} text chunks")
print(f"   (chunk size: 1000 chars, overlap: 200 chars)")

# ============================================================
# STEP 6: Generate embeddings using local model
# ============================================================

print("\nLoading embedding model...")
print("   (This may take a moment on first run as the model downloads)")

from langchain_huggingface import HuggingFaceEmbeddings

print(f"   Using device: {DEVICE}")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": DEVICE},
    encode_kwargs={"normalize_embeddings": True}
)

print("   Embedding model loaded")

# ============================================================
# STEP 7: Create FAISS vector store and save
# ============================================================

print("\nCreating vector database...")
print(f"   Embedding {len(chunks)} chunks (this may take a while for large datasets)...")

from langchain_community.vectorstores import FAISS

vector_store = FAISS.from_documents(
    documents=chunks,
    embedding=embeddings
)

print("   Vector database created")

# Determine output folder name
if args.output:
    output_folder = args.output
else:
    output_folder = input_path.stem + "_engram"

output_path = Path(output_folder)

# Save the FAISS index
print(f"\nSaving Memory Cartridge to: {output_folder}/")
vector_store.save_local(str(output_path))

# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 50)
print("MEMORY CARTRIDGE CREATED SUCCESSFULLY!")
print("=" * 50)

# Count source types
source_types = {}
for doc in all_documents:
    st = doc.metadata.get("source_type", "unknown")
    source_types[st] = source_types.get(st, 0) + 1

print(f"\n   Indexed {successful_files} files")
print(f"   Total chunks: {len(chunks)}")
print(f"   Location: {output_path.absolute()}")

print(f"\n   Source breakdown:")
for st, count in sorted(source_types.items()):
    label = {
        "pdf_text": "PDF (text)",
        "scanned_pdf": "PDF (scanned/OCR)",
        "pdf_low_text": "PDF (low text)",
        "text": "Text files",
        "image": "Images (OCR)"
    }.get(st, st)
    print(f"      - {label}: {count} pages/docs")

if failed_files:
    print(f"\n   Skipped {len(failed_files)} files due to errors:")
    for f, err in failed_files[:5]:
        print(f"      - {f.name}: {err[:40]}...")
    if len(failed_files) > 5:
        print(f"      ... and {len(failed_files) - 5} more")

print(f"\nNext step: Run the server with:")
print(f"   python server.py {output_folder}")

#!/usr/bin/env python3
"""
Engram Ingest Module - Convert files into a Memory Cartridge.

Supports: PDF, text, code, config files, images (with OCR)
"""

import sys
from pathlib import Path
from typing import List, Tuple, Optional

# File extensions
TEXT_EXTENSIONS = [".txt", ".md", ".rst"]
CODE_EXTENSIONS = [
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".go", ".rs", ".c", ".cpp", ".h",
    ".rb", ".php", ".swift", ".kt", ".scala",
    ".html", ".css", ".scss", ".json", ".yaml", ".yml",
    ".toml", ".xml", ".sql", ".sh", ".bash"
]
PDF_EXTENSIONS = [".pdf"]
IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]
ALL_EXTENSIONS = TEXT_EXTENSIONS + CODE_EXTENSIONS + PDF_EXTENSIONS + IMAGE_EXTENSIONS


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


def check_ocr_available() -> bool:
    """Check if OCR dependencies are available."""
    try:
        import pytesseract
        from PIL import Image
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def extract_text_from_image(image_path: Path) -> Tuple[str, bool]:
    """Extract text from an image using OCR."""
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip(), True
    except Exception as e:
        return f"OCR failed: {str(e)}", False


def is_pdf_page_scanned(page_text: str) -> bool:
    """Detect if a PDF page is likely a scanned image."""
    stripped = page_text.strip()
    if len(stripped) < 50:
        return True
    alphanumeric = sum(c.isalnum() for c in stripped)
    if len(stripped) > 0 and alphanumeric / len(stripped) < 0.5:
        return True
    return False


def ocr_pdf_page(pdf_path: Path, page_num: int) -> Tuple[str, bool]:
    """Extract text from a specific PDF page using OCR."""
    try:
        from pdf2image import convert_from_path
        import pytesseract
        images = convert_from_path(
            pdf_path,
            first_page=page_num + 1,
            last_page=page_num + 1,
            dpi=200
        )
        if images:
            text = pytesseract.image_to_string(images[0])
            return text.strip(), True
        return "", False
    except Exception as e:
        return f"OCR failed: {str(e)}", False


def run_ingest(
    input_path: str,
    output_name: Optional[str] = None,
    use_ocr: bool = True,
    quiet: bool = False
) -> bool:
    """
    Main ingest function - index files into a memory cartridge.

    Args:
        input_path: Path to file or folder to index
        output_name: Name for output engram folder
        use_ocr: Whether to use OCR for scanned docs
        quiet: Suppress output

    Returns:
        True if successful, False otherwise
    """
    from langchain_community.document_loaders import PyPDFLoader, TextLoader
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS

    def log(msg):
        if not quiet:
            print(msg)

    input_path = Path(input_path)
    if not input_path.exists():
        log(f"Error: Path not found: {input_path}")
        return False

    DEVICE = get_best_device()
    OCR_ENABLED = use_ocr and check_ocr_available()

    # Collect files
    files_to_process = []

    if input_path.is_file():
        if input_path.suffix.lower() not in ALL_EXTENSIONS:
            log(f"Error: Unsupported file type '{input_path.suffix}'")
            return False
        files_to_process.append(input_path)
        log(f"Processing single file: {input_path.name}")

    elif input_path.is_dir():
        log(f"Scanning folder: {input_path}")

        for ext in ALL_EXTENSIONS:
            found = list(input_path.rglob(f"*{ext}"))
            found.extend(list(input_path.rglob(f"*{ext.upper()}")))
            files_to_process.extend(found)

        # Remove duplicates and sort
        files_to_process = sorted(set(files_to_process))

        # Filter out hidden files and common excludes
        files_to_process = [
            f for f in files_to_process
            if not any(part.startswith('.') for part in f.parts)
            and 'node_modules' not in f.parts
            and '__pycache__' not in f.parts
            and 'venv' not in f.parts
            and '.git' not in f.parts
        ]

        if not files_to_process:
            log(f"Error: No supported files found in {input_path}")
            return False

        log(f"Found {len(files_to_process)} files to process")

    # Load documents
    all_documents = []
    successful_files = 0
    failed_files = []

    log(f"\nIndexing {len(files_to_process)} files...")

    for i, file_path in enumerate(files_to_process, 1):
        file_ext = file_path.suffix.lower()

        if not quiet and i % 10 == 0:
            print(f"  Progress: {i}/{len(files_to_process)}", end="\r")

        try:
            # PDF files
            if file_ext in PDF_EXTENSIONS:
                loader = PyPDFLoader(str(file_path))
                docs = loader.load()

                for doc in docs:
                    doc.metadata["source_file"] = str(file_path)
                    doc.metadata["source_type"] = "pdf"

                    # OCR fallback for scanned pages
                    if OCR_ENABLED and is_pdf_page_scanned(doc.page_content):
                        page_num = doc.metadata.get("page", 0)
                        ocr_text, success = ocr_pdf_page(file_path, page_num)
                        if success and len(ocr_text) > len(doc.page_content):
                            doc.page_content = ocr_text
                            doc.metadata["source_type"] = "pdf_ocr"

                all_documents.extend(docs)
                successful_files += 1

            # Text and code files
            elif file_ext in TEXT_EXTENSIONS + CODE_EXTENSIONS:
                try:
                    loader = TextLoader(str(file_path), encoding="utf-8")
                    docs = loader.load()
                except:
                    # Try with different encoding
                    loader = TextLoader(str(file_path), encoding="latin-1")
                    docs = loader.load()

                for doc in docs:
                    doc.metadata["source_file"] = str(file_path)
                    doc.metadata["source_type"] = "code" if file_ext in CODE_EXTENSIONS else "text"
                    doc.metadata["file_extension"] = file_ext

                all_documents.extend(docs)
                successful_files += 1

            # Image files (OCR)
            elif file_ext in IMAGE_EXTENSIONS and OCR_ENABLED:
                text, success = extract_text_from_image(file_path)
                if success and text.strip():
                    doc = Document(
                        page_content=text,
                        metadata={
                            "source_file": str(file_path),
                            "source_type": "image_ocr"
                        }
                    )
                    all_documents.append(doc)
                    successful_files += 1

        except Exception as e:
            failed_files.append((file_path, str(e)))

    if not all_documents:
        log("Error: No documents were loaded successfully.")
        return False

    log(f"\nLoaded {successful_files} files successfully")

    # Split into chunks
    log("Splitting text into chunks...")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    chunks = text_splitter.split_documents(all_documents)
    log(f"Created {len(chunks)} text chunks")

    # Create embeddings
    log(f"Creating embeddings (device: {DEVICE})...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": DEVICE},
        encode_kwargs={"normalize_embeddings": True}
    )

    # Create vector store
    log("Building vector database...")

    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    # Determine output folder
    if output_name:
        output_folder = output_name
    else:
        output_folder = input_path.name + "_engram"

    output_path = Path(output_folder)

    # Save
    log(f"Saving to: {output_folder}/")
    vector_store.save_local(str(output_path))

    log(f"\n✓ Memory cartridge created!")
    log(f"  Files indexed: {successful_files}")
    log(f"  Chunks: {len(chunks)}")
    log(f"  Location: {output_path.absolute()}")

    if failed_files:
        log(f"\n  Skipped {len(failed_files)} files due to errors")

    return True


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert files or folders into a Memory Cartridge"
    )
    parser.add_argument(
        "input_path",
        type=str,
        help="Path to a file or folder to process"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Custom name for the output engram folder"
    )
    parser.add_argument(
        "--no-ocr",
        action="store_true",
        help="Disable OCR for scanned PDFs and images"
    )
    args = parser.parse_args()

    success = run_ingest(
        args.input_path,
        args.output,
        use_ocr=not args.no_ocr
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Project Engram - The Ghost v2: Incremental & Resumable

Smart features:
- Processes files in small batches (100 at a time)
- Saves progress after EACH batch
- Resumes exactly where it left off
- Never loses work
- Only processes new/changed files

Usage:
    python ghost.py                     # Watch ~/ with defaults
    python ghost.py ~/Documents         # Watch specific folder
    python ghost.py -o brain_engram     # Custom engram name
"""

import argparse
import sys
import time
import json
import hashlib
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set

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
# CONFIGURATION
# ============================================================

BATCH_SIZE = 100  # Process 100 files, then save
DEBOUNCE_SECONDS = 2.0
MIN_REBUILD_INTERVAL = 10.0
MAX_FILE_SIZE_MB = 50

# Folders to ignore
IGNORED_FOLDERS = {
    "library", "appdata", "applications", ".trash", ".trashes",
    "node_modules", ".npm", ".yarn", "venv", "env", ".venv",
    "__pycache__", ".pytest_cache", ".git", ".svn",
    ".vscode", ".idea", "vendor", ".cargo", ".rustup",
    "build", "dist", "out", "target", ".next", ".nuxt",
    ".cache", "cache", ".tmp", "tmp", ".local", ".config",
    ".dropbox", ".docker", ".kube", "pods",
    ".spotlight-v100", ".fseventsd", ".documentrevisions-v100",
}

# Extensions to ignore
IGNORED_EXTENSIONS = {
    ".ds_store", ".log", ".tmp", ".temp", ".swp",
    ".exe", ".dll", ".so", ".dylib", ".o", ".pyc",
    ".dmg", ".iso", ".pkg", ".zip", ".tar", ".gz", ".rar",
    ".db", ".sqlite", ".lock",
}

# Extensions to index
INDEXED_EXTENSIONS = {
    ".pdf", ".txt", ".md", ".rst",
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".go", ".rs", ".c", ".cpp", ".h",
    ".rb", ".php", ".swift",
    ".html", ".css", ".json", ".yaml", ".yml",
    ".sql", ".sh", ".bash",
    ".png", ".jpg", ".jpeg",  # OCR
}

# ============================================================
# LOGGING
# ============================================================

def log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = {
        "INFO": "👻", "CHANGE": "📝", "BUILD": "🔨",
        "SUCCESS": "✅", "ERROR": "❌", "WATCH": "👁️",
        "SKIP": "⏭️", "SCAN": "🔍", "SAVE": "💾",
        "RESUME": "▶️", "BATCH": "📦",
    }.get(level, "  ")
    print(f"[{timestamp}] {prefix} {message}", flush=True)

# ============================================================
# FILE REGISTRY - Tracks what's been processed
# ============================================================

class FileRegistry:
    """Tracks which files have been processed."""

    def __init__(self, engram_path: Path):
        self.registry_file = engram_path / "registry.json"
        self.data: Dict[str, dict] = {}
        self.load()

    def load(self):
        if self.registry_file.exists():
            try:
                self.data = json.loads(self.registry_file.read_text())
                log(f"Loaded registry: {len(self.data)} files tracked", "RESUME")
            except:
                self.data = {}

    def save(self):
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        self.registry_file.write_text(json.dumps(self.data, indent=2))

    def get_file_hash(self, path: Path) -> str:
        """Quick hash based on path + size + mtime."""
        try:
            stat = path.stat()
            return hashlib.md5(f"{path}:{stat.st_size}:{stat.st_mtime}".encode()).hexdigest()
        except:
            return ""

    def needs_processing(self, path: Path) -> bool:
        """Check if file is new or changed."""
        path_str = str(path)
        current_hash = self.get_file_hash(path)

        if path_str not in self.data:
            return True
        if self.data[path_str].get("hash") != current_hash:
            return True
        return False

    def mark_processed(self, path: Path):
        """Mark file as processed."""
        self.data[str(path)] = {
            "hash": self.get_file_hash(path),
            "processed_at": datetime.now().isoformat()
        }

    def get_deleted_files(self, current_files: Set[Path]) -> List[str]:
        """Find files in registry that no longer exist."""
        current_paths = {str(p) for p in current_files}
        return [p for p in self.data.keys() if p not in current_paths]

# ============================================================
# SMART FILTERING
# ============================================================

def should_ignore_path(path: Path) -> bool:
    path_parts = [p.lower() for p in path.parts]
    for part in path_parts:
        if part in IGNORED_FOLDERS:
            return True
        if part.startswith(".") and len(part) > 1:
            return True
    return False

def should_ignore_file(file_path: Path) -> bool:
    name = file_path.name.lower()
    suffix = file_path.suffix.lower()

    if suffix in IGNORED_EXTENSIONS:
        return True
    if suffix not in INDEXED_EXTENSIONS:
        return True

    try:
        if file_path.stat().st_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            return True
    except:
        return True

    return False

def is_valid_file(path: Path) -> bool:
    if should_ignore_path(path):
        return False
    if should_ignore_file(path):
        return False
    return True

# ============================================================
# INCREMENTAL BUILDER
# ============================================================

class IncrementalBuilder:
    """Builds index incrementally, saves after each batch."""

    def __init__(self, watch_folder: Path, engram_name: str):
        self.watch_folder = watch_folder
        self.engram_path = Path(engram_name)
        self.engram_path.mkdir(parents=True, exist_ok=True)

        self.registry = FileRegistry(self.engram_path)
        self.embeddings = None
        self.vector_store = None
        self.building = False
        self.lock = threading.Lock()

    def _load_embeddings(self):
        if self.embeddings is None:
            log(f"Loading embedding model on {DEVICE}...", "BUILD")
            from langchain_huggingface import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": DEVICE},
                encode_kwargs={"normalize_embeddings": True}
            )
            log(f"Embedding model ready ({DEVICE})", "SUCCESS")

    def _load_existing_index(self):
        """Load existing FAISS index if it exists."""
        index_file = self.engram_path / "index.faiss"
        if index_file.exists():
            try:
                from langchain_community.vectorstores import FAISS
                self.vector_store = FAISS.load_local(
                    str(self.engram_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                log(f"Loaded existing index from {self.engram_path}", "RESUME")
                return True
            except Exception as e:
                log(f"Could not load existing index: {e}", "ERROR")
        return False

    def _check_ocr(self) -> bool:
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            return True
        except:
            return False

    def _process_file(self, file_path: Path, ocr_available: bool) -> list:
        """Process a single file and return documents."""
        from langchain_community.document_loaders import PyPDFLoader, TextLoader
        from langchain_core.documents import Document

        ext = file_path.suffix.lower()
        docs = []

        try:
            if ext == ".pdf":
                loader = PyPDFLoader(str(file_path))
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source_file"] = str(file_path)
                    doc.metadata["source_type"] = "pdf"

            elif ext in {".png", ".jpg", ".jpeg"}:
                if ocr_available:
                    import pytesseract
                    from PIL import Image
                    text = pytesseract.image_to_string(Image.open(file_path)).strip()
                    if len(text) > 10:
                        docs = [Document(
                            page_content=text,
                            metadata={"source_file": str(file_path), "source_type": "image"}
                        )]

            else:  # Text/code files
                try:
                    loader = TextLoader(str(file_path), encoding="utf-8")
                    docs = loader.load()
                except:
                    loader = TextLoader(str(file_path), encoding="latin-1")
                    docs = loader.load()

                for doc in docs:
                    doc.metadata["source_file"] = str(file_path)
                    doc.metadata["source_type"] = "code" if ext in {".py", ".js", ".ts"} else "text"

        except Exception as e:
            pass  # Skip failed files silently

        return docs

    def collect_files(self) -> List[Path]:
        """Collect all valid files."""
        files = []
        for ext in INDEXED_EXTENSIONS:
            try:
                for f in self.watch_folder.rglob(f"*{ext}"):
                    if is_valid_file(f):
                        files.append(f)
            except PermissionError:
                continue
        return sorted(set(files))

    def build(self) -> bool:
        """Build index incrementally with batch saves."""
        with self.lock:
            if self.building:
                return False
            self.building = True

        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            from langchain_community.vectorstores import FAISS

            log("Starting incremental build...", "BUILD")

            # Load embeddings
            self._load_embeddings()

            # Load existing index
            self._load_existing_index()

            # Collect files
            all_files = self.collect_files()
            log(f"Found {len(all_files)} total files", "SCAN")

            # Filter to only new/changed files
            files_to_process = [f for f in all_files if self.registry.needs_processing(f)]
            log(f"Need to process {len(files_to_process)} new/changed files", "SCAN")

            if not files_to_process and self.vector_store:
                log("Nothing new to process", "SUCCESS")
                self.building = False
                return True

            # Process in batches
            ocr_available = self._check_ocr()
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

            total_batches = (len(files_to_process) + BATCH_SIZE - 1) // BATCH_SIZE
            total_chunks = 0

            for batch_num in range(total_batches):
                start_idx = batch_num * BATCH_SIZE
                end_idx = min(start_idx + BATCH_SIZE, len(files_to_process))
                batch_files = files_to_process[start_idx:end_idx]

                log(f"Batch {batch_num + 1}/{total_batches}: Processing {len(batch_files)} files...", "BATCH")

                # Process batch
                all_docs = []
                for file_path in batch_files:
                    docs = self._process_file(file_path, ocr_available)
                    all_docs.extend(docs)
                    self.registry.mark_processed(file_path)

                if not all_docs:
                    continue

                # Chunk
                chunks = splitter.split_documents(all_docs)
                total_chunks += len(chunks)

                # Add to index
                if self.vector_store is None:
                    self.vector_store = FAISS.from_documents(chunks, self.embeddings)
                else:
                    batch_store = FAISS.from_documents(chunks, self.embeddings)
                    self.vector_store.merge_from(batch_store)

                # SAVE after each batch!
                self.vector_store.save_local(str(self.engram_path))
                self.registry.save()

                log(f"Batch {batch_num + 1} complete: +{len(chunks)} chunks (saved!)", "SAVE")

            log(f"Build complete: {len(files_to_process)} files, {total_chunks} chunks", "SUCCESS")
            return True

        except Exception as e:
            log(f"Build error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False

        finally:
            self.building = False

# ============================================================
# FILE WATCHER
# ============================================================

class GhostHandler:
    def __init__(self, builder: IncrementalBuilder):
        self.builder = builder
        self.timer: Optional[threading.Timer] = None
        self.lock = threading.Lock()

    def _should_process(self, path: str) -> bool:
        return is_valid_file(Path(path))

    def _schedule_rebuild(self):
        with self.lock:
            if self.timer:
                self.timer.cancel()
            self.timer = threading.Timer(DEBOUNCE_SECONDS, self.builder.build)
            self.timer.start()

    def on_any_event(self, event):
        if not event.is_directory and self._should_process(event.src_path):
            log(f"Changed: {Path(event.src_path).name}", "CHANGE")
            self._schedule_rebuild()

# ============================================================
# GhostWatcher class for CLI import
# ============================================================

class GhostWatcher:
    """Wrapper class for CLI integration."""

    def __init__(self, watch_folder: str, output: str):
        self.watch_folder = Path(watch_folder).expanduser().resolve()
        self.output = output

    def run(self):
        """Start the watcher."""
        if not self.watch_folder.exists():
            log(f"Folder not found: {self.watch_folder}", "ERROR")
            return

        print()
        print("=" * 60)
        print("ENGRAM WATCHER - Incremental & Resumable")
        print("=" * 60)
        print(f"   Watching:    {self.watch_folder}")
        print(f"   Engram:      {self.output}")
        print(f"   Batch size:  {BATCH_SIZE} files")
        print(f"   Device:      {DEVICE} {'(GPU accelerated!)' if DEVICE != 'cpu' else '(CPU)'}")
        print(f"   Saves:       After EVERY batch (never loses work!)")
        print("=" * 60)
        print()

        builder = IncrementalBuilder(self.watch_folder, self.output)

        # Initial build
        builder.build()

        # Watch for changes
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        class Handler(FileSystemEventHandler):
            def __init__(self, builder):
                self.ghost = GhostHandler(builder)

            def on_created(self, event):
                self.ghost.on_any_event(event)

            def on_modified(self, event):
                self.ghost.on_any_event(event)

            def on_deleted(self, event):
                self.ghost.on_any_event(event)

        observer = Observer()
        observer.schedule(Handler(builder), str(self.watch_folder), recursive=True)
        observer.start()

        log(f"Watching for changes... (Ctrl+C to stop)", "WATCH")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            log("Shutting down...", "INFO")
            observer.stop()
            observer.join()


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="The Ghost v2 - Incremental & Resumable")
    parser.add_argument("watch_folder", nargs="?", default=str(Path.home()),
                        help="Folder to watch (default: home)")
    parser.add_argument("-o", "--output", default="brain_engram",
                        help="Engram name (default: brain_engram)")
    parser.add_argument("--no-watch", action="store_true",
                        help="Just build once, don't watch for changes")
    args = parser.parse_args()

    watch_folder = Path(args.watch_folder).expanduser().resolve()

    if not watch_folder.exists():
        log(f"Folder not found: {watch_folder}", "ERROR")
        sys.exit(1)

    print()
    print("=" * 60)
    print("👻 THE GHOST v2 - Incremental & Resumable")
    print("=" * 60)
    print(f"   Watching:    {watch_folder}")
    print(f"   Engram:      {args.output}")
    print(f"   Batch size:  {BATCH_SIZE} files")
    print(f"   Device:      {DEVICE} {'(GPU accelerated!)' if DEVICE != 'cpu' else '(CPU)'}")
    print(f"   Saves:       After EVERY batch (never loses work!)")
    print("=" * 60)
    print()

    builder = IncrementalBuilder(watch_folder, args.output)

    # Initial build
    builder.build()

    if args.no_watch:
        log("Build complete. Exiting (--no-watch)", "SUCCESS")
        return

    # Watch for changes
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        class Handler(FileSystemEventHandler):
            def __init__(self, builder):
                self.ghost = GhostHandler(builder)

            def on_created(self, event):
                self.ghost.on_any_event(event)

            def on_modified(self, event):
                self.ghost.on_any_event(event)

            def on_deleted(self, event):
                self.ghost.on_any_event(event)

        observer = Observer()
        observer.schedule(Handler(builder), str(watch_folder), recursive=True)
        observer.start()

        log(f"Watching for changes... (Ctrl+C to stop)", "WATCH")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        log("Shutting down...", "INFO")
        observer.stop()
        observer.join()

if __name__ == "__main__":
    main()

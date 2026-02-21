# Project Engram - Improvement Roadmap

> Tracking all planned improvements, organized by phases.

---

## Current State (Baseline)

- **Model**: `all-MiniLM-L6-v2` (384 dimensions, CPU-only)
- **Processing**: Sequential file loading, batched embedding (100 files/batch)
- **Storage**: Single FAISS index per cartridge
- **Index Size**: 646,403 chunks from 48,000+ files
- **Full Reindex Time**: ~2+ hours on CPU

---

## Phase 5: GPU Acceleration

**Goal**: Speed up embedding generation by 5-10x

**Priority**: HIGH (biggest performance win)

**Changes**:

| File | Change |
|------|--------|
| `ingest.py` | Add MPS/CUDA device detection |
| `ghost.py` | Add MPS/CUDA device detection |

**Implementation**:
```python
# Auto-detect best available device
import torch

def get_device():
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"

# Use in embeddings
model_kwargs={"device": get_device()}
```

**Expected Results**:
- CPU: ~2+ hours for 646K chunks
- MPS (Apple Silicon): ~15-30 minutes
- CUDA (NVIDIA): ~10-20 minutes

**Dependencies**:
```
torch>=2.0.0
```

**Status**: [x] COMPLETE

**Files Changed**:
- `ingest.py` - Added `get_best_device()` function, uses DEVICE variable
- `ghost.py` - Added `get_best_device()` function, uses DEVICE variable

---

## Phase 6: Parallel File Loading

**Goal**: Load multiple files simultaneously while embedding

**Priority**: MEDIUM

**Changes**:

| File | Change |
|------|--------|
| `ghost.py` | Add ThreadPoolExecutor for file loading |
| `ingest.py` | Add ThreadPoolExecutor for file loading |

**Implementation**:
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_files_parallel(file_paths, max_workers=4):
    """Load multiple files simultaneously."""
    documents = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_path = {
            executor.submit(load_single_file, path): path
            for path in file_paths
        }

        for future in as_completed(future_to_path):
            path = future_to_path[future]
            try:
                docs = future.result()
                documents.extend(docs)
            except Exception as e:
                print(f"Error loading {path}: {e}")

    return documents
```

**Expected Results**:
- File loading: 3-4x faster
- Works best with SSDs
- Combines well with GPU acceleration

**Status**: [ ] Not Started

---

## Phase 7: Smarter Chunking

**Goal**: Improve search quality with better text splitting

**Priority**: MEDIUM

**Current Approach**:
- Fixed 1000 characters per chunk
- 200 character overlap
- No awareness of content structure

**Improvements**:

### 7a. Semantic Chunking
Split by meaning, not character count:
```python
from langchain_experimental.text_splitter import SemanticChunker

text_splitter = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile"
)
```

### 7b. Code-Aware Chunking
For source code files:
```python
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    Language
)

python_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=1000,
    chunk_overlap=200
)
```

### 7c. Document Structure Awareness
Respect headers, paragraphs, code blocks:
```python
from langchain_text_splitters import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on
)
```

**Status**: [ ] Not Started

---

## Phase 8: Hybrid Search

**Goal**: Combine semantic search with keyword search for better results

**Priority**: MEDIUM

**Current Approach**:
- Pure semantic search (embeddings only)
- Can miss exact keyword matches

**Implementation**:
```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

# Keyword search
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 5

# Semantic search
faiss_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# Combine 50/50
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, faiss_retriever],
    weights=[0.5, 0.5]
)
```

**Benefits**:
- Finds exact matches (names, IDs, specific terms)
- Also finds semantically similar content
- Best of both worlds

**Dependencies**:
```
rank_bm25>=0.2.2
```

**Status**: [ ] Not Started

---

## Phase 9: Multiple Cartridges

**Goal**: Manage multiple memory cartridges with easy switching

**Priority**: LOW

**Features**:
- [ ] List all available cartridges
- [ ] Create new cartridge
- [ ] Switch active cartridge
- [ ] Delete cartridge
- [ ] Merge cartridges

**New MCP Tools**:
```python
@mcp.tool()
def list_cartridges() -> str:
    """List all available memory cartridges."""
    pass

@mcp.tool()
def switch_cartridge(name: str) -> str:
    """Switch to a different memory cartridge."""
    pass

@mcp.tool()
def create_cartridge(name: str, source_folder: str) -> str:
    """Create a new memory cartridge from a folder."""
    pass
```

**Status**: [ ] Not Started

---

## Phase 10: Web UI Dashboard

**Goal**: Visual interface for managing Engram

**Priority**: LOW

**Tech Stack Options**:
- **Streamlit** (fastest to build)
- **Gradio** (good for ML projects)
- **FastAPI + React** (most flexible)

**Features**:
- [ ] View all indexed files
- [ ] Search interface with results preview
- [ ] Indexing progress visualization
- [ ] Cartridge management
- [ ] File statistics and analytics

**Status**: [ ] Not Started

---

## Phase 11: Additional File Formats

**Goal**: Support more document types

**Priority**: LOW

| Format | Library | Notes |
|--------|---------|-------|
| .docx | `python-docx` | Word documents |
| .xlsx | `openpyxl` | Excel spreadsheets |
| .pptx | `python-pptx` | PowerPoint slides |
| .epub | `ebooklib` | E-books |
| .html | `beautifulsoup4` | Web pages |
| .csv | `pandas` | Data files |
| .json | built-in | Config/data files |

**Audio/Video** (requires transcription):
| Format | Library | Notes |
|--------|---------|-------|
| .mp3, .wav | `whisper` | OpenAI Whisper |
| .mp4, .mov | `whisper` + `ffmpeg` | Extract audio first |

**Status**: [ ] Not Started

---

## Phase 12: AI Enhancements

**Goal**: Add intelligent features on top of search

**Priority**: LOW

**Features**:

### 12a. Auto-Summarization
Generate summaries when indexing:
```python
# Store summary as metadata
doc.metadata["summary"] = generate_summary(doc.page_content)
```

### 12b. Topic Clustering
Automatically group related documents:
```python
from sklearn.cluster import KMeans

# Cluster embeddings
kmeans = KMeans(n_clusters=20)
clusters = kmeans.fit_predict(embeddings)
```

### 12c. Duplicate Detection
Find and flag duplicate content:
```python
# Compare embedding similarity
from sklearn.metrics.pairwise import cosine_similarity

# Flag duplicates above 0.95 similarity
```

### 12d. Smart Suggestions
"You might also want to see..." based on query.

**Status**: [ ] Not Started

---

## Quick Reference: Phase Priority

| Phase | Name | Priority | Effort | Impact |
|-------|------|----------|--------|--------|
| 5 | GPU Acceleration | HIGH | Low | High |
| 6 | Parallel File Loading | MEDIUM | Low | Medium |
| 7 | Smarter Chunking | MEDIUM | Medium | Medium |
| 8 | Hybrid Search | MEDIUM | Medium | High |
| 9 | Multiple Cartridges | LOW | Medium | Medium |
| 10 | Web UI Dashboard | LOW | High | Medium |
| 11 | Additional Formats | LOW | Medium | Low |
| 12 | AI Enhancements | LOW | High | High |

---

## Recommended Order

1. **Phase 5** - GPU Acceleration (quick win, huge impact)
2. **Phase 6** - Parallel Loading (complements Phase 5)
3. **Phase 8** - Hybrid Search (better search quality)
4. **Phase 7** - Smarter Chunking (better for code/docs)
5. **Phase 9+** - As needed

---

## Completed Phases

- [x] **Phase 1**: Basic ingestion + MCP server
- [x] **Phase 2**: OCR support (scanned PDFs, images)
- [x] **Phase 3**: Ghost file watcher
- [x] **Phase 4**: Incremental updates + crash recovery
- [x] **Phase 5**: GPU acceleration (MPS/CUDA auto-detection)

---

*Last Updated: February 2025*

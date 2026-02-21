#!/usr/bin/env python3
"""
Project Engram - The Server (server.py)

This script loads a Memory Cartridge (FAISS vector database) and exposes it
as an MCP (Model Context Protocol) server that AI agents can connect to.

Usage:
    python server.py <engram_folder>

Example:
    python server.py manual_engram
"""

import argparse
import os
import sys
from pathlib import Path


# ============================================================
# Helper: Print to stderr (keeps stdout clean for MCP protocol)
# ============================================================

def log(message: str):
    """Print status messages to stderr so they don't interfere with MCP."""
    print(message, file=sys.stderr)


# ============================================================
# STEP 1: Parse command-line arguments or environment variable
# ============================================================

parser = argparse.ArgumentParser(
    description="Start an MCP server to serve a Memory Cartridge"
)
parser.add_argument(
    "engram_folder",
    type=str,
    nargs="?",  # Make it optional
    default=None,
    help="Path to the Memory Cartridge folder (created by ingest.py)"
)
# Use parse_known_args to ignore extra arguments (e.g., from mcp run)
args, _ = parser.parse_known_args()

# Get engram path from environment variable (preferred for MCP) or CLI argument
# Environment variable takes precedence to support `mcp run` command
engram_folder = os.environ.get("ENGRAM_PATH") or args.engram_folder

if not engram_folder:
    log("Error: No Memory Cartridge specified.")
    log("   Usage: python server.py <engram_folder>")
    log("   Or set ENGRAM_PATH environment variable.")
    sys.exit(1)

# Validate the folder exists
engram_path = Path(engram_folder)
if not engram_path.exists():
    log(f"Error: Folder not found: {engram_path}")
    log("   Make sure you've run ingest.py first to create a Memory Cartridge.")
    sys.exit(1)

# Check that it contains a FAISS index
if not (engram_path / "index.faiss").exists():
    log(f"Error: No FAISS index found in {engram_path}")
    log("   This doesn't appear to be a valid Memory Cartridge.")
    sys.exit(1)

log(f"Project Engram - Memory Server")
log("=" * 50)
log(f"Loading Memory Cartridge: {engram_path.name}")

# ============================================================
# STEP 2: Load the embedding model (same as used in ingest.py)
# ============================================================

log("\nInitializing embedding model...")

from langchain_huggingface import HuggingFaceEmbeddings

# IMPORTANT: Must use the SAME model that was used to create the embeddings!
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

log("   Embedding model loaded")

# ============================================================
# STEP 3: Load the FAISS vector store
# ============================================================

log("\nLoading vector database...")

from langchain_community.vectorstores import FAISS

# Load the saved FAISS index
# allow_dangerous_deserialization is needed because FAISS uses pickle
vector_store = FAISS.load_local(
    str(engram_path),
    embeddings,
    allow_dangerous_deserialization=True  # Safe here - we created this file
)

log("   Vector database loaded")
log(f"   Memory cartridge '{engram_path.name}' is ready!")

# ============================================================
# STEP 4: Create the MCP Server
# ============================================================

log("\nStarting MCP Server...")

from mcp.server.fastmcp import FastMCP

# Create the MCP server instance
# The name appears in the AI's tool list
mcp = FastMCP(
    name=f"engram-{engram_path.stem}",
)


@mcp.tool()
def query_memory(query: str) -> str:
    """
    Search the Memory Cartridge for information relevant to your query.

    This tool searches through the indexed documents and returns the most
    relevant text chunks that match your question or topic.

    Args:
        query: Your question or search topic (e.g., "How do I reset the device?")

    Returns:
        The top 5 most relevant text chunks from the Memory Cartridge.
    """
    log(f"\nQuery received: '{query}'")

    # Search the vector store for similar chunks
    # k=5 means return the top 5 most relevant results
    results = vector_store.similarity_search(query, k=5)

    log(f"   Found {len(results)} relevant chunks")

    # Format the results nicely
    output_parts = []
    for i, doc in enumerate(results, 1):
        # Get the source info if available
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", None)

        # Build the result header
        if page is not None:
            header = f"[Result {i} - Page {page + 1}]"
        else:
            header = f"[Result {i}]"

        output_parts.append(f"{header}\n{doc.page_content}")

    # Join all results with separators
    return "\n\n---\n\n".join(output_parts)


# ============================================================
# STEP 5: Run the server
# ============================================================

log("=" * 50)
log("MCP Server is running!")
log(f"   Tool available: 'query_memory'")
log("\nTo connect this to Claude Desktop, add to your config:")
log(f"""
{{
  "mcpServers": {{
    "engram": {{
      "command": "python",
      "args": ["{Path(sys.argv[0]).absolute()}", "{engram_path.absolute()}"]
    }}
  }}
}}
""")
log("Waiting for connections... (Press Ctrl+C to stop)")
log("-" * 50)

# Start the MCP server using stdio transport
# This is how Claude Desktop and other MCP clients communicate with the server
mcp.run()

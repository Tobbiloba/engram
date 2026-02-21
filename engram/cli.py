#!/usr/bin/env python3
"""
Engram CLI - Local, persistent memory for AI development workflows.

Usage:
    engram init [folder]       Index a folder
    engram query "search"      Search your memory
    engram watch               Start background watcher
    engram status              Show index stats
    engram setup               Auto-configure MCP clients
"""

import click
import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Version
VERSION = "0.1.0"

# Default engram folder name
DEFAULT_ENGRAM = "engram_index"


def get_device():
    """Auto-detect best device for embeddings."""
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
    except ImportError:
        pass
    return "cpu"


def print_banner():
    """Print the Engram banner."""
    click.echo()
    click.secho("  ENGRAM", fg="cyan", bold=True)
    click.secho("  Local, persistent memory for AI", fg="white")
    click.echo()


def print_success(message):
    """Print success message."""
    click.secho(f"  ✓ {message}", fg="green")


def print_error(message):
    """Print error message."""
    click.secho(f"  ✗ {message}", fg="red")


def print_info(message):
    """Print info message."""
    click.secho(f"  → {message}", fg="blue")


def print_warning(message):
    """Print warning message."""
    click.secho(f"  ! {message}", fg="yellow")


@click.group(invoke_without_command=True)
@click.option("--version", "-v", is_flag=True, help="Show version")
@click.pass_context
def main(ctx, version):
    """Engram - Local, persistent memory for AI development workflows."""
    if version:
        click.echo(f"engram v{VERSION}")
        return

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.argument("folder", default=".", type=click.Path(exists=True))
@click.option("-o", "--output", default=None, help="Output engram name")
@click.option("--no-ocr", is_flag=True, help="Disable OCR")
def init(folder, output, no_ocr):
    """Index a folder into a memory cartridge."""
    print_banner()

    folder_path = Path(folder).resolve()
    output_name = output or f"{folder_path.name}_engram"

    print_info(f"Indexing: {folder_path}")
    print_info(f"Output: {output_name}/")
    print_info(f"Device: {get_device()}")
    click.echo()

    # Import here to avoid slow startup
    try:
        from engram.ingest import run_ingest
        run_ingest(str(folder_path), output_name, use_ocr=not no_ocr)
    except ImportError:
        # Fallback to running the script directly
        cmd = [sys.executable, "ingest.py", str(folder_path), "-o", output_name]
        if no_ocr:
            cmd.append("--no-ocr")

        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
        if result.returncode != 0:
            print_error("Indexing failed")
            sys.exit(1)

    print_success("Memory cartridge created!")
    click.echo()
    click.echo(f"  Next: Run 'engram setup' to configure MCP")


@main.command()
@click.argument("query_text")
@click.option("-n", "--num-results", default=5, help="Number of results")
@click.option("-e", "--engram", default=None, help="Engram folder to query")
def query(query_text, num_results, engram):
    """Search your memory cartridge."""
    # Find engram folder
    if engram:
        engram_path = Path(engram)
    else:
        # Look for *_engram folders in current directory
        engram_folders = list(Path(".").glob("*_engram"))
        if not engram_folders:
            print_error("No engram found. Run 'engram init' first.")
            sys.exit(1)
        engram_path = engram_folders[0]

    if not engram_path.exists():
        print_error(f"Engram not found: {engram_path}")
        sys.exit(1)

    print_info(f"Searching: {engram_path}")
    print_info(f"Query: {query_text}")
    click.echo()

    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS

        # Load embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": get_device()},
            encode_kwargs={"normalize_embeddings": True}
        )

        # Load vector store
        vector_store = FAISS.load_local(
            str(engram_path),
            embeddings,
            allow_dangerous_deserialization=True
        )

        # Search
        results = vector_store.similarity_search(query_text, k=num_results)

        click.echo(f"  Found {len(results)} results:")
        click.echo()

        for i, doc in enumerate(results, 1):
            source = doc.metadata.get("source_file", "Unknown")
            source_name = Path(source).name if source != "Unknown" else source

            click.secho(f"  [{i}] {source_name}", fg="cyan", bold=True)

            # Truncate content for display
            content = doc.page_content[:300].replace("\n", " ")
            if len(doc.page_content) > 300:
                content += "..."

            click.echo(f"      {content}")
            click.echo()

    except Exception as e:
        print_error(f"Search failed: {e}")
        sys.exit(1)


@main.command()
@click.argument("folder", default=".", type=click.Path(exists=True))
@click.option("-o", "--output", default="brain_engram", help="Output engram name")
def watch(folder, output):
    """Start background file watcher (Ghost)."""
    print_banner()

    folder_path = Path(folder).resolve()

    print_info(f"Watching: {folder_path}")
    print_info(f"Engram: {output}/")
    print_info(f"Device: {get_device()}")
    print_info("Press Ctrl+C to stop")
    click.echo()

    # Run ghost.py
    try:
        from engram.ghost import main as ghost_main
        ghost_main(folder_path, output)
    except ImportError:
        cmd = [sys.executable, "ghost.py", str(folder_path), "-o", output]
        subprocess.run(cmd, cwd=Path(__file__).parent.parent)


@main.command()
@click.option("-e", "--engram", default=None, help="Engram folder")
def status(engram):
    """Show index status and stats."""
    print_banner()

    # Find engram folders
    if engram:
        engram_paths = [Path(engram)]
    else:
        engram_paths = list(Path(".").glob("*_engram"))

    if not engram_paths:
        print_warning("No engram folders found in current directory")
        click.echo()
        click.echo("  Run 'engram init <folder>' to create one")
        return

    for engram_path in engram_paths:
        if not engram_path.exists():
            continue

        click.secho(f"  {engram_path.name}/", fg="cyan", bold=True)

        # Check for index files
        index_file = engram_path / "index.faiss"
        pkl_file = engram_path / "index.pkl"
        registry_file = engram_path / "registry.json"

        if index_file.exists():
            size_mb = index_file.stat().st_size / (1024 * 1024)
            print_success(f"Index: {size_mb:.1f} MB")
        else:
            print_warning("No index found")

        if registry_file.exists():
            try:
                registry = json.loads(registry_file.read_text())
                print_success(f"Files tracked: {len(registry)}")
            except:
                pass

        # Show last modified
        if index_file.exists():
            mtime = datetime.fromtimestamp(index_file.stat().st_mtime)
            print_info(f"Last updated: {mtime.strftime('%Y-%m-%d %H:%M')}")

        click.echo()


@main.command()
def setup():
    """Auto-configure MCP for Claude Desktop and Cursor."""
    print_banner()

    print_info("Detecting MCP clients...")
    click.echo()

    configured = False

    # Find engram folder to configure
    engram_paths = list(Path(".").glob("*_engram"))
    if not engram_paths:
        print_warning("No engram found. Run 'engram init' first.")
        print_info("Will configure with placeholder path")
        engram_path = Path("./your_engram").resolve()
    else:
        engram_path = engram_paths[0].resolve()

    # Get server.py path
    server_path = Path(__file__).parent.parent / "server.py"
    if not server_path.exists():
        server_path = Path.cwd() / "server.py"

    # Get Python path
    python_path = Path(sys.executable)

    # Claude Desktop config
    claude_config_paths = [
        Path.home() / "Library/Application Support/Claude/claude_desktop_config.json",  # macOS
        Path.home() / "AppData/Roaming/Claude/claude_desktop_config.json",  # Windows
        Path.home() / ".config/claude/claude_desktop_config.json",  # Linux
    ]

    for config_path in claude_config_paths:
        if config_path.parent.exists():
            click.secho("  Claude Desktop", fg="cyan", bold=True)

            # Load existing config or create new
            if config_path.exists():
                config = json.loads(config_path.read_text())
            else:
                config = {}

            if "mcpServers" not in config:
                config["mcpServers"] = {}

            # Add engram config
            config["mcpServers"]["engram"] = {
                "command": str(python_path),
                "args": [str(server_path), str(engram_path)]
            }

            # Write config
            config_path.write_text(json.dumps(config, indent=2))

            print_success(f"Configured: {config_path}")
            print_info(f"Server: {server_path}")
            print_info(f"Engram: {engram_path}")
            configured = True
            click.echo()
            break

    # Cursor config
    cursor_config_paths = [
        Path.home() / ".cursor/mcp.json",
        Path.home() / "Library/Application Support/Cursor/mcp.json",  # macOS
        Path.home() / "AppData/Roaming/Cursor/mcp.json",  # Windows
    ]

    for config_path in cursor_config_paths:
        if config_path.parent.exists():
            click.secho("  Cursor", fg="cyan", bold=True)

            # Load existing config or create new
            if config_path.exists():
                try:
                    config = json.loads(config_path.read_text())
                except:
                    config = {}
            else:
                config = {}

            if "mcpServers" not in config:
                config["mcpServers"] = {}

            # Add engram config
            config["mcpServers"]["engram"] = {
                "command": str(python_path),
                "args": [str(server_path), str(engram_path)]
            }

            # Write config
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(json.dumps(config, indent=2))

            print_success(f"Configured: {config_path}")
            print_info(f"Server: {server_path}")
            print_info(f"Engram: {engram_path}")
            configured = True
            click.echo()
            break

    if configured:
        print_success("MCP configured!")
        click.echo()
        click.echo("  Restart Claude Desktop or Cursor to load the changes.")
        click.echo("  Then ask: 'What do you know about my codebase?'")
    else:
        print_warning("No MCP clients found")
        click.echo()
        click.echo("  Manual setup required. Add to your MCP config:")
        click.echo()
        click.echo(f'  "engram": {{')
        click.echo(f'    "command": "{python_path}",')
        click.echo(f'    "args": ["{server_path}", "{engram_path}"]')
        click.echo(f'  }}')


if __name__ == "__main__":
    main()

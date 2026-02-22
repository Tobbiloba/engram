#!/usr/bin/env python3
"""
Engram CLI - Local, persistent memory for AI development workflows.

Usage:
    engram init [folder]       Index a folder
    engram query "search"      Search your memory
    engram watch               Start background watcher
    engram daemon              Run watcher as background service
    engram status              Show index stats
    engram setup               Auto-configure MCP clients
"""

import click
import sys
import os
import json
import subprocess
import signal
from pathlib import Path
from datetime import datetime

VERSION = "0.1.1"
DEFAULT_ENGRAM_DIR = Path.home() / ".engram"


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
    click.echo()
    click.secho("  ENGRAM", fg="cyan", bold=True)
    click.secho("  Local, persistent memory for AI", fg="white")
    click.echo()


def print_success(message):
    click.secho(f"  ✓ {message}", fg="green")


def print_error(message):
    click.secho(f"  ✗ {message}", fg="red")


def print_info(message):
    click.secho(f"  → {message}", fg="blue")


def print_warning(message):
    click.secho(f"  ! {message}", fg="yellow")


def get_engram_storage_dir():
    """Get the global engram storage directory."""
    storage = DEFAULT_ENGRAM_DIR
    storage.mkdir(parents=True, exist_ok=True)
    return storage


def get_pid_file():
    """Get path to daemon PID file."""
    return get_engram_storage_dir() / "daemon.pid"


@click.group(invoke_without_command=True)
@click.option("--version", "-v", is_flag=True, help="Show version")
@click.pass_context
def main(ctx, version):
    """Engram - Local, persistent memory for AI development workflows.

    \b
    Quick Start:
        engram init ~/my-project    Index your project
        engram setup                Configure Claude/Cursor
        engram status               Check what's indexed

    \b
    After setup, ask your AI:
        "What do you know about my codebase?"
        "What changed in auth this week?"
        "Explain the login flow"

    \b
    Storage: ~/.engram/
    """
    if version:
        click.echo(f"engram v{VERSION}")
        return

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.argument("folder", default=".", type=click.Path(exists=True))
@click.option("-o", "--output", default=None, help="Output engram name")
@click.option("--no-ocr", is_flag=True, help="Disable OCR")
@click.option("--god-mode", is_flag=True, help="Index entire home directory (slow!)")
def init(folder, output, no_ocr, god_mode):
    """Index a folder into a memory cartridge.

    \b
    Examples:
        engram init                    Index current folder
        engram init ~/projects/myapp   Index specific folder
        engram init ~/projects -o work Index with custom name
        engram init --god-mode         Index entire home (WARNING: slow!)

    \b
    Indexed data is stored in: ~/.engram/<name>/
    """
    print_banner()

    if god_mode:
        folder = str(Path.home())
        output = output or "everything"
        print_warning("GOD MODE: Indexing entire home directory")
        print_warning("This will take a LONG time. Press Ctrl+C to cancel.")
        click.echo()

    folder_path = Path(folder).resolve()
    output_name = output or f"{folder_path.name}_engram"

    # Store in ~/.engram/
    storage_dir = get_engram_storage_dir()
    output_path = storage_dir / output_name

    print_info(f"Indexing: {folder_path}")
    print_info(f"Output: {output_path}")
    print_info(f"Device: {get_device()}")
    click.echo()

    try:
        from engram.ingest import run_ingest
        success = run_ingest(
            str(folder_path),
            str(output_path),
            use_ocr=not no_ocr
        )

        if success:
            print_success("Memory cartridge created!")
            click.echo()
            click.echo("  Next steps:")
            click.echo("    1. Run 'engram setup' to configure MCP")
            click.echo("    2. Restart Claude Desktop or Cursor")
            click.echo("    3. Ask: 'What do you know about my codebase?'")
        else:
            print_error("Indexing failed")
            sys.exit(1)

    except Exception as e:
        print_error(f"Indexing failed: {e}")
        sys.exit(1)


@main.command()
@click.argument("query_text")
@click.option("-n", "--num-results", default=5, help="Number of results")
@click.option("-e", "--engram", default=None, help="Engram name to query")
def query(query_text, num_results, engram):
    """Search your memory cartridge.

    \b
    Examples:
        engram query "how does authentication work"
        engram query "database connection" -n 10
        engram query "login" -e myproject_engram
    """
    storage_dir = get_engram_storage_dir()

    if engram:
        engram_path = storage_dir / engram
    else:
        # Find engram folders
        engram_folders = [d for d in storage_dir.iterdir() if d.is_dir()]
        if not engram_folders:
            # Also check current directory
            engram_folders = list(Path(".").glob("*_engram"))

        if not engram_folders:
            print_error("No engram found. Run 'engram init' first.")
            sys.exit(1)

        engram_path = engram_folders[0]

    if not engram_path.exists():
        print_error(f"Engram not found: {engram_path}")
        sys.exit(1)

    print_info(f"Searching: {engram_path.name}")
    print_info(f"Query: {query_text}")
    click.echo()

    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": get_device()},
            encode_kwargs={"normalize_embeddings": True}
        )

        vector_store = FAISS.load_local(
            str(engram_path),
            embeddings,
            allow_dangerous_deserialization=True
        )

        results = vector_store.similarity_search(query_text, k=num_results)

        click.echo(f"  Found {len(results)} results:")
        click.echo()

        for i, doc in enumerate(results, 1):
            source = doc.metadata.get("source_file", "Unknown")
            source_name = Path(source).name if source != "Unknown" else source

            click.secho(f"  [{i}] {source_name}", fg="cyan", bold=True)

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
    """Start file watcher (runs in foreground).

    Press Ctrl+C to stop. For background daemon, use 'engram daemon'.
    """
    print_banner()

    folder_path = Path(folder).resolve()
    storage_dir = get_engram_storage_dir()
    output_path = storage_dir / output

    print_info(f"Watching: {folder_path}")
    print_info(f"Engram: {output_path}")
    print_info(f"Device: {get_device()}")
    print_info("Press Ctrl+C to stop")
    click.echo()

    try:
        from engram.ghost import GhostWatcher
        watcher = GhostWatcher(str(folder_path), str(output_path))
        watcher.run()
    except ImportError:
        print_error("Ghost module not found")
        sys.exit(1)
    except KeyboardInterrupt:
        print_info("Stopped watching")


@main.command()
@click.argument("folder", default=".", type=click.Path(exists=True))
@click.option("-o", "--output", default="brain_engram", help="Output engram name")
def daemon(folder, output):
    """Start file watcher as background daemon.

    \b
    Keeps running after you close the terminal.

    \b
    Examples:
        engram daemon ~/projects      Start watching
        engram daemon-stop            Stop the daemon
    """
    print_banner()

    pid_file = get_pid_file()

    # Check if already running
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, 0)  # Check if process exists
            print_warning(f"Daemon already running (PID {pid})")
            print_info("Run 'engram daemon-stop' to stop it")
            return
        except (ProcessLookupError, ValueError):
            pid_file.unlink()  # Stale PID file

    folder_path = Path(folder).resolve()
    storage_dir = get_engram_storage_dir()
    output_path = storage_dir / output

    print_info(f"Starting daemon...")
    print_info(f"Watching: {folder_path}")
    print_info(f"Engram: {output_path}")

    # Fork to background
    pid = os.fork()

    if pid > 0:
        # Parent process
        pid_file.write_text(str(pid))
        print_success(f"Daemon started (PID {pid})")
        print_info("Run 'engram daemon-stop' to stop")
        return

    # Child process - become daemon
    os.setsid()
    os.chdir("/")

    # Redirect stdout/stderr to log file
    log_file = storage_dir / "daemon.log"
    sys.stdout = open(log_file, "a")
    sys.stderr = sys.stdout

    try:
        from engram.ghost import GhostWatcher
        watcher = GhostWatcher(str(folder_path), str(output_path))
        watcher.run()
    except Exception as e:
        print(f"Daemon error: {e}")


@main.command("daemon-stop")
def daemon_stop():
    """Stop the background daemon."""
    print_banner()

    pid_file = get_pid_file()

    if not pid_file.exists():
        print_warning("No daemon running")
        return

    try:
        pid = int(pid_file.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        pid_file.unlink()
        print_success(f"Daemon stopped (PID {pid})")
    except ProcessLookupError:
        pid_file.unlink()
        print_warning("Daemon was not running (cleaned up stale PID)")
    except Exception as e:
        print_error(f"Failed to stop daemon: {e}")


@main.command()
@click.option("-e", "--engram", default=None, help="Engram folder")
def status(engram):
    """Show index status and stats.

    \b
    Shows:
        - All indexed projects
        - Storage location
        - Index size
        - Last update time
        - Daemon status
    """
    print_banner()

    storage_dir = get_engram_storage_dir()

    click.secho(f"  Storage: {storage_dir}", fg="white")
    click.echo()

    # Check daemon status
    pid_file = get_pid_file()
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, 0)
            click.secho(f"  Daemon: Running (PID {pid})", fg="green")
        except:
            click.secho("  Daemon: Not running", fg="yellow")
    else:
        click.secho("  Daemon: Not running", fg="yellow")

    click.echo()

    # Find engram folders
    if engram:
        engram_paths = [storage_dir / engram]
    else:
        engram_paths = [d for d in storage_dir.iterdir() if d.is_dir()]
        # Also check current directory
        engram_paths.extend(Path(".").glob("*_engram"))

    if not engram_paths:
        print_warning("No engram folders found")
        click.echo()
        click.echo("  Run 'engram init <folder>' to create one")
        return

    click.secho("  Indexed Projects:", fg="cyan", bold=True)
    click.echo()

    for engram_path in engram_paths:
        if not engram_path.exists():
            continue

        click.secho(f"    {engram_path.name}", fg="cyan", bold=True)

        index_file = engram_path / "index.faiss"
        if index_file.exists():
            size_mb = index_file.stat().st_size / (1024 * 1024)
            mtime = datetime.fromtimestamp(index_file.stat().st_mtime)
            click.echo(f"      Size: {size_mb:.1f} MB")
            click.echo(f"      Updated: {mtime.strftime('%Y-%m-%d %H:%M')}")
        else:
            click.echo("      Status: No index found")

        click.echo()


@main.command()
def setup():
    """Auto-configure MCP for Claude Desktop and Cursor.

    \b
    This configures your AI tools to use Engram's memory.

    After running this:
        1. Restart Claude Desktop or Cursor
        2. Ask: "What do you know about my codebase?"

    \b
    MCP Tools available to your AI:
        - query_memory: Search your indexed code
        - query_recent: Find recently changed files
        - whats_changed: See what changed this week
        - explain_file: Get file history
    """
    print_banner()

    print_info("Detecting MCP clients...")
    click.echo()

    configured = False
    storage_dir = get_engram_storage_dir()

    # Find engram folder
    engram_folders = [d for d in storage_dir.iterdir() if d.is_dir()]
    if not engram_folders:
        engram_folders = list(Path(".").glob("*_engram"))

    if not engram_folders:
        print_warning("No engram found. Run 'engram init' first.")
        return

    engram_path = engram_folders[0].resolve()

    # Find server.py - check package location first
    import engram
    package_dir = Path(engram.__file__).parent
    server_path = package_dir / "server.py"

    if not server_path.exists():
        # Fall back to current directory
        server_path = Path.cwd() / "server.py"

    if not server_path.exists():
        print_error("server.py not found!")
        print_info("Make sure you installed engram correctly")
        return

    python_path = Path(sys.executable)

    # Claude Desktop config
    claude_config_paths = [
        Path.home() / "Library/Application Support/Claude/claude_desktop_config.json",
        Path.home() / "AppData/Roaming/Claude/claude_desktop_config.json",
        Path.home() / ".config/claude/claude_desktop_config.json",
    ]

    for config_path in claude_config_paths:
        if config_path.parent.exists():
            click.secho("  Claude Desktop", fg="cyan", bold=True)

            if config_path.exists():
                config = json.loads(config_path.read_text())
            else:
                config = {}

            if "mcpServers" not in config:
                config["mcpServers"] = {}

            config["mcpServers"]["engram"] = {
                "command": str(python_path),
                "args": [str(server_path), str(engram_path)]
            }

            config_path.write_text(json.dumps(config, indent=2))

            print_success("Configured!")
            print_info(f"Engram: {engram_path.name}")
            configured = True
            click.echo()
            break

    # Cursor config
    cursor_config_paths = [
        Path.home() / ".cursor/mcp.json",
        Path.home() / "Library/Application Support/Cursor/mcp.json",
        Path.home() / "AppData/Roaming/Cursor/mcp.json",
    ]

    for config_path in cursor_config_paths:
        if config_path.parent.exists():
            click.secho("  Cursor", fg="cyan", bold=True)

            if config_path.exists():
                try:
                    config = json.loads(config_path.read_text())
                except:
                    config = {}
            else:
                config = {}

            if "mcpServers" not in config:
                config["mcpServers"] = {}

            config["mcpServers"]["engram"] = {
                "command": str(python_path),
                "args": [str(server_path), str(engram_path)]
            }

            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(json.dumps(config, indent=2))

            print_success("Configured!")
            print_info(f"Engram: {engram_path.name}")
            configured = True
            click.echo()
            break

    if configured:
        print_success("MCP configured!")
        click.echo()
        click.echo("  Next steps:")
        click.echo("    1. Restart Claude Desktop or Cursor")
        click.echo("    2. Ask: 'What do you know about my codebase?'")
        click.echo()
        click.echo("  Available AI commands:")
        click.secho("    • 'Search for [topic]'", fg="cyan")
        click.secho("    • 'What changed this week?'", fg="cyan")
        click.secho("    • 'Explain [filename]'", fg="cyan")
    else:
        print_warning("No MCP clients found")
        click.echo()
        click.echo("  Manual setup required. See docs.")


@main.command()
def tools():
    """Show available MCP tools your AI can use."""
    print_banner()

    click.secho("  MCP Tools:", fg="cyan", bold=True)
    click.echo()

    tools_info = [
        ("query_memory", "Search your indexed codebase", "Find code related to authentication"),
        ("query_recent", "Find recently changed files", "What changed in auth this week?"),
        ("whats_changed", "Summary of recent changes", "Give me a changelog"),
        ("explain_file", "Get file history and context", "Explain the login.py file"),
    ]

    for name, desc, example in tools_info:
        click.secho(f"    {name}", fg="green", bold=True)
        click.echo(f"      {desc}")
        click.echo(f"      Example: \"{example}\"")
        click.echo()


if __name__ == "__main__":
    main()

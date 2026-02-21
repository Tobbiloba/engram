#!/bin/bash
#
# Engram Installer
# Local, persistent memory for AI development workflows
#
# Usage:
#   curl -sSL https://engram.dev/install | bash
#
# Or:
#   bash install.sh
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Print functions
print_banner() {
    echo ""
    echo -e "${CYAN}${BOLD}  ENGRAM${NC}"
    echo -e "  Local, persistent memory for AI"
    echo ""
}

print_success() {
    echo -e "${GREEN}  ✓ $1${NC}"
}

print_error() {
    echo -e "${RED}  ✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}  → $1${NC}"
}

# Check Python version
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python not found. Please install Python 3.9+"
        exit 1
    fi

    # Check version
    PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 9 ]); then
        print_error "Python 3.9+ required. Found: $PYTHON_VERSION"
        exit 1
    fi

    print_success "Python $PYTHON_VERSION found"
}

# Main installation
main() {
    print_banner

    print_info "Checking requirements..."
    echo ""

    # Check Python
    check_python

    # Determine install directory
    INSTALL_DIR="${ENGRAM_INSTALL_DIR:-$HOME/.engram}"

    print_info "Installing to: $INSTALL_DIR"

    # Create directory
    mkdir -p "$INSTALL_DIR"

    # Clone or download
    if command -v git &> /dev/null; then
        print_info "Cloning repository..."
        if [ -d "$INSTALL_DIR/.git" ]; then
            cd "$INSTALL_DIR" && git pull --quiet
        else
            git clone --quiet https://github.com/Tobbiloba/engram.git "$INSTALL_DIR" 2>/dev/null || {
                # If repo doesn't exist yet, create basic structure
                print_info "Creating local installation..."
            }
        fi
        print_success "Repository ready"
    else
        print_info "Git not found, using pip install..."
    fi

    # Create virtual environment
    print_info "Creating virtual environment..."
    cd "$INSTALL_DIR"
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"

    # Activate and install
    print_info "Installing dependencies..."
    source venv/bin/activate

    # Upgrade pip
    pip install --quiet --upgrade pip

    # Install engram
    if [ -f "setup.py" ]; then
        pip install --quiet -e .
    else
        pip install --quiet engram 2>/dev/null || {
            # Install dependencies manually if package not on PyPI
            pip install --quiet \
                langchain langchain-community langchain-huggingface \
                langchain-text-splitters langchain-core \
                sentence-transformers faiss-cpu pypdf mcp watchdog click torch
        }
    fi

    print_success "Dependencies installed"

    # Create shell wrapper
    print_info "Setting up command..."

    WRAPPER_SCRIPT="$HOME/.local/bin/engram"
    mkdir -p "$(dirname "$WRAPPER_SCRIPT")"

    cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
source "$INSTALL_DIR/venv/bin/activate"
python -m engram.cli "\$@"
EOF

    chmod +x "$WRAPPER_SCRIPT"

    # Add to PATH if needed
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        print_info "Adding ~/.local/bin to PATH..."

        # Detect shell
        if [ -n "$ZSH_VERSION" ]; then
            SHELL_RC="$HOME/.zshrc"
        elif [ -n "$BASH_VERSION" ]; then
            SHELL_RC="$HOME/.bashrc"
        else
            SHELL_RC="$HOME/.profile"
        fi

        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
        print_info "Added to $SHELL_RC"
    fi

    print_success "Command 'engram' installed"

    # Done
    echo ""
    echo -e "${GREEN}${BOLD}  Installation complete!${NC}"
    echo ""
    echo "  Quick start:"
    echo ""
    echo "    1. Restart your terminal (or run: source ~/.zshrc)"
    echo ""
    echo "    2. Index your project:"
    echo "       engram init ~/your/project"
    echo ""
    echo "    3. Configure MCP:"
    echo "       engram setup"
    echo ""
    echo "    4. Start asking Claude/Cursor about your code!"
    echo ""
    echo -e "  ${CYAN}Docs: https://github.com/Tobbiloba/engram${NC}"
    echo ""
}

# Run
main

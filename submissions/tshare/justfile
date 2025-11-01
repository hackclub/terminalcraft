# TShare Development Commands

default:
    @just --list

# Run tunnel server only
tunnel *args:
    cargo run --bin tunnel-server -- {{args}}

# Run web server only  
web *args:
    cargo run --bin web-server -- {{args}}

# Run client only
client *args:
    cargo run --bin tshare -- {{args}}

# Run tunnel server and web server simultaneously (logs go to ~/.tshare/)
run:
    #!/usr/bin/env bash
    set -e
    
    echo "Starting TShare servers..."
    echo "Tunnel server will be available on port 8385 (API and WebSocket)"
    echo "Web server will be available on port 8386"
    echo "Logs are written to ~/.tshare/tunnel-server.log and ~/.tshare/web-server.log"
    echo "Press Ctrl+C to stop all servers"
    echo ""
    
    # Start tunnel server and web server in parallel with log prefixes
    (cargo run --bin tunnel-server 2>&1 | sed 's/^/[tunnel-server]: /') &
    TUNNEL_PID=$!
    
    # Give tunnel server time to start
    sleep 2
    
    (cargo run --bin web-server 2>&1 | sed 's/^/[web-server]: /') &
    WEB_PID=$!
    
    # Function to cleanup processes on exit
    cleanup() {
        echo ""
        echo "Shutting down servers..."
        kill $TUNNEL_PID $WEB_PID 2>/dev/null || true
        wait $TUNNEL_PID $WEB_PID 2>/dev/null || true
        echo "All servers stopped."
    }
    
    # Set up signal handlers
    trap cleanup EXIT INT TERM
    
    # Wait for processes
    wait $TUNNEL_PID $WEB_PID

format:
    cargo fmt --all
    taplo fmt
    @echo "Formatting HTML files..."
    @if command -v djlint >/dev/null 2>&1; then \
        find . -name "*.html" -not -path "./target/*" -exec djlint --reformat {} \; ; \
    else \
        echo "No HTML formatter found. Install djlint (pip install djlint) for HTML formatting"; \
    fi

format-check:
    cargo fmt --all -- --check
    taplo fmt --check
    @echo "Checking HTML formatting..."
    @if command -v djlint >/dev/null 2>&1; then \
        find . -name "*.html" -not -path "./target/*" -exec djlint --check {} \; ; \
    else \
        echo "No HTML formatter found. Install djlint (pip install djlint) for HTML formatting"; \
    fi

lint:
    cargo clippy --workspace --release --lib --bins --tests --examples --all-targets --all-features -- -D warnings

fix:
    cargo clippy --fix --allow-dirty --allow-staged --workspace --all-targets --all-features --release

build:
    cargo build --release --workspace --all-targets

finalize:
    just format
    just lint
    just build

# Build all binaries in debug mode
build-debug:
    cargo build --workspace

# Check all code compiles
check:
    cargo check --workspace

# Run tests
test:
    cargo test --workspace

# Install all binaries
install:
    cargo install --path . --bin tunnel-server
    cargo install --path . --bin web-server  
    cargo install --path . --bin tshare

# Clean build artifacts
clean:
    cargo clean

# View logs
logs:
    #!/usr/bin/env bash
    echo "=== TShare Logs ==="
    echo "Logs are located in ~/.tshare/"
    echo ""
    if [ -f ~/.tshare/tunnel-server.log ]; then
        echo "=== Tunnel Server Log ==="
        tail -20 ~/.tshare/tunnel-server.log
        echo ""
    fi
    if [ -f ~/.tshare/web-server.log ]; then
        echo "=== Web Server Log ==="
        tail -20 ~/.tshare/web-server.log
        echo ""
    fi
    if [ -f ~/.tshare/tshare.log ]; then
        echo "=== Client Log ==="
        tail -20 ~/.tshare/tshare.log
        echo ""
    fi

# Follow logs in real-time
logs-follow:
    #!/usr/bin/env bash
    echo "Following all TShare logs (Ctrl+C to stop)..."
    echo "Logs are located in ~/.tshare/"
    echo ""
    if command -v multitail >/dev/null 2>&1; then
        multitail -f ~/.tshare/tunnel-server.log -f ~/.tshare/web-server.log -f ~/.tshare/tshare.log
    else
        echo "Install multitail for better log following, falling back to tail..."
        tail -f ~/.tshare/*.log 2>/dev/null || echo "No log files found"
    fi

# Clear all logs
logs-clear:
    #!/usr/bin/env bash
    echo "Clearing all TShare logs..."
    rm -f ~/.tshare/*.log
    echo "Logs cleared."

# Build Debian package
build-deb:
    #!/usr/bin/env bash
    set -e
    
    echo "Building Debian package for TShare..."
    
    # Build release binaries
    cargo build --release
    
    # Create package directory structure
    PKG_NAME="tshare"
    PKG_VERSION=$(grep '^version' Cargo.toml | head -1 | cut -d'"' -f2)
    PKG_DIR="releases/${PKG_NAME}_${PKG_VERSION}_amd64"
    
    mkdir -p releases
    rm -rf "$PKG_DIR"
    mkdir -p "$PKG_DIR/DEBIAN"
    mkdir -p "$PKG_DIR/usr/bin"
    mkdir -p "$PKG_DIR/usr/share/doc/$PKG_NAME"
    mkdir -p "$PKG_DIR/usr/share/man/man1"
    
    # Copy binaries
    cp target/release/tshare "$PKG_DIR/usr/bin/"
    cp target/release/tunnel-server "$PKG_DIR/usr/bin/"
    cp target/release/web-server "$PKG_DIR/usr/bin/"
    
    # Make binaries executable
    chmod +x "$PKG_DIR/usr/bin/"*
    
    # Copy documentation
    cp README.md "$PKG_DIR/usr/share/doc/$PKG_NAME/"
    cp LICENSE "$PKG_DIR/usr/share/doc/$PKG_NAME/"
    
    # Create control file
    cat > "$PKG_DIR/DEBIAN/control" << EOF
    Package: $PKG_NAME
    Version: $PKG_VERSION
    Section: utils
    Priority: optional
    Architecture: amd64
    Maintainer: RobbyV2 <robby@robby.blue>
    Description: Terminal sharing made simple
     TShare lets you share your terminal session with anyone through a simple web link.
     Perfect for pair programming, debugging, teaching, or getting help.
     .
     This package includes:
     - tshare: CLI client for sharing terminal sessions
     - tunnel-server: WebSocket relay server for terminal data
     - web-server: Web interface for viewing shared terminals
    Homepage: https://github.com/RobbyV2/tshare
    EOF
    
    # Create postinst script for systemd service (optional)
    cat > "$PKG_DIR/DEBIAN/postinst" << 'EOF'
    #!/bin/bash
    set -e
    
    echo "TShare installed successfully!"
    echo ""
    echo "Quick start:"
    echo "1. Start servers: tunnel-server & web-server &"
    echo "2. Share terminal: tshare share"
    echo ""
    echo "For more information, see: https://github.com/RobbyV2/tshare"
    
    exit 0
    EOF
    
    chmod +x "$PKG_DIR/DEBIAN/postinst"
    
    # Build the .deb package
    dpkg-deb --build "$PKG_DIR"
    
    echo "Debian package created: releases/${PKG_NAME}_${PKG_VERSION}_amd64.deb"
    
    # Verify the package
    echo "Package info:"
    dpkg --info "releases/${PKG_NAME}_${PKG_VERSION}_amd64.deb"
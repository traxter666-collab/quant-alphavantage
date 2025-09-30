#!/bin/bash
# UNIFIED TRADING SYSTEM - LINUX/MAC LAUNCHER
# No .py scripts needed - just run commands

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -eq 0 ]; then
    # Default: Auto-analysis based on market time
    python "$SCRIPT_DIR/seamless_market_system.py"
elif [ "$1" = "now" ]; then
    python "$SCRIPT_DIR/seamless_market_system.py"
elif [ "$1" = "monitor" ]; then
    # Continuous monitoring 30s
    python "$SCRIPT_DIR/seamless_market_system.py" monitor 30
elif [ "$1" = "fast" ]; then
    # Fast monitoring 10s
    python "$SCRIPT_DIR/seamless_market_system.py" monitor 10
elif [ "$1" = "stream" ]; then
    # Alias for monitor
    python "$SCRIPT_DIR/seamless_market_system.py" monitor 30
elif [ "$1" = "auto" ]; then
    # Auto-launcher - waits for market open
    python "$SCRIPT_DIR/market_open_auto_launcher.py"
elif [ "$1" = "health" ]; then
    # System health check
    python "$SCRIPT_DIR/system_validation.py"
elif [ "$1" = "quick" ]; then
    # Quick snapshot
    python "$SCRIPT_DIR/seamless_market_system.py" quick
else
    echo "UNIFIED TRADING SYSTEM"
    echo "====================="
    echo ""
    echo "USAGE:"
    echo "  ./trade              Auto-analysis (adapts to market time)"
    echo "  ./trade now          Current market analysis"
    echo "  ./trade monitor      Continuous updates (30s)"
    echo "  ./trade fast         Fast updates (10s)"
    echo "  ./trade stream       Streaming mode (30s)"
    echo "  ./trade auto         Auto-start at market open"
    echo "  ./trade health       System health check"
    echo "  ./trade quick        Quick snapshot"
    echo ""
fi
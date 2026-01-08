#!/bin/bash
# Shell script to run the Log & PCAP Analyzer (Linux/Mac)

echo "========================================"
echo "  Unified Log & PCAP Analyzer v2.0"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "[OK] Activating virtual environment..."
    source .venv/bin/activate
else
    echo "[WARNING] Virtual environment not found"
    echo "Using system Python..."
fi

echo ""
echo "Starting application..."
echo ""

# Run the main application
python3 main.py

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Application exited with errors"
    read -p "Press Enter to continue..."
fi

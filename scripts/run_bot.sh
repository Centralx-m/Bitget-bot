#!/bin/bash
# scripts/run_bot.sh - Run the bot

echo "🚀 Starting XTAAGC Bot..."

# Activate virtual environment
source venv/bin/activate

# Set Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}"

# Run bot
python src/main.py
#!/usr/bin/env bash
# Simple run script for Termux / Linux
source venv/bin/activate 2>/dev/null || true
if [ -z "$BOT_TOKEN" ]; then
  echo "Please set BOT_TOKEN environment variable, e.g.:"
  echo "export BOT_TOKEN="your_bot_token_here""
  exit 1
fi
python bot_silverinsta.py

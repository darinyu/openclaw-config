#!/bin/bash
# Usage: add_word.sh <word> <meaning> [source]
# Add a new vocabulary word for Darin
python3 /data/.openclaw/workspace/vocabulary/quiz.py add "$1" "$2" "$3"

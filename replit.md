# GrammarZen - Grammar Checking Application

## Overview
A web-based grammar checking tool built with FastAPI (Python backend) and vanilla JavaScript frontend. Uses LanguageTool for primary grammar checking, supplemented by custom rules for improved accuracy.

## Architecture
- **Backend**: FastAPI server (`src/main.py`) running on port 5000
- **Grammar Engine**: `src/grammar_engine.py` - Singleton wrapper around LanguageTool with custom rule integration
- **Custom Rules**: `src/custom_rules.py` - Supplementary regex-based grammar rules for confused words, subject-verb agreement, and common misspellings that LanguageTool misses
- **Text Analyzer**: `src/text_analyzer.py` - Readability, sentiment, and writing suggestions
- **Frontend**: Static files in `src/static/` (app.js, style.css, index.html served via Jinja2 templates)

## Scoring System
- Severity-weighted penalties: errors=15pts, warnings=8pts, style=3pts
- Error density multiplier: more errors per word increases penalty
- Grade thresholds: Excellent (95+), Very Good (85+), Good (70+), Fair (50+), Poor (30+), Needs Work (<30)

## Key Dependencies
- `language_tool_python` - LanguageTool wrapper for grammar checking
- `fastapi` + `uvicorn` - Web server
- `textblob` - Sentiment analysis
- `pydantic` - Request validation
- `jinja2` - HTML templating

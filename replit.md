# GrammarZen

A free, open-source grammar checker and text analysis tool built with FastAPI and vanilla JavaScript.

## Architecture

- **Backend**: Python 3.11 + FastAPI + Uvicorn (port 5000)
- **Frontend**: HTML/CSS/JS in `src/static/`
- **Grammar Engine**: `language-tool-python` (Java-based LanguageTool wrapper)
- **NLP**: `nltk`, `textblob` for sentiment/readability analysis

## Project Structure

```
src/
  main.py              # FastAPI app, API routes, rate limiter
  grammar_engine.py    # LanguageTool integration (singleton)
  text_analyzer.py     # Sentiment, readability, suggestions
  custom_rules.py      # Regex-based grammar rules
  static/
    index.html         # Main grammar checker UI
    style.css          # Rajdhani font, light theme
    app.js             # Frontend logic
    api-docs.html      # API documentation page (Whois Mono font, dark theme)
    logo.png           # Branding
```

## API

- `GET /` — Main app UI
- `GET /api?req={text}` — Public grammar API (rate limited: 3 req / 25 min per IP)
- `GET /api/docs` — API documentation page
- `POST /api/correct` — Internal API used by frontend (no rate limit)
- `GET /health` — Health check

## Key Dependencies

- fastapi, uvicorn, pydantic
- language-tool-python (requires Java/OpenJDK 17)
- nltk, textblob, spacy
- aiofiles, httpx, python-multipart

## Notes

- LanguageTool downloads on first startup (~250MB), engine loads in background thread
- OpenJDK 17 installed via Nix system dependencies
- Rate limiting is in-memory (resets on server restart)

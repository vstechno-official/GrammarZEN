# GrammarZen

A free, instant grammar correction web application powered by LanguageTool.

## Project Structure

```
src/
  main.py              - FastAPI server entry point (port 5000)
  grammar_engine.py    - Grammar checking engine using language-tool-python
  text_analyzer.py     - Sentiment analysis, readability scoring, and writing suggestions
  static/
    index.html         - Main HTML page
    app.js             - Frontend JavaScript
    style.css          - Styles (dark theme)
  requirements.txt     - Python package requirements (reference only)
```

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Grammar Engine**: language-tool-python (wraps LanguageTool, requires Java/OpenJDK 17)
- **NLP**: TextBlob, NLTK
- **Frontend**: Vanilla HTML/CSS/JS with Inter + JetBrains Mono fonts

## Dependencies

- **System**: openjdk17, gcc
- **Python**: fastapi, uvicorn, language-tool-python, textblob, nltk, python-multipart, aiofiles, httpx

## Running

The app runs via the "Start application" workflow: `python src/main.py`
Serves on port 5000 (webview).

# GrammarZen

A free grammar correction web application built with FastAPI (Python) and vanilla HTML/CSS/JS.

## Project Structure
- `src/main.py` - FastAPI application entry point
- `src/grammar_engine.py` - Grammar correction logic using language-tool-python
- `src/text_analyzer.py` - Sentiment analysis and readability calculations
- `src/static/index.html` - Main UI
- `src/static/style.css` - Application styling
- `src/static/app.js` - Frontend logic
- `src/static/logo.png` - App logo (GrammarZen brand logo)
- `attached_assets/` - Source image assets (not served by web server)

## Key Details
- Backend: FastAPI with uvicorn
- Frontend: Vanilla HTML/CSS/JS with Google Fonts (Inter, JetBrains Mono)
- Logo: `src/static/logo.png` used as both the header brand icon and browser favicon

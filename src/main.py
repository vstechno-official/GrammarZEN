import asyncio
import threading
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, field_validator
from grammar_engine import GrammarEngine
from text_analyzer import analyze_sentiment, calculate_readability, generate_suggestions
import uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(title="GrammarZen", version="1.0.0")
engine = GrammarEngine()


def preload_engine():
    time.sleep(1)
    engine.initialize()


threading.Thread(target=preload_engine, daemon=True).start()

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class TextRequest(BaseModel):
    text: str
    mode: str = "full"

    @field_validator('text')
    @classmethod
    def text_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        if len(v) > 10000:
            raise ValueError('Text exceeds 10000 character limit')
        return v


@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/health")
async def health():
    return JSONResponse({
        "status": "ok",
        "engine_ready": engine.is_ready(),
        "version": "1.0.0"
    })


@app.post("/api/correct")
async def correct_text(req: TextRequest):
    if not engine.is_ready():
        raise HTTPException(status_code=503, detail="Grammar engine is still loading. Please wait a moment.")
    try:
        result = await asyncio.get_event_loop().run_in_executor(None, engine.correct, req.text)
        sentiment, polarity = analyze_sentiment(req.text)
        readability = calculate_readability(req.text)
        suggestions = generate_suggestions(req.text, result.issues)
        return JSONResponse({
            "original_text": result.original_text,
            "corrected_text": result.corrected_text,
            "issues": [
                {
                    "offset": i.offset,
                    "length": i.length,
                    "message": i.message,
                    "replacements": i.replacements,
                    "rule_id": i.rule_id,
                    "category": i.category,
                    "context": i.context,
                    "severity": i.severity
                }
                for i in result.issues
            ],
            "score": result.score,
            "word_count": result.word_count,
            "sentence_count": result.sentence_count,
            "issue_count": result.issue_count,
            "suggestions": suggestions,
            "readability_score": readability,
            "sentiment": sentiment,
            "sentiment_polarity": polarity,
            "avg_sentence_length": result.avg_sentence_length,
            "vocabulary_richness": result.vocabulary_richness,
            "processing_time_ms": result.processing_time_ms
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False, workers=1)

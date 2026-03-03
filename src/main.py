import asyncio
import threading
import time
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Request
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

RATE_LIMIT_MAX = 3
RATE_LIMIT_WINDOW = 25 * 60
rate_limit_store = defaultdict(list)


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_rate_limit(client_ip: str) -> dict:
    now = time.time()
    timestamps = rate_limit_store[client_ip]
    rate_limit_store[client_ip] = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
    timestamps = rate_limit_store[client_ip]
    remaining = RATE_LIMIT_MAX - len(timestamps)
    if remaining <= 0:
        oldest = min(timestamps)
        reset_in = int(RATE_LIMIT_WINDOW - (now - oldest))
        return {"allowed": False, "remaining": 0, "reset_in": reset_in}
    return {"allowed": True, "remaining": remaining, "reset_in": 0}


def record_request(client_ip: str):
    rate_limit_store[client_ip].append(time.time())


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


@app.get("/api/docs")
async def api_docs():
    return FileResponse(os.path.join(STATIC_DIR, "api-docs.html"))


@app.get("/health")
async def health():
    return JSONResponse({
        "status": "ok",
        "engine_ready": engine.is_ready(),
        "version": "1.0.0"
    })


@app.get("/api")
async def api_get(request: Request, req: str = ""):
    if not req or not req.strip():
        return JSONResponse({
            "error": "Missing 'req' parameter",
            "usage": "/api?req=Your text here",
            "docs": "/api/docs"
        }, status_code=400)

    if len(req) > 10000:
        return JSONResponse({
            "error": "Text exceeds 10,000 character limit"
        }, status_code=400)

    if not engine.is_ready():
        return JSONResponse({
            "error": "Grammar engine is still loading. Please try again in a moment."
        }, status_code=503)

    client_ip = get_client_ip(request)
    limit_check = check_rate_limit(client_ip)

    if not limit_check["allowed"]:
        minutes = limit_check["reset_in"] // 60
        seconds = limit_check["reset_in"] % 60
        return JSONResponse({
            "error": "Rate limit exceeded",
            "message": f"You have used all {RATE_LIMIT_MAX} requests. Try again in {minutes}m {seconds}s.",
            "retry_after_seconds": limit_check["reset_in"]
        }, status_code=429, headers={
            "Retry-After": str(limit_check["reset_in"]),
            "X-RateLimit-Limit": str(RATE_LIMIT_MAX),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(limit_check["reset_in"])
        })

    record_request(client_ip)
    remaining = limit_check["remaining"] - 1

    try:
        result = await asyncio.get_event_loop().run_in_executor(None, engine.correct, req)
        sentiment, polarity = analyze_sentiment(req)
        readability = calculate_readability(req)
        suggestions = generate_suggestions(req, result.issues)

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
            "processing_time_ms": result.processing_time_ms,
            "rate_limit": {
                "remaining": remaining,
                "limit": RATE_LIMIT_MAX,
                "window": "25 minutes"
            }
        }, headers={
            "X-RateLimit-Limit": str(RATE_LIMIT_MAX),
            "X-RateLimit-Remaining": str(remaining)
        })
    except Exception as e:
        return JSONResponse({
            "error": str(e)
        }, status_code=500)


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

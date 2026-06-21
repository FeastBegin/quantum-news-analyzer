import os
import requests
import feedparser
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from backend.quantum_classifier import QuantumHypeClassifier
from backend.llm_analyzer import LLMAnalyzer

app = FastAPI(title="Quantum News Analyzer")

# Initialize models
quantum_classifier = QuantumHypeClassifier()
llm_analyzer = LLMAnalyzer()

class AnalysisRequest(BaseModel):
    text: str

class AnalysisResponse(BaseModel):
    hype_score: float
    features: list[float]
    summary: str
    keywords: list[str]
    is_mock: bool

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_text(request: AnalysisRequest):
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
        
    try:
        text_to_analyze = request.text
        # Check if text is a URL
        if text_to_analyze.startswith("http://") or text_to_analyze.startswith("https://"):
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(text_to_analyze, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract main text
            paragraphs = soup.find_all('p')
            text_to_analyze = ' '.join([p.get_text() for p in paragraphs])
            if not text_to_analyze.strip():
                raise Exception("Could not extract text from URL")

        # Step 1: LLM extracts features and summary
        features, summary, keywords = llm_analyzer.analyze_text(text_to_analyze)
        
        # Step 2: Qiskit calculates Hype Score based on features
        hype_score = quantum_classifier.calculate_hype_score(features)
        
        return AnalysisResponse(
            hype_score=hype_score,
            features=features,
            summary=summary,
            keywords=keywords,
            is_mock=llm_analyzer.is_mock
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class NewsResponse(BaseModel):
    title: str
    link: str
    date: str
    hype_score: float
    keywords: list[str]
    summary: str

@app.get("/api/news", response_model=list[NewsResponse])
async def get_news():
    try:
        # Fetch RSS feed
        url = "https://news.google.com/rss/search?q=quantum+computing&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        
        results = []
        # Take top 3 news items to limit API calls and processing time
        for entry in feed.entries[:3]:
            # Analyze title + description
            text_to_analyze = f"{entry.title}. {entry.description}"
            features, summary, keywords = llm_analyzer.analyze_text(text_to_analyze)
            hype_score = quantum_classifier.calculate_hype_score(features)
            
            results.append(NewsResponse(
                title=entry.title,
                link=entry.link,
                date=entry.published if hasattr(entry, 'published') else '',
                hype_score=hype_score,
                keywords=keywords,
                summary=summary
            ))
            
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount frontend static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
async def serve_frontend():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend not found. Please ensure frontend/index.html exists."}

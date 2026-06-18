import os
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
    is_mock: bool

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_text(request: AnalysisRequest):
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
        
    try:
        # Step 1: LLM extracts features and summary
        features, summary = llm_analyzer.analyze_text(request.text)
        
        # Step 2: Qiskit calculates Hype Score based on features
        hype_score = quantum_classifier.calculate_hype_score(features)
        
        return AnalysisResponse(
            hype_score=hype_score,
            features=features,
            summary=summary,
            is_mock=llm_analyzer.is_mock
        )
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

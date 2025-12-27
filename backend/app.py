"""
NFL Game Outcome Predictor - FastAPI Backend

This is the web API backend for the NFL game predictor.
It loads the trained ML model at startup and exposes REST endpoints
for predictions, team lists, and health checks.

Endpoints:
- GET /health - Health check
- GET /teams?season=2025 - Get valid teams for a season
- POST /predict - Predict game outcome
- GET / - Serve frontend (static files)

Run with:
    uvicorn backend.app:app --reload
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, validator
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path to import predictor_utils
sys.path.append(str(Path(__file__).parent.parent))
from src.predictor_utils import PredictorEngine

# Initialize FastAPI app
app = FastAPI(
    title="NFL Game Outcome Predictor API",
    description="Predict NFL game outcomes using machine learning",
    version="2.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global predictor engine (loaded once at startup)
predictor: Optional[PredictorEngine] = None


# Pydantic models for request/response validation
class PredictRequest(BaseModel):
    """Request model for game prediction."""
    home_team: str
    away_team: str
    season: Optional[int] = None
    
    @validator('home_team', 'away_team')
    def validate_team(cls, v):
        """Validate team name is not empty."""
        if not v or not v.strip():
            raise ValueError('Team name cannot be empty')
        return v.strip().upper()
    
    @validator('away_team')
    def teams_must_differ(cls, v, values):
        """Ensure home and away teams are different."""
        if 'home_team' in values and v == values['home_team']:
            raise ValueError('Home and away teams must be different')
        return v
    
    @validator('season')
    def validate_season(cls, v):
        """Validate season is reasonable."""
        if v is not None and (v < 2000 or v > 2030):
            raise ValueError('Season must be between 2000 and 2030')
        return v


class PredictResponse(BaseModel):
    """Response model for game prediction."""
    home_team: str
    away_team: str
    predicted_winner: str
    home_win_probability: float
    away_win_probability: float
    home_stats: dict
    away_stats: dict
    season: Optional[int]
    current_week: Optional[int]
    confidence: str


class TeamsResponse(BaseModel):
    """Response model for teams list."""
    season: Optional[int]
    teams: list
    count: int


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    model_loaded: bool
    trained_on_seasons: Optional[list]


@app.on_event("startup")
async def startup_event():
    """Load ML model at startup."""
    global predictor
    try:
        predictor = PredictorEngine()
        print("✅ Model loaded successfully")
        if predictor.metadata:
            print(f"   Trained on seasons: {predictor.metadata.get('trained_on_seasons', 'unknown')}")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("   Run 'python src/train_model.py' to train the model first")


@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Serve the frontend HTML."""
    frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)
    raise HTTPException(status_code=404, detail="Frontend not found")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns status of the API and whether the model is loaded.
    """
    return {
        "status": "ok",
        "model_loaded": predictor is not None,
        "trained_on_seasons": predictor.metadata.get('trained_on_seasons') if predictor else None
    }


@app.get("/teams", response_model=TeamsResponse)
async def get_teams(season: Optional[int] = Query(None, description="Season year (e.g., 2025)")):
    """
    Get list of valid team abbreviations.
    
    Args:
        season: Optional season to filter teams
    
    Returns:
        List of team abbreviations (e.g., ["KC", "BUF", "SF", ...])
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        teams = predictor.get_teams(season)
        return {
            "season": season,
            "teams": teams,
            "count": len(teams)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error getting teams: {str(e)}")


@app.post("/predict", response_model=PredictResponse)
async def predict_game(request: PredictRequest):
    """
    Predict the outcome of an NFL game.
    
    Args:
        request: Prediction request with home_team, away_team, and optional season
    
    Returns:
        Prediction results with winner, probabilities, and statistics
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Make prediction
        result = predictor.predict(
            home_team=request.home_team,
            away_team=request.away_team,
            season=request.season
        )
        
        # Add confidence level
        max_prob = max(result['home_win_probability'], result['away_win_probability'])
        if max_prob > 0.65:
            confidence = "High"
        elif max_prob > 0.55:
            confidence = "Moderate"
        else:
            confidence = "Low"
        
        result['confidence'] = confidence
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


# Mount static files for CSS and JS
try:
    frontend_dir = Path(__file__).parent.parent / "frontend"
    if frontend_dir.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
except Exception as e:
    print(f"Warning: Could not mount static files: {e}")


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("  NFL Game Outcome Predictor - Web API")
    print("="*70)
    print("\nStarting server...")
    print("Visit: http://localhost:8000")
    print("\nAPI Documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

# Backend - NFL Predictor API

FastAPI backend server for the NFL Game Outcome Predictor.

## Quick Start

```bash
# From project root directory:
uvicorn backend.app:app --reload
```

Then visit:
- **Web App**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "trained_on_seasons": [2022, 2023, 2024]
}
```

### GET /teams
Get list of teams for a season

**Parameters:**
- `season` (optional): Season year (e.g., 2025)

**Response:**
```json
{
  "season": 2025,
  "teams": ["ARI", "ATL", "BAL", ...],
  "count": 32
}
```

### POST /predict
Predict game outcome

**Request:**
```json
{
  "home_team": "KC",
  "away_team": "BUF",
  "season": 2025
}
```

**Response:**
```json
{
  "home_team": "KC",
  "away_team": "BUF",
  "predicted_winner": "KC",
  "home_win_probability": 0.68,
  "away_win_probability": 0.32,
  "home_stats": {
    "avg_points_for": 28.4,
    "avg_points_against": 19.2,
    "recent_form": 30.1
  },
  "away_stats": {
    "avg_points_for": 26.8,
    "avg_points_against": 20.5,
    "recent_form": 25.2
  },
  "season": 2025,
  "current_week": 10,
  "confidence": "High"
}
```

## Development

### Run with Auto-Reload
```bash
uvicorn backend.app:app --reload
```

Changes to `app.py` will automatically reload the server.

### Run on Different Port
```bash
uvicorn backend.app:app --reload --port 3000
```

### Run Programmatically
```bash
python backend/app.py
```

## Dependencies

- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Request/response validation

All installed via `requirements.txt` in project root.

## Architecture

The backend:
1. Loads ML model at startup (once)
2. Caches game data in memory
3. Validates all requests with Pydantic
4. Uses shared `predictor_utils.py` for predictions
5. Returns JSON responses
6. Serves frontend static files

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid input)
- `404`: Not found
- `500`: Server error
- `503`: Service unavailable (model not loaded)

Error responses include descriptive messages:
```json
{
  "detail": "Home and away teams must be different"
}
```

## CORS

CORS is enabled to allow requests from any origin during development.

For production, update `allow_origins` in `app.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    ...
)
```

## Performance

- Model loads once at startup
- Games data is cached in memory
- Predictions take 50-100ms
- Handles concurrent requests efficiently

## Testing

Use the interactive docs at `/docs` to test all endpoints in your browser!

Or use curl:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/teams?season=2025
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"home_team": "KC", "away_team": "BUF", "season": 2025}'
```

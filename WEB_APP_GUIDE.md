# NFL Predictor Web Application Guide

## 🌐 Architecture Overview

This application is now a full-stack web app with:

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│                 │  HTTP   │                  │  Loads  │                 │
│  Frontend       │ ───────▶│  FastAPI Backend │────────▶│  ML Model       │
│  (HTML/CSS/JS)  │◀─────── │  (Python)        │         │  (scikit-learn) │
│                 │  JSON   │                  │         │                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
```

### Frontend
- **Technology**: Vanilla JavaScript + HTML + CSS
- **Location**: `frontend/`
- **Purpose**: User interface for selecting teams and viewing predictions

### Backend
- **Technology**: FastAPI (Python web framework)
- **Location**: `backend/app.py`
- **Purpose**: REST API that serves predictions using the trained ML model

### Shared Logic
- **Location**: `src/predictor_utils.py`
- **Purpose**: Reusable prediction engine used by both CLI and web API

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies added:
- `fastapi` - Modern web framework
- `uvicorn` - ASGI server
- `python-multipart` - For form data

### 2. Ensure Model is Trained

If you haven't trained the model yet:

```bash
python src/train_model.py
```

Or with current season data:

```bash
python src/train_model.py --include-current 2025
```

### 3. Start the Backend

```bash
uvicorn backend.app:app --reload
```

You should see:
```
======================================================================
  NFL Game Outcome Predictor - Web API
======================================================================

Starting server...
Visit: http://localhost:8000

API Documentation: http://localhost:8000/docs

Press Ctrl+C to stop
======================================================================

INFO:     Uvicorn running on http://0.0.0.0:8000
✅ Model loaded successfully
   Trained on seasons: [2022, 2023, 2024]
```

### 4. Access the Web App

Open your browser and go to:

**http://localhost:8000**

That's it! The frontend is served by the backend automatically.

## 📡 API Endpoints

### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "trained_on_seasons": [2022, 2023, 2024]
}
```

### 2. Get Teams
```http
GET /teams?season=2025
```

**Response:**
```json
{
  "season": 2025,
  "teams": ["ARI", "ATL", "BAL", "BUF", "CAR", ...],
  "count": 32
}
```

### 3. Predict Game
```http
POST /predict
Content-Type: application/json

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

## 🧪 Testing the API

### Option 1: Interactive API Docs

FastAPI provides automatic interactive documentation:

**http://localhost:8000/docs**

You can test all endpoints directly from your browser!

### Option 2: Command Line (curl)

```bash
# Health check
curl http://localhost:8000/health

# Get teams
curl http://localhost:8000/teams?season=2025

# Predict game
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"home_team": "KC", "away_team": "BUF", "season": 2025}'
```

### Option 3: Python

```python
import requests

# Get teams
response = requests.get('http://localhost:8000/teams?season=2025')
teams = response.json()
print(teams)

# Predict game
response = requests.post('http://localhost:8000/predict', json={
    'home_team': 'KC',
    'away_team': 'BUF',
    'season': 2025
})
prediction = response.json()
print(prediction)
```

## 🎨 Frontend Features

The web interface includes:

1. **Season Selection** - Choose which season to analyze
2. **Team Dropdowns** - Select home and away teams (prevents duplicate selection)
3. **Smart Validation** - Can't pick same team twice
4. **Loading States** - Shows spinner while predicting
5. **Error Handling** - Clear error messages
6. **Beautiful Results** - Animated winner display with stats
7. **Responsive Design** - Works on desktop and mobile

## 🔄 How It Builds on the CLI Project

### Before (CLI Only)
```
User → src/predict_game.py → Model → Terminal Output
```

### After (CLI + Web)
```
User → frontend/index.html → backend/app.py → src/predictor_utils.py → Model → JSON → Beautiful UI
                              
OR

User → src/predict_game.py → src/predictor_utils.py → Model → Terminal Output
```

### Key Improvements

1. **Code Reuse**: `src/predictor_utils.py` contains shared logic
2. **No Duplication**: Prediction code isn't repeated
3. **Both Interfaces**: CLI still works, web app is added
4. **Same Model**: Both use the exact same trained model
5. **Consistent Results**: Same inputs give same outputs in CLI and web

## 🛠️ Development Tips

### Running with Auto-Reload

The `--reload` flag makes the backend restart when you change code:

```bash
uvicorn backend.app:app --reload
```

### Changing the Port

```bash
uvicorn backend.app:app --reload --port 3000
```

Then update `API_BASE_URL` in `frontend/script.js`:
```javascript
const API_BASE_URL = "https://nfl-game-predictor.onrender.com";
```

### Viewing Logs

Backend logs appear in the terminal where you ran `uvicorn`. They show:
- Incoming requests
- Errors
- Model predictions

## 📱 Frontend Development

The frontend is simple vanilla JS - no build process needed!

### File Structure
```
frontend/
├── index.html    # Page structure
├── style.css     # Styling
└── script.js     # Logic & API calls
```

### Making Changes

1. Edit any frontend file
2. Refresh browser (Ctrl+R / Cmd+R)
3. Changes appear immediately!

No webpack, no npm, no build step. Just edit and refresh.

## 🚨 Troubleshooting

### "Model not loaded"

**Problem**: Backend started but model file doesn't exist

**Solution**:
```bash
python src/train_model.py
```

### "Cannot connect to API"

**Problem**: Backend isn't running

**Solution**: Start the backend:
```bash
uvicorn backend.app:app --reload
```

### "No data found for season"

**Problem**: Data for that season hasn't been downloaded

**Solution**:
```bash
python src/update_data.py --season 2025
python src/build_games_dataset.py --season 2025
python src/build_features.py --season 2025
```

### CORS Errors in Browser Console

**Problem**: Frontend and backend on different domains

**Solution**: The app already has CORS enabled in `backend/app.py`. If you're still having issues, check that you're accessing the frontend through the backend (http://localhost:8000) not directly opening the HTML file.

### Port Already in Use

**Problem**: Port 8000 is taken by another process

**Solution**: Use a different port:
```bash
uvicorn backend.app:app --reload --port 8001
```

## 🎯 Next Steps

Now that you have a working web app, you can:

1. **Deploy it**: Use services like Heroku, Railway, or Render
2. **Add features**: 
   - Prediction history
   - Comparison of multiple games
   - Season statistics dashboard
3. **Improve UI**: Add charts, animations, team logos
4. **Mobile app**: Wrap in React Native or Flutter
5. **Share it**: Put it on your resume and GitHub!

## 📊 Performance Notes

- **Model loads once**: At startup, not per request
- **Fast predictions**: ~50-100ms per prediction
- **Caching**: Games data is cached in memory
- **Concurrent requests**: FastAPI handles multiple users

## 🎓 What You've Built

You now have:
- ✅ A real machine learning model (scikit-learn)
- ✅ A production-grade REST API (FastAPI)
- ✅ A responsive web frontend (HTML/CSS/JS)
- ✅ Automatic interactive docs (Swagger UI)
- ✅ Clean, maintainable code
- ✅ Both CLI and web interfaces
- ✅ Something impressive for your resume!

This demonstrates:
- Full-stack development skills
- ML engineering (not just notebooks)
- API design
- Clean code architecture
- Real-world application of ML

Perfect for showing employers you can build complete, production-ready applications!

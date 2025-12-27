"""
NFL Game Outcome Predictor - Shared Utilities

This module contains shared logic for both CLI and web API.
Avoids code duplication by providing reusable functions for:
- Loading models and data
- Computing team statistics
- Making predictions

Used by:
- src/predict_game.py (CLI)
- backend/app.py (Web API)
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import json


class PredictorEngine:
    """
    NFL game outcome prediction engine.
    Loads model once and reuses it for predictions.
    """
    
    def __init__(self, model_path: str = "models/logistic_regression.pkl",
                 scaler_path: str = "models/scaler.pkl",
                 metadata_path: str = "models/model_metadata.json"):
        """
        Initialize predictor with trained model.
        
        Args:
            model_path: Path to trained model file
            scaler_path: Path to feature scaler file
            metadata_path: Path to model metadata JSON
        """
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        
        # Load metadata if available
        self.metadata = {}
        if Path(metadata_path).exists():
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
        
        self.games_cache = {}  # Cache loaded games by season
    
    def load_games(self, season: Optional[int] = None) -> pd.DataFrame:
        """
        Load games dataset, using cache if available.
        
        Args:
            season: Optional season to load (e.g., 2025)
        
        Returns:
            DataFrame with game data
        """
        cache_key = f"season_{season}" if season else "all"
        
        if cache_key in self.games_cache:
            return self.games_cache[cache_key]
        
        processed_path = Path("data/processed")
        
        # Try season-specific file first
        if season:
            season_file = processed_path / f"games_{season}.csv"
            if season_file.exists():
                games = pd.read_csv(season_file)
                self.games_cache[cache_key] = games
                return games
        
        # Fall back to general file
        general_file = processed_path / "games.csv"
        if general_file.exists():
            games = pd.read_csv(general_file)
            self.games_cache[cache_key] = games
            return games
        
        raise FileNotFoundError(f"No games data found for season {season}")
    
    def get_team_stats(self, games: pd.DataFrame, team: str, 
                       season: Optional[int] = None) -> Tuple[float, float, float]:
        """
        Calculate team statistics from historical games.
        
        Args:
            games: DataFrame with game data
            team: Team abbreviation (e.g., "KC", "BUF")
            season: Optional season to filter
        
        Returns:
            Tuple of (avg_points_for, avg_points_against, recent_form)
        """
        # Filter to specific season if requested
        if season and 'season' in games.columns:
            games = games[games["season"] == season].copy()
        
        # Get all games where this team played
        home_games = games[games["home_team"] == team]
        away_games = games[games["away_team"] == team]
        
        # Combine points scored and allowed
        points_for = []
        points_against = []
        
        if not home_games.empty:
            points_for.extend(home_games["home_score"].tolist())
            points_against.extend(home_games["away_score"].tolist())
        
        if not away_games.empty:
            points_for.extend(away_games["away_score"].tolist())
            points_against.extend(away_games["home_score"].tolist())
        
        # Calculate averages
        if len(points_for) > 0:
            avg_points_for = np.mean(points_for)
            avg_points_against = np.mean(points_against)
            # Recent form: last 5 games
            recent_form = np.mean(points_for[-5:]) if len(points_for) >= 5 else avg_points_for
        else:
            # No data - return None to signal fallback needed
            return None, None, None
        
        return avg_points_for, avg_points_against, recent_form
    
    def get_league_average(self, games: pd.DataFrame) -> float:
        """Calculate league-wide average points."""
        all_scores = pd.concat([games["home_score"], games["away_score"]])
        return all_scores.mean()
    
    def predict(self, home_team: str, away_team: str, 
                season: Optional[int] = None) -> Dict[str, Any]:
        """
        Predict game outcome.
        
        Args:
            home_team: Home team abbreviation
            away_team: Away team abbreviation
            season: Optional season for context
        
        Returns:
            Dictionary with prediction results
        """
        # Load games data
        try:
            games = self.load_games(season)
        except FileNotFoundError as e:
            raise ValueError(f"Data not available: {str(e)}")
        
        # Get team statistics
        home_for, home_against, home_recent = self.get_team_stats(games, home_team, season)
        away_for, away_against, away_recent = self.get_team_stats(games, away_team, season)
        
        # Use league average as fallback
        league_avg = self.get_league_average(games)
        
        if home_for is None:
            home_for = league_avg
            home_against = league_avg
            home_recent = league_avg
        
        if away_for is None:
            away_for = league_avg
            away_against = league_avg
            away_recent = league_avg
        
        # Build feature vector
        features = {
            "home_team_avg_points_for": home_for,
            "home_team_avg_points_against": home_against,
            "away_team_avg_points_for": away_for,
            "away_team_avg_points_against": away_against,
            "home_recent_form": home_recent,
            "away_recent_form": away_recent,
            "home_field_advantage": 1
        }
        
        X = pd.DataFrame([features])
        X = X.fillna(0)  # Safety check
        
        # Scale and predict
        X_scaled = self.scaler.transform(X)
        prediction = int(self.model.predict(X_scaled)[0])
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        # Get current week if season provided
        current_week = None
        if season and 'week' in games.columns:
            season_games = games[games['season'] == season]
            if not season_games.empty:
                current_week = int(season_games['week'].max())
        
        # Build result
        result = {
            "home_team": home_team,
            "away_team": away_team,
            "predicted_winner": home_team if prediction == 1 else away_team,
            "home_win_probability": float(probabilities[1]),
            "away_win_probability": float(probabilities[0]),
            "home_stats": {
                "avg_points_for": float(home_for),
                "avg_points_against": float(home_against),
                "recent_form": float(home_recent)
            },
            "away_stats": {
                "avg_points_for": float(away_for),
                "avg_points_against": float(away_against),
                "recent_form": float(away_recent)
            },
            "season": season,
            "current_week": current_week
        }
        
        return result
    
    def get_teams(self, season: Optional[int] = None) -> list:
        """
        Get list of valid team abbreviations for a season.
        
        Args:
            season: Optional season to filter
        
        Returns:
            List of team abbreviations
        """
        try:
            games = self.load_games(season)
            teams = set()
            teams.update(games["home_team"].unique())
            teams.update(games["away_team"].unique())
            return sorted(list(teams))
        except Exception:
            return []

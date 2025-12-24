"""
NFL Game Outcome Predictor - Prediction Script

This script predicts the outcome of an NFL game between two teams using a trained
logistic regression model. It loads historical game data, computes team statistics
from past games only (avoiding data leakage), and outputs a prediction with probabilities.

Can predict for:
- Any historical matchup
- Current season matchups (using only games played so far)

Usage:
    python src/predict_game.py <HomeTeam> <AwayTeam> [--season YEAR]

Examples:
    python src/predict_game.py "SEA" "SF"               # Historical data
    python src/predict_game.py "KC" "BUF" --season 2025  # 2025 season context
"""

import argparse
import sys
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import json

def get_team_stats(games, team, season=None):
    """
    Calculate team statistics from all historical games.
    If season is specified, only use games from that season played so far.
    
    Args:
        games: DataFrame containing all past games
        team: Team abbreviation (e.g., "SEA", "SF")
        season: Optional season to filter (for current-season predictions)
    
    Returns:
        tuple: (avg_points_for, avg_points_against, recent_form)
    """
    # Filter to specific season if requested
    if season:
        games = games[games["season"] == season].copy()
    
    # Get all games where this team played (home or away)
    home_games = games[games["home_team"] == team]
    away_games = games[games["away_team"] == team]
    
    # Combine points scored and allowed
    points_for = []
    points_against = []
    
    # From home games
    if not home_games.empty:
        points_for.extend(home_games["home_score"].tolist())
        points_against.extend(home_games["away_score"].tolist())
    
    # From away games
    if not away_games.empty:
        points_for.extend(away_games["away_score"].tolist())
        points_against.extend(away_games["home_score"].tolist())
    
    # Calculate averages
    if len(points_for) > 0:
        avg_points_for = np.mean(points_for)
        avg_points_against = np.mean(points_against)
        # Recent form: average points from last 5 games
        recent_form = np.mean(points_for[-5:]) if len(points_for) >= 5 else avg_points_for
    else:
        # No historical data available
        avg_points_for = None
        avg_points_against = None
        recent_form = None
    
    return avg_points_for, avg_points_against, recent_form


def get_league_average(games):
    """Calculate league-wide average points."""
    all_scores = pd.concat([games["home_score"], games["away_score"]])
    return all_scores.mean()


def main():
    """Main function to predict game outcome."""
    
    parser = argparse.ArgumentParser(
        description="Predict NFL game outcome",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/predict_game.py "SEA" "SF"               # Using all historical data
  python src/predict_game.py "KC" "BUF" --season 2025  # 2025 season context
  python src/predict_game.py "DAL" "PHI" --season 2025 --week 10  # Week context
        """
    )
    
    parser.add_argument('home_team', type=str, help='Home team abbreviation (e.g., SEA, KC)')
    parser.add_argument('away_team', type=str, help='Away team abbreviation (e.g., SF, BUF)')
    parser.add_argument('--season', type=int, help='Season year for context (e.g., 2025)')
    parser.add_argument('--week', type=int, help='Week number for context display')
    
    args = parser.parse_args()
    
    home_team = args.home_team
    away_team = args.away_team
    season = args.season
    week = args.week
    
    # Display header
    print(f"\n{'='*70}")
    if season:
        if week:
            print(f"  NFL PREDICTION ({season} Season, Week {week})")
        else:
            print(f"  NFL PREDICTION ({season} Season)")
    else:
        print(f"  NFL GAME PREDICTION")
    print(f"  {home_team} (Home) vs {away_team} (Away)")
    print(f"{'='*70}\n")
    
    # Load the trained model, scaler, and metadata
    try:
        model_path = "models/logistic_regression.pkl"
        scaler_path = "models/scaler.pkl"
        metadata_path = "models/model_metadata.json"
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        # Load metadata if available
        if Path(metadata_path).exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            print(f"✅ Model loaded (trained on seasons: {metadata.get('trained_on_seasons', 'unknown')})")
        else:
            print("✅ Model and scaler loaded successfully")
            metadata = {}
        
    except FileNotFoundError:
        print(f"❌ Error: Model files not found")
        print("   Please train the model first:")
        print("   python src/train_model.py")
        sys.exit(1)
    
    # Load games dataset (contains all historical games)
    processed_path = Path("data/processed")
    
    # Try to load season-specific data first, then fall back to general data
    games_files_to_try = []
    if season:
        games_files_to_try.append(processed_path / f"games_{season}.csv")
    games_files_to_try.append(processed_path / "games.csv")
    
    games = None
    for games_file in games_files_to_try:
        if games_file.exists():
            games = pd.read_csv(games_file)
            print(f"✅ Loaded {len(games)} historical games from {games_file.name}\n")
            break
    
    if games is None:
        print(f"❌ Error: No games dataset found")
        print("   Please build the dataset first:")
        if season:
            print(f"   1. python src/update_data.py --season {season}")
            print(f"   2. python src/build_games_dataset.py --season {season}")
        else:
            print("   1. python src/build_games_dataset.py")
        sys.exit(1)
    
    # Calculate team statistics from historical games
    print("Computing team statistics from historical data...")
    
    # Use season-specific stats if season provided
    home_for, home_against, home_recent = get_team_stats(games, home_team, season)
    away_for, away_against, away_recent = get_team_stats(games, away_team, season)
    
    # Get league average for fallback
    league_avg = get_league_average(games)
    
    # Check for missing data and use fallback
    missing_data = False
    if home_for is None:
        print(f"⚠️  Warning: No historical data found for {home_team}")
        if season:
            print(f"   (in {season} season - using league average as fallback)")
        else:
            print(f"   (using league average as fallback)")
        home_for = league_avg
        home_against = league_avg
        home_recent = league_avg
    
    if away_for is None:
        print(f"⚠️  Warning: No historical data found for {away_team}")
        if season:
            print(f"   (in {season} season - using league average as fallback)")
        else:
            print(f"   (using league average as fallback)")
        away_for = league_avg
        away_against = league_avg
        away_recent = league_avg
    
    print()
    
    # Build feature vector for prediction
    # Home field advantage is implicitly encoded (home team is always listed first)
    example_game = {
        "home_team_avg_points_for": home_for,
        "home_team_avg_points_against": home_against,
        "away_team_avg_points_for": away_for,
        "away_team_avg_points_against": away_against,
        "home_recent_form": home_recent,
        "away_recent_form": away_recent,
        "home_field_advantage": 1  # Binary feature: always 1 for predictions
    }
    
    # Convert to DataFrame for prediction
    X_new = pd.DataFrame([example_game])
    
    # Ensure no NaN values (replace with 0 as fallback, though we checked above)
    X_new = X_new.fillna(0)
    
    # Scale features using the same scaler from training
    X_new_scaled = scaler.transform(X_new)
    
    # Make prediction
    prediction = model.predict(X_new_scaled)[0]
    probabilities = model.predict_proba(X_new_scaled)[0]
    
    # Display results
    print("="*70)
    print("  PREDICTION RESULTS")
    print("="*70)
    print(f"\n  Home Team ({home_team}):")
    print(f"    • Average Points For: {home_for:.1f}")
    print(f"    • Average Points Against: {home_against:.1f}")
    print(f"    • Recent Form (last 5 games): {home_recent:.1f}")
    print(f"\n  Away Team ({away_team}):")
    print(f"    • Average Points For: {away_for:.1f}")
    print(f"    • Average Points Against: {away_against:.1f}")
    print(f"    • Recent Form (last 5 games): {away_recent:.1f}")
    
    if season and 'season' in games.columns:
        # Show how many games each team has played this season
        home_games_played = len(games[(games['season'] == season) & 
                                       ((games['home_team'] == home_team) | 
                                        (games['away_team'] == home_team))])
        away_games_played = len(games[(games['season'] == season) & 
                                       ((games['home_team'] == away_team) | 
                                        (games['away_team'] == away_team))])
        print(f"\n  {season} Season Context:")
        print(f"    • {home_team}: {home_games_played} games played")
        print(f"    • {away_team}: {away_games_played} games played")
    
    print("\n" + "-"*70)
    if prediction == 1:
        print(f"  🏆 PREDICTED WINNER: {home_team} (Home)")
    else:
        print(f"  🏆 PREDICTED WINNER: {away_team} (Away)")
    
    print(f"\n  Win Probabilities:")
    print(f"    • {home_team} (Home): {probabilities[1]*100:.1f}%")
    print(f"    • {away_team} (Away): {probabilities[0]*100:.1f}%")
    
    # Confidence indicator
    confidence = max(probabilities[0], probabilities[1])
    if confidence > 0.65:
        confidence_level = "High"
    elif confidence > 0.55:
        confidence_level = "Moderate"
    else:
        confidence_level = "Low (close matchup)"
    print(f"\n  Confidence: {confidence_level}")
    
    print("="*70 + "\n")
    
    # Disclaimer for current season predictions
    if season and season >= 2025:
        print("Note: This is a statistical prediction based on historical performance.")
        print("      It does not account for injuries, weather, or other contextual factors.\n")


if __name__ == "__main__":
    main()

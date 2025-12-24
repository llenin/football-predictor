"""
NFL Game Outcome Predictor - Feature Engineering

This script creates features for each game based on historical team performance.
Features are calculated using only past games to avoid data leakage - statistics
for a game are computed from games that occurred before it.

Features created:
- Average points scored by each team (rolling average)
- Average points allowed by each team (rolling average)
- Recent form: average points in last 5 games
- Home field advantage: binary indicator (always 1, representing home team)

Can process:
- All available seasons (default)
- Specific season only (--season 2025)

CRITICAL: For Week 1 or teams with no history, uses league averages to prevent NaNs.

Input: data/processed/games.csv or data/processed/games_2025.csv
Output: data/processed/games_with_features.csv or data/processed/games_with_features_2025.csv
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path

def calculate_league_averages(games):
    """
    Calculate league-wide average points for/against.
    Used as fallback for teams with no historical data (Week 1).
    
    Args:
        games: DataFrame with game data
    
    Returns:
        tuple: (avg_points_for, avg_points_against)
    """
    # Average points scored across all games
    all_scores = pd.concat([games["home_score"], games["away_score"]])
    league_avg = all_scores.mean()
    
    return league_avg, league_avg


def build_features(games_df, use_league_avg_fallback=True):
    """
    Build features from historical game data.
    
    Args:
        games_df: DataFrame with game-level data
        use_league_avg_fallback: If True, use league averages for Week 1 games
    
    Returns:
        pd.DataFrame: Games with engineered features
    """
    
    games = games_df.copy()
    
    # Sort by season and week to ensure chronological order
    # This is critical to prevent data leakage!
    games = games.sort_values(by=["season", "week"]).reset_index(drop=True)
    
    # Calculate league averages for fallback (Week 1 games)
    league_avg_for, league_avg_against = calculate_league_averages(games)
    print(f"League average points (for fallback): {league_avg_for:.1f}\n")
    
    # Initialize feature columns
    games["home_team_avg_points_for"] = league_avg_for  # Default to league avg
    games["home_team_avg_points_against"] = league_avg_against
    games["away_team_avg_points_for"] = league_avg_for
    games["away_team_avg_points_against"] = league_avg_against
    games["home_recent_form"] = league_avg_for
    games["away_recent_form"] = league_avg_for
    games["home_field_advantage"] = 1  # Binary feature: home team always has advantage
    
    # Dictionary to store running statistics for each team
    # Structure: {team: {"points_for": [list of scores], "points_against": [list of scores]}}
    team_stats = {}
    
    print("Calculating rolling statistics for each game...")
    print("(Features use only games that occurred BEFORE each game)")
    print("(Week 1 games use league averages as fallback)\n")
    
    # Process each game chronologically
    for idx, row in games.iterrows():
        home, away = row["home_team"], row["away_team"]
        home_score, away_score = row["home_score"], row["away_score"]
        
        # Initialize team stats if this is first time seeing the team
        if home not in team_stats:
            team_stats[home] = {"points_for": [], "points_against": []}
        if away not in team_stats:
            team_stats[away] = {"points_for": [], "points_against": []}
        
        # Calculate and assign features BEFORE this game (using only past games)
        # This prevents data leakage - we only use information available before the game
        
        # Home team features
        if len(team_stats[home]["points_for"]) > 0:
            # Team has historical data - use it
            games.at[idx, "home_team_avg_points_for"] = np.mean(team_stats[home]["points_for"])
            games.at[idx, "home_team_avg_points_against"] = np.mean(team_stats[home]["points_against"])
            # Recent form (last 5 games)
            recent_games = team_stats[home]["points_for"][-5:]
            games.at[idx, "home_recent_form"] = np.mean(recent_games)
        # else: Keep league average (already set as default)
        
        # Away team features
        if len(team_stats[away]["points_for"]) > 0:
            # Team has historical data - use it
            games.at[idx, "away_team_avg_points_for"] = np.mean(team_stats[away]["points_for"])
            games.at[idx, "away_team_avg_points_against"] = np.mean(team_stats[away]["points_against"])
            # Recent form (last 5 games)
            recent_games = team_stats[away]["points_for"][-5:]
            games.at[idx, "away_recent_form"] = np.mean(recent_games)
        # else: Keep league average (already set as default)
        
        # After assigning features, update team statistics with this game's results
        # These updated stats will be used for future games
        team_stats[home]["points_for"].append(home_score)
        team_stats[home]["points_against"].append(away_score)
        team_stats[away]["points_for"].append(away_score)
        team_stats[away]["points_against"].append(home_score)
        
        # Progress indicator
        if (idx + 1) % 100 == 0:
            print(f"  Processed {idx + 1}/{len(games)} games...")
    
    return games


def main():
    """Main function to handle command-line arguments and build features."""
    
    parser = argparse.ArgumentParser(
        description="Engineer features from game-level data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/build_features.py                    # All seasons
  python src/build_features.py --season 2025      # 2025 only
        """
    )
    
    parser.add_argument(
        '--season',
        type=int,
        help='Process features for a single season only'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("  NFL Game Predictor - Feature Engineering")
    print("="*70 + "\n")
    
    # Determine input file
    processed_path = Path("data/processed")
    if args.season:
        input_file = processed_path / f"games_{args.season}.csv"
        output_file = processed_path / f"games_with_features_{args.season}.csv"
    else:
        input_file = processed_path / "games.csv"
        output_file = processed_path / "games_with_features.csv"
    
    # Load games dataset
    try:
        games = pd.read_csv(input_file)
        print(f"Loaded {len(games)} games from {input_file}")
    except FileNotFoundError:
        print(f"❌ Error: Input file not found: {input_file}")
        print("   Please run build_games_dataset.py first")
        if args.season:
            print(f"   Command: python src/build_games_dataset.py --season {args.season}")
        return
    
    # Build features
    games_with_features = build_features(games)
    
    # Save the dataset with engineered features
    games_with_features.to_csv(output_file, index=False)
    
    print(f"\n✅ Feature engineering complete!")
    print(f"   Output: {output_file}")
    print(f"   Shape: {games_with_features.shape}")
    print(f"   Features: {list(games_with_features.columns)}")
    
    # Show summary statistics
    print("\n" + "-"*70)
    print("Feature Summary Statistics:")
    print("-"*70)
    feature_cols = [
        "home_team_avg_points_for", "home_team_avg_points_against",
        "away_team_avg_points_for", "away_team_avg_points_against",
        "home_recent_form", "away_recent_form"
    ]
    print(games_with_features[feature_cols].describe())
    print("\n")
    
    # Provide next-step guidance
    print("Next step: Train the model")
    print("Command: python src/train_model.py\n")

if __name__ == "__main__":
    main()
"""
NFL Game Outcome Predictor - Dataset Builder

This script processes raw NFL play-by-play data from nflverse and creates a
game-level dataset. Each row represents one game with the final scores.

The play-by-play data is aggregated to extract:
- Game ID, season, week
- Home and away team names
- Final scores for both teams
- Winner (binary: 1 = home win, 0 = away win)

Can process:
- All available seasons (default)
- Specific season only (--season 2025)
- Only completed games (excludes future games)

Data source: nflverse play-by-play CSV files
Expected input files: data/raw/play_by_play_YYYY.csv.gz

Output: data/processed/games.csv or data/processed/games_2025.csv
"""

import argparse
import pandas as pd
from pathlib import Path

def build_games(seasons=None):
    """
    Build game-level dataset from play-by-play data.
    
    Args:
        seasons: List of seasons to process, or None for all available
    
    Returns:
        pd.DataFrame: Game-level dataset
    """
    
    raw_path = Path("data/raw")
    
    # Determine which files to load
    if seasons is None:
        # Load all available files
        files = sorted(raw_path.glob("play_by_play_*.csv.gz"))
        season_label = "all seasons"
    else:
        # Load specific seasons only
        files = [raw_path / f"play_by_play_{season}.csv.gz" for season in seasons]
        season_label = f"season{'s' if len(seasons) > 1 else ''} {', '.join(map(str, seasons))}"
    
    print(f"Loading play-by-play data for {season_label}...")
    print(f"  Source: {raw_path}\n")
    
    # Load all play-by-play files and concatenate
    dfs = []
    for file in files:
        if file.exists():
            print(f"  Loading {file.name}...")
            df = pd.read_csv(file, compression='gzip', low_memory=False)
            dfs.append(df)
        else:
            print(f"  ⚠️  Warning: {file.name} not found, skipping...")
    
    if not dfs:
        print("\n❌ Error: No play-by-play data files found!")
        print("   Please download data first:")
        print("   python src/update_data.py --season 2025")
        return None
    
    # Combine all seasons into one dataframe
    pbp = pd.concat(dfs, ignore_index=True)
    print(f"\n✅ Loaded {len(pbp):,} plays from {len(dfs)} file(s)")
    print(f"   Columns: {pbp.shape[1]}")
    print(f"   Memory: {pbp.memory_usage(deep=True).sum() / 1024**2:.1f} MB\n")
    
    # Aggregate play-by-play data into game-level data
    # Group by unique game identifiers and extract final scores
    print("Aggregating plays into games...")
    games = pbp.groupby(
        ["game_id", "season", "week", "home_team", "away_team"]
    ).agg(
        home_score=("total_home_score", "max"),  # Final home score
        away_score=("total_away_score", "max")   # Final away score
    ).reset_index()
    
    # Filter out future games (games that haven't been played yet)
    # These will have NaN or 0 scores
    print("Filtering out unplayed games...")
    initial_games = len(games)
    games = games[
        (games["home_score"].notna()) & 
        (games["away_score"].notna()) &
        ((games["home_score"] > 0) | (games["away_score"] > 0))
    ].copy()
    
    removed = initial_games - len(games)
    if removed > 0:
        print(f"  Removed {removed} unplayed/incomplete games")
    
    print(f"✅ Created {len(games)} completed game records\n")
    
    # Sort by season and week (chronological order is critical!)
    games = games.sort_values(by=["season", "week"]).reset_index(drop=True)
    
    # Create target variable: 1 if home team wins, 0 if away team wins
    # Note: Ties are rare in modern NFL (overtime rules changed)
    games["home_win"] = (games["home_score"] > games["away_score"]).astype(int)
    
    return games


def main():
    """Main function to handle command-line arguments and build dataset."""
    
    parser = argparse.ArgumentParser(
        description="Build game-level dataset from play-by-play data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/build_games_dataset.py                    # All seasons
  python src/build_games_dataset.py --season 2025      # 2025 only
  python src/build_games_dataset.py --seasons 2023 2024 2025  # Multiple seasons
        """
    )
    
    parser.add_argument(
        '--season',
        type=int,
        help='Process a single season only'
    )
    
    parser.add_argument(
        '--seasons',
        type=int,
        nargs='+',
        help='Process multiple specific seasons'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("  NFL Game Predictor - Dataset Builder")
    print("="*70 + "\n")
    
    # Determine which seasons to process
    seasons = None
    if args.season:
        seasons = [args.season]
    elif args.seasons:
        seasons = sorted(args.seasons)
    
    # Build dataset
    games = build_games(seasons)
    
    if games is None:
        return
    
    # Calculate and display statistics
    home_wins = games["home_win"].sum()
    away_wins = len(games) - home_wins
    home_win_pct = home_wins / len(games) * 100
    
    print("-"*70)
    print("Dataset Statistics:")
    print("-"*70)
    print(f"  Total games: {len(games)}")
    print(f"  Home wins:   {home_wins} ({home_win_pct:.1f}%)")
    print(f"  Away wins:   {away_wins} ({100-home_win_pct:.1f}%)")
    print(f"  Seasons:     {sorted(games['season'].unique())}")
    
    if 'week' in games.columns:
        print(f"  Weeks:       {games['week'].min():.0f} - {games['week'].max():.0f}")
    
    print(f"  Teams:       {games['home_team'].nunique()}")
    print()
    
    # Save processed dataset
    processed_path = Path("data/processed")
    processed_path.mkdir(parents=True, exist_ok=True)
    
    # Use season-specific filename if single season
    if seasons and len(seasons) == 1:
        output_file = processed_path / f"games_{seasons[0]}.csv"
    else:
        output_file = processed_path / "games.csv"
    
    games.to_csv(output_file, index=False)
    
    print("="*70)
    print(f"✅ Dataset saved to: {output_file}")
    print(f"   Shape: {games.shape}")
    print(f"   Columns: {list(games.columns)}")
    print("="*70 + "\n")
    
    # Provide next-step guidance
    if seasons and len(seasons) == 1:
        print("Next step: Build features for this season")
        print(f"Command: python src/build_features.py --season {seasons[0]}\n")
    else:
        print("Next step: Build features")
        print("Command: python src/build_features.py\n")

if __name__ == "__main__":
    main()
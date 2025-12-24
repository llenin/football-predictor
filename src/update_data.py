"""
NFL Game Outcome Predictor - Data Update Script

This script downloads the latest NFL play-by-play data using nfl_data_py
and saves it to the data/raw/ directory. Use this to get current-season data
for live predictions during the NFL season.

Usage:
    python src/update_data.py --season 2025
    python src/update_data.py --season 2024

The script will:
- Download play-by-play data for the specified season
- Save as compressed CSV (play_by_play_YYYY.csv.gz)
- Overwrite existing files if they exist
- Display download statistics

Data source: nflverse via nfl_data_py
"""

import argparse
import pandas as pd
from pathlib import Path
import nfl_data_py as nfl

def update_season_data(season):
    """
    Download and save play-by-play data for a specific season.
    
    Args:
        season: Integer year (e.g., 2025)
    
    Returns:
        tuple: (success: bool, rows: int, file_path: str)
    """
    print("\n" + "="*70)
    print(f"  NFL Data Updater - Season {season}")
    print("="*70 + "\n")
    
    try:
        # Download play-by-play data using nfl_data_py
        print(f"📥 Downloading play-by-play data for {season} season...")
        print("   (This may take 30-60 seconds for a full season)\n")
        
        pbp_data = nfl.import_pbp_data([season])
        
        if pbp_data.empty:
            print(f"⚠️  Warning: No data available for {season} season yet")
            print("   The season may not have started or data may not be published")
            return False, 0, None
        
        # Prepare output path
        raw_path = Path("data/raw")
        raw_path.mkdir(parents=True, exist_ok=True)
        
        output_file = raw_path / f"play_by_play_{season}.csv.gz"
        
        # Save as compressed CSV
        print(f"💾 Saving data to {output_file}...")
        pbp_data.to_csv(output_file, index=False, compression='gzip')
        
        # Display statistics
        rows = len(pbp_data)
        size_mb = output_file.stat().st_size / (1024 * 1024)
        
        print("\n" + "="*70)
        print("  DOWNLOAD COMPLETE")
        print("="*70)
        print(f"\n  Season:        {season}")
        print(f"  Rows loaded:   {rows:,} plays")
        print(f"  File size:     {size_mb:.1f} MB")
        print(f"  Saved to:      {output_file}")
        
        # Show week range if available
        if 'week' in pbp_data.columns:
            weeks = pbp_data['week'].dropna().unique()
            if len(weeks) > 0:
                min_week = int(weeks.min())
                max_week = int(weeks.max())
                print(f"  Weeks:         {min_week} - {max_week}")
        
        # Show games count
        if 'game_id' in pbp_data.columns:
            games = pbp_data['game_id'].nunique()
            print(f"  Games:         {games}")
        
        print("\n" + "="*70 + "\n")
        
        return True, rows, str(output_file)
        
    except Exception as e:
        print(f"\n❌ Error downloading data: {e}")
        print("   Please check:")
        print("   1. Internet connection")
        print("   2. nfl_data_py is installed: pip install nfl_data_py")
        print("   3. Season year is valid (e.g., 2022-2025)")
        return False, 0, None


def main():
    """Main function to handle command-line arguments and update data."""
    
    parser = argparse.ArgumentParser(
        description="Download latest NFL play-by-play data for predictions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/update_data.py --season 2025
  python src/update_data.py --season 2024
  
After updating data, run:
  1. python src/build_games_dataset.py --season 2025
  2. python src/build_features.py --season 2025
  3. python src/train_model.py
  4. python src/predict_game.py "KC" "BUF" --season 2025
        """
    )
    
    parser.add_argument(
        '--season',
        type=int,
        default=2025,
        help='NFL season year to download (default: 2025)'
    )
    
    args = parser.parse_args()
    
    # Validate season
    if args.season < 2000 or args.season > 2030:
        print(f"❌ Error: Invalid season {args.season}")
        print("   Season must be between 2000 and 2030")
        return
    
    # Download data
    success, rows, file_path = update_season_data(args.season)
    
    if success:
        print("✅ Data update successful!")
        print("\nNext steps:")
        print(f"  1. Build games:    python src/build_games_dataset.py --season {args.season}")
        print(f"  2. Build features: python src/build_features.py --season {args.season}")
        print(f"  3. Train model:    python src/train_model.py")
        print(f"  4. Make prediction: python src/predict_game.py \"KC\" \"BUF\" --season {args.season}")
    else:
        print("\n❌ Data update failed")


if __name__ == "__main__":
    main()

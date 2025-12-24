"""
Quick Start Guide - NFL Game Outcome Predictor

This script demonstrates how to use the NFL predictor step by step.
Run this after setting up the environment and downloading data.
"""

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def main():
    print_section("NFL GAME OUTCOME PREDICTOR - QUICK START")
    
    print("This project predicts NFL game outcomes using machine learning.")
    print("Follow these steps to set up and use the predictor:\n")
    
    print("STEP 1: Install Dependencies")
    print("-" * 70)
    print("  pip install -r requirements.txt")
    print()
    
    print("STEP 2: Download Data")
    print("-" * 70)
    print("  Visit: https://github.com/nflverse/nflverse-data/releases")
    print("  Download: play_by_play_2022.csv.gz, play_by_play_2023.csv.gz, etc.")
    print("  Place files in: data/raw/")
    print()
    
    print("STEP 3: Build Game Dataset")
    print("-" * 70)
    print("  python src/build_games_dataset.py")
    print("  → Converts play-by-play data to game-level data")
    print()
    
    print("STEP 4: Engineer Features")
    print("-" * 70)
    print("  python src/build_features.py")
    print("  → Creates predictive features from historical stats")
    print()
    
    print("STEP 5: Train Model")
    print("-" * 70)
    print("  python src/train_model.py")
    print("  → Trains logistic regression model")
    print("  → Displays accuracy and evaluation metrics")
    print()
    
    print("STEP 6: Make Predictions!")
    print("-" * 70)
    print('  python src/predict_game.py "SEA" "SF"')
    print('  python src/predict_game.py "KC" "BUF"')
    print('  python src/predict_game.py "DAL" "PHI"')
    print()
    
    print_section("COMMON TEAM ABBREVIATIONS")
    
    teams = {
        "AFC East": ["BUF", "MIA", "NE", "NYJ"],
        "AFC North": ["BAL", "CIN", "CLE", "PIT"],
        "AFC South": ["HOU", "IND", "JAX", "TEN"],
        "AFC West": ["DEN", "KC", "LV", "LAC"],
        "NFC East": ["DAL", "NYG", "PHI", "WAS"],
        "NFC North": ["CHI", "DET", "GB", "MIN"],
        "NFC South": ["ATL", "CAR", "NO", "TB"],
        "NFC West": ["ARI", "LA", "SF", "SEA"]
    }
    
    for division, teams_list in teams.items():
        print(f"{division:15s} {', '.join(teams_list)}")
    
    print_section("EXAMPLE PREDICTIONS")
    
    print("Try predicting these classic rivalries:")
    print()
    print('  python src/predict_game.py "GB" "CHI"    # Packers vs Bears')
    print('  python src/predict_game.py "DAL" "WAS"   # Cowboys vs Washington')
    print('  python src/predict_game.py "SF" "SEA"    # 49ers vs Seahawks')
    print('  python src/predict_game.py "NE" "NYJ"    # Patriots vs Jets')
    print('  python src/predict_game.py "PIT" "BAL"   # Steelers vs Ravens')
    print()
    
    print_section("TROUBLESHOOTING")
    
    print("Problem: 'No historical data found for team'")
    print("Solution: Check team abbreviation (must be exact, e.g., 'SEA' not 'Seahawks')")
    print()
    print("Problem: 'Model file not found'")
    print("Solution: Run 'python src/train_model.py' first")
    print()
    print("Problem: 'Games dataset not found'")
    print("Solution: Run 'python src/build_games_dataset.py' and 'python src/build_features.py'")
    print()
    
    print_section("PROJECT STRUCTURE")
    
    print("football-predictor/")
    print("├── data/")
    print("│   ├── raw/              # Place downloaded CSV.GZ files here")
    print("│   └── processed/        # Generated game datasets")
    print("├── models/               # Trained model files")
    print("├── src/                  # Python scripts")
    print("│   ├── build_games_dataset.py")
    print("│   ├── build_features.py")
    print("│   ├── train_model.py")
    print("│   └── predict_game.py")
    print("├── requirements.txt")
    print("└── README.md")
    print()
    
    print("="*70)
    print("  For more details, see README.md")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

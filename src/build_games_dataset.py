import pandas as pd
from pathlib import Path

# Point to raw data folder
raw_path = Path("data/raw")
files = [
    raw_path / "play_by_play_2022.csv.gz",
    raw_path / "play_by_play_2023.csv.gz",
    raw_path / "play_by_play_2024.csv.gz"
]

# Load pbp data
dfs = [pd.read_csv(f, low_memory=False) for f in files]
pbp = pd.concat(dfs, ignore_index=True)

print("Loaded play-by-play:", pbp.shape)

# Aggregate into games
games = pbp.groupby(["game_id", "season", "week", "home_team", "away_team"]).agg(
    home_score=("total_home_score", "max"),
    away_score=("total_away_score", "max")
).reset_index()

# Add target label (1 = home win, 0 = away win)
games["home_win"] = (games["home_score"] > games["away_score"]).astype(int)

# save processed dataset
processed_path = Path("data/processed")
processed_path.mkdir(parents=True, exist_ok=True)
games.to_csv(processed_path / "games.csv", index=False)

print("Saved games dataset:", games.shape)
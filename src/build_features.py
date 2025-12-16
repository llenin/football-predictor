import pandas as pd

# load games dataset
games = pd.read_csv("data/processed/games.csv")

# sort by season/week to calculate rolling stats
games = games.sort_values(by=["season", "week"])

# prepare feature columns
games["home_team_avg_points_for"] = 0.0
games["home_team_avg_points_against"] = 0.0
games["away_team_avg_points_for"] = 0.0
games["away_team_avg_points_against"] = 0.0

# store team stats as we move week by week
team_stats = {}

for idx, row in games.iterrows():
    home, away = row["home_team"], row["away_team"]
    home_score, away_score = row["home_score"], row["away_score"]

    # initialize team stats if new
    if home not in team_stats:
        team_stats[home] = {"points_for": [], "points_against": []}
    if away not in team_stats:
        team_stats[away] = {"points_for": [], "points_against": []}

    # assign rolling averges BEFORE this game
    if team_stats[home]["points_for"]:
        games.at[idx, "home_team_avg_points_for"] = sum(team_stats[home]["points_for"]) / len(team_stats[home]["points_for"])
        games.at[idx, "home_team_avg_points_against"] = sum(team_stats[home]["points_against"]) / len(team_stats[home]["points_against"])
    if team_stats[away]["points_for"]:
        games.at[idx, "away_team_avg_points_for"] = sum(team_stats[away]["points_for"]) / len(team_stats[away]["points_for"])
        games.at[idx, "away_team_avg_points_against"] = sum(team_stats[away]["points_against"]) / len(team_stats[away]["points_against"])

    # after assigning, update team stats with this game
    team_stats[home]["points_for"].append(home_score)
    team_stats[home]["points_against"].append(away_score)
    team_stats[away]["points_for"].append(away_score)
    team_stats[away]["points_against"].append(home_score)

# Save engineered dataset
games.to_csv("data/processed/games_with_features.csv", index=False)
print("✅ Saved games_with_features.csv:", games.shape)
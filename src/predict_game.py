import sys
import joblib
import pandas as pd

# Load model
model_path = "models/logistic_regression.pkl"
model = joblib.load(model_path)
print("✅ Model loaded successfully")

# Load games dataset
games_path = "data/processed/games.csv"
games = pd.read_csv(games_path)

# Check command-line arguments
if len(sys.argv) != 3:
    print("Usage: python src/predict_game.py 'HomeTeam' 'AwayTeam'")
    sys.exit(1)

home_team = sys.argv[1]
away_team = sys.argv[2]

# Calculate averages for the teams
def get_team_stats(team, is_home=True):
    if is_home:
        team_games = games[games["home_team"] == team]
        avg_points_for = team_games["home_score"].mean()
        avg_points_against = team_games["away_score"].mean()
    else:
        team_games = games[games["away_team"] == team]
        avg_points_for = team_games["away_score"].mean()
        avg_points_against = team_games["home_score"].mean()
    return avg_points_for, avg_points_against

home_for, home_against = get_team_stats(home_team, is_home=True)
away_for, away_against = get_team_stats(away_team, is_home=False)

# Build input row
example_game = {
    "home_team_avg_points_for": home_for,
    "home_team_avg_points_against": home_against,
    "away_team_avg_points_for": away_for,
    "away_team_avg_points_against": away_against
}

# X_new = pd.DataFrame([example_game])

# Handle missing values
X_new = X_new.fillna(0)

# Predict outcome
prediction = model.predict(X_new)[0]
probabilities = model.predict_proba(X_new)[0]

print(f"\nPrediction result: {home_team} vs {away_team}")
print("🏠 Home Team Win" if prediction == 1 else "🛫 Away Team Win")
print(f"Confidence → {home_team}: {probabilities[1]:.2f}, {away_team}: {probabilities[0]:.2f}")

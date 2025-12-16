import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib
import os

# Load data
games = pd.read_csv("data/processed/games_with_features.csv")

# Select features (X) and target (y)
features = [
    "home_team_avg_points_for",
    "home_team_avg_points_against",
    "away_team_avg_points_for",
    "away_team_avg_points_against"
]
X = games[features]
y = games["home_win"]

# Drop rows with missing values (first few games of a season may have NaNs)
X = X.dropna()
y = y.loc[X.index]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train logistic regression
model = LogisticRegression()
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("✅ Model trained")
print("Test Accuracy:", round(accuracy, 3))

# Save model
os.makedirs("models", exist_ok=True)
model_path = "models/logistic_regression.pkl"
joblib.dump(model, model_path)
print(f"Model saved to {model_path}")
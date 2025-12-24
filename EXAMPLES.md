# NFL Game Outcome Predictor - Usage Examples

## Quick Command Reference

### Setup (One Time)
```bash
# Install dependencies
pip install -r requirements.txt

# Build dataset from raw data
python src/build_games_dataset.py

# Engineer features
python src/build_features.py

# Train the model
python src/train_model.py
```

### Make Predictions (Anytime)
```bash
# Basic usage
python src/predict_game.py "<HomeTeam>" "<AwayTeam>"

# Examples
python src/predict_game.py "SEA" "SF"
python src/predict_game.py "KC" "BUF"
python src/predict_game.py "DAL" "PHI"
```

## Example Output

### Training the Model
```
============================================================
  NFL Game Outcome Predictor - Model Training
============================================================

Loading data...
✅ Loaded 825 games with features

Cleaning data...
  Removed 32 games with missing features
  Training set: 793 games

Train set: 634 games
Test set:  159 games
Home win rate in training: 57.4%

Scaling features...
✅ Features scaled (mean=0, std=1)

Training logistic regression model...
✅ Model trained successfully

============================================================
  MODEL EVALUATION RESULTS
============================================================

Training Accuracy: 62.5%
Test Accuracy:     61.0%
Baseline (always predict home win): 57.2%

Model improvement over baseline: 3.8%

------------------------------------------------------------
Classification Report:
------------------------------------------------------------
              precision    recall  f1-score   support

    Away Win      0.583     0.574     0.578        68
    Home Win      0.629     0.637     0.633        91

    accuracy                          0.610       159
   macro avg      0.606     0.606     0.606       159
weighted avg      0.610     0.610     0.610       159

------------------------------------------------------------
Feature Importance (Logistic Regression Coefficients):
------------------------------------------------------------
  home_team_avg_points_for            +0.4521
  away_team_avg_points_against        +0.3892
  home_recent_form                    +0.2134
  ...

✅ Model saved to: models/logistic_regression.pkl
✅ Scaler saved to: models/scaler.pkl
```

### Making a Prediction
```
============================================================
  NFL GAME PREDICTION: SEA (Home) vs SF (Away)
============================================================

✅ Model and scaler loaded successfully
✅ Loaded 825 historical games

Computing team statistics from historical data...

============================================================
  PREDICTION RESULTS
============================================================

  Home Team (SEA):
    • Average Points For: 23.4
    • Average Points Against: 21.8
    • Recent Form (last 5 games): 24.1

  Away Team (SF):
    • Average Points For: 25.2
    • Average Points Against: 19.5
    • Recent Form (last 5 games): 26.3

------------------------------------------------------------
  🏆 PREDICTED WINNER: SF (Away)

  Win Probabilities:
    • SEA (Home): 42.3%
    • SF (Away): 57.7%
============================================================
```

## Common Team Codes

| Division | Teams |
|----------|-------|
| **AFC East** | BUF, MIA, NE, NYJ |
| **AFC North** | BAL, CIN, CLE, PIT |
| **AFC South** | HOU, IND, JAX, TEN |
| **AFC West** | DEN, KC, LV, LAC |
| **NFC East** | DAL, NYG, PHI, WAS |
| **NFC North** | CHI, DET, GB, MIN |
| **NFC South** | ATL, CAR, NO, TB |
| **NFC West** | ARI, LA, SF, SEA |

## Classic Rivalry Predictions

Try these matchups:
```bash
# NFC North Rivalry
python src/predict_game.py "GB" "CHI"

# NFC East Rivalry  
python src/predict_game.py "DAL" "WAS"
python src/predict_game.py "PHI" "NYG"

# AFC East Rivalry
python src/predict_game.py "NE" "NYJ"
python src/predict_game.py "BUF" "MIA"

# AFC North Rivalry
python src/predict_game.py "PIT" "BAL"
python src/predict_game.py "CIN" "CLE"

# NFC West Rivalry
python src/predict_game.py "SF" "SEA"
python src/predict_game.py "LA" "ARI"

# Cross-Conference
python src/predict_game.py "KC" "TB"
python src/predict_game.py "BUF" "LA"
```

## Troubleshooting

### Error: "No historical data found for team"
**Cause:** Team abbreviation is incorrect or not in dataset  
**Solution:** 
- Use exact 2-3 letter codes (e.g., "SEA" not "Seahawks")
- Check spelling (case-sensitive)
- Refer to team codes table above

### Error: "Model file not found"
**Cause:** Model hasn't been trained yet  
**Solution:** Run `python src/train_model.py`

### Error: "Games dataset not found"
**Cause:** Dataset hasn't been built  
**Solution:** 
1. Run `python src/build_games_dataset.py`
2. Run `python src/build_features.py`
3. Run `python src/train_model.py`

### Low Confidence Predictions
**Why:** Teams are very evenly matched based on historical stats  
**Interpretation:** Close games are harder to predict (realistic!)

## Tips for Best Results

1. **More data is better:** Include multiple seasons for more reliable statistics
2. **Recent seasons matter:** More recent data may be more relevant
3. **Check team names:** Use exact abbreviations from the table
4. **Understand probabilities:** 60% is good for sports prediction!
5. **Context matters:** Model doesn't know about injuries, weather, etc.

## Project Workflow Diagram

```
Raw Data (nflverse)
        ↓
  build_games_dataset.py  →  games.csv
        ↓
   build_features.py      →  games_with_features.csv
        ↓
    train_model.py        →  logistic_regression.pkl + scaler.pkl
        ↓
   predict_game.py        →  Prediction + Probabilities
```

## What The Model Learns

The logistic regression model learns:
- Which teams score more/fewer points on average
- Which teams allow more/fewer points (defense)
- How teams have performed recently (momentum)
- The statistical advantage of playing at home

It does NOT know about:
- Specific player injuries or availability
- Weather conditions
- Coaching changes
- Referee assignments
- Playoff implications
- Team motivation

This makes it a solid baseline predictor based purely on statistical trends!

# 2025 NFL Predictions - Quick Reference

## 🚀 First Time Setup (15 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download data for training (2022-2024 for historical baseline)
python src/update_data.py --season 2022
python src/update_data.py --season 2023
python src/update_data.py --season 2024

# 3. Download 2025 current season
python src/update_data.py --season 2025

# 4. Build historical datasets
python src/build_games_dataset.py --seasons 2022 2023 2024
python src/build_features.py

# 5. Build 2025 dataset
python src/build_games_dataset.py --season 2025
python src/build_features.py --season 2025

# 6. Train model with 2025 data
python src/train_model.py --include-current 2025

# 7. Make your first prediction!
python src/predict_game.py "KC" "BUF" --season 2025
```

## 📅 Weekly Update (5 minutes)

Run this every Monday after Sunday games to get latest results:

```bash
# Update data
python src/update_data.py --season 2025

# Rebuild datasets with new games
python src/build_games_dataset.py --season 2025
python src/build_features.py --season 2025

# Optional: Retrain (recommended every 2-3 weeks)
python src/train_model.py --include-current 2025

# Make predictions for upcoming week
python src/predict_game.py "HOME_TEAM" "AWAY_TEAM" --season 2025
```

## 🎯 Common Commands

### Predict a Game
```bash
# Basic (2025 context)
python src/predict_game.py "KC" "BUF" --season 2025

# With week display
python src/predict_game.py "SF" "SEA" --season 2025 --week 11

# Historical matchup
python src/predict_game.py "GB" "CHI"
```

### Update Data
```bash
# Latest 2025 data
python src/update_data.py --season 2025

# Specific past season
python src/update_data.py --season 2023
```

### Retrain Model
```bash
# Historical only (most stable)
python src/train_model.py

# With 2025 data (adapts to current season)
python src/train_model.py --include-current 2025
```

## 📊 Understanding Output

### High Confidence (>65%)
```
🏆 PREDICTED WINNER: KC (Home)
Win Probabilities:
  • KC (Home): 68.2%
  • BUF (Away): 31.8%
Confidence: High
```
**Strong favorite** - model is very confident

### Moderate Confidence (55-65%)
```
🏆 PREDICTED WINNER: SF (Away)
Win Probabilities:
  • SEA (Home): 42.5%
  • SF (Away): 57.5%
Confidence: Moderate
```
**Slight favorite** - reasonable prediction

### Low Confidence (<55%)
```
🏆 PREDICTED WINNER: DAL (Home)
Win Probabilities:
  • DAL (Home): 51.3%
  • PHI (Away): 48.7%
Confidence: Low (close matchup)
```
**Toss-up game** - very even matchup

## 🏈 Week 11 2025 Example Predictions

```bash
# Thursday Night
python src/predict_game.py "PIT" "CLE" --season 2025 --week 11

# Sunday Afternoon
python src/predict_game.py "KC" "BUF" --season 2025 --week 11
python src/predict_game.py "SF" "GB" --season 2025 --week 11
python src/predict_game.py "LAC" "BAL" --season 2025 --week 11

# Sunday Night
python src/predict_game.py "DAL" "WAS" --season 2025 --week 11

# Monday Night
python src/predict_game.py "HOU" "NO" --season 2025 --week 11
```

## 🔧 Troubleshooting

### "No data found for 2025"
```bash
# Download it first:
python src/update_data.py --season 2025
```

### "Model not found"
```bash
# Train the model:
python src/train_model.py
```

### "Team not found"
Check team abbreviation - use official codes:
- Seattle = "SEA" (not "Seahawks")
- Kansas City = "KC" (not "KAN")
- San Francisco = "SF" (not "SFO")

### Week 1 predictions seem off
This is normal! Week 1 uses league averages since teams have no 2025 games yet. Predictions improve each week as more data accumulates.

## 📋 Team Codes Reference

| Team | Code | Team | Code |
|------|------|------|------|
| Arizona Cardinals | ARI | Miami Dolphins | MIA |
| Atlanta Falcons | ATL | Minnesota Vikings | MIN |
| Baltimore Ravens | BAL | New England Patriots | NE |
| Buffalo Bills | BUF | New Orleans Saints | NO |
| Carolina Panthers | CAR | New York Giants | NYG |
| Chicago Bears | CHI | New York Jets | NYJ |
| Cincinnati Bengals | CIN | Las Vegas Raiders | LV |
| Cleveland Browns | CLE | Philadelphia Eagles | PHI |
| Dallas Cowboys | DAL | Pittsburgh Steelers | PIT |
| Denver Broncos | DEN | Los Angeles Chargers | LAC |
| Detroit Lions | DET | Los Angeles Rams | LA |
| Green Bay Packers | GB | San Francisco 49ers | SF |
| Houston Texans | HOU | Seattle Seahawks | SEA |
| Indianapolis Colts | IND | Tampa Bay Buccaneers | TB |
| Jacksonville Jaguars | JAX | Tennessee Titans | TEN |
| Kansas City Chiefs | KC | Washington Commanders | WAS |

## 💡 Pro Tips

1. **Update weekly**: Run the weekly update every Monday for best accuracy
2. **Retrain occasionally**: Re-train model every 2-3 weeks during season
3. **Check team stats**: Look at the team statistics in output to understand why
4. **Low confidence = close game**: Don't over-interpret predictions near 50%
5. **Context matters**: Model doesn't know injuries, weather, etc.

## 📈 Model Accuracy Expectations

- **Week 1-2**: ~55-58% (limited 2025 data)
- **Week 3-6**: ~58-62% (building 2025 profile)
- **Week 7+**: ~60-65% (established 2025 trends)
- **Overall**: Better than coin flip, competitive with experts

## 🎯 Best Use Cases

✅ **Good for:**
- Comparing team strengths statistically
- Understanding matchup dynamics
- Educational ML project
- Portfolio showcase

❌ **Not for:**
- Gambling/betting (use responsibly)
- Ignoring injuries/context
- Expecting 100% accuracy
- Week 1 predictions (limited data)

## 🚀 Next Steps

After mastering basic predictions, try:
- Tracking your prediction accuracy
- Comparing against Vegas odds
- Adding your own features
- Building a web interface
- Analyzing which features matter most

---

**Remember**: This is a statistical model based on historical performance. Real games are influenced by many factors not in the data (injuries, weather, motivation, etc.). Use predictions as one input, not the only input!

Happy predicting! 🏈

# NFL Game Outcome Predictor

A machine learning project that predicts NFL game outcomes using historical play-by-play data. This project demonstrates data processing, feature engineering, and predictive modeling using logistic regression.

**NEW: Now available as a web application!** Use the beautiful web interface or the command-line tool.

**ALSO NEW: Live 2025 season predictions!** Automatically downloads the latest NFL data and makes predictions based on games played so far.

## 📊 Project Overview

This predictor uses historical NFL game data to forecast whether the home team or away team will win a matchup. The model considers team offensive and defensive strength, recent form, and home-field advantage to make predictions with probability estimates.

**Key Features:**
- **🌐 Web Application** - Beautiful, responsive web interface
- **💻 Command-Line Tool** - Full-featured CLI for power users
- **📡 REST API** - FastAPI backend for integration
- **🔴 Live 2025 season predictions** using up-to-date data
- Automatically downloads latest NFL data via nfl_data_py
- Processes NFL play-by-play data into game-level statistics
- Engineers meaningful features while avoiding data leakage
- Trains an interpretable logistic regression model
- Provides predictions with probability scores
- Clean, documented, and reproducible code

## 🎯 Model Performance

- **Test Accuracy:** ~60-65% (typical performance)
- **Baseline Accuracy:** ~57% (always predicting home team wins)
- **Model Type:** Logistic Regression (chosen for interpretability and simplicity)

The model outperforms the baseline, demonstrating that historical team statistics provide predictive value for game outcomes.

## 📁 Project Structure

```
football-predictor/
├── data/
│   ├── raw/                          # Raw play-by-play data files
│   │   ├── play_by_play_2022.csv.gz
│   │   ├── play_by_play_2023.csv.gz
│   │   ├── play_by_play_2024.csv.gz
│   │   └── play_by_play_2025.csv.gz  # Current season (auto-downloaded)
│   └── processed/                    # Processed datasets
│       ├── games.csv                 # All historical games
│       ├── games_2025.csv            # 2025 season games
│       ├── games_with_features.csv   # Historical with features
│       └── games_with_features_2025.csv  # 2025 with features
├── models/
│   ├── logistic_regression.pkl       # Trained model
│   ├── scaler.pkl                    # Feature scaler
│   └── model_metadata.json           # Training info
├── src/
│   ├── update_data.py                # Download latest NFL data (NEW!)
│   ├── build_games_dataset.py        # Convert play-by-play to games
│   ├── build_features.py             # Feature engineering
│   ├── train_model.py                # Model training
│   └── predict_game.py               # Make predictions
├── requirements.txt
└── README.md
```

## 🗂️ Data Source

This project uses play-by-play data from **[nflverse](https://github.com/nflverse/nflverse-data)** via the **nfl_data_py** package.

**Two ways to get data:**

### Option 1: Automatic Download (Recommended for 2025)
```bash
python src/update_data.py --season 2025
```

### Option 2: Manual Download (For historical seasons)
1. Visit: https://github.com/nflverse/nflverse-data/releases
2. Download `play_by_play_[YEAR].csv.gz` files for desired seasons (e.g., 2022, 2023, 2024)
3. Place files in the `data/raw/` directory

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download this repository:**
   ```bash
   cd football-predictor
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 📝 Usage

You can use this predictor in two ways:

### 🌐 Option 1: Web Application (Recommended)

The easiest way to use the predictor:

```bash
# 1. Make sure model is trained (one-time setup)
python src/train_model.py --include-current 2025

# 2. Start the web server
uvicorn backend.app:app --reload

# 3. Open your browser to http://localhost:8000
```

**Features:**
- Beautiful, intuitive interface
- Select teams from dropdowns
- See predictions with visual stats
- Real-time updates
- No command-line knowledge needed!

**See [WEB_APP_GUIDE.md](WEB_APP_GUIDE.md) for complete web app documentation.**

---

### 💻 Option 2: Command-Line Interface

For power users and automation:

#### 🆕 Quick Start: 2025 Season Predictions

For live 2025 season predictions, follow this workflow:

```bash
# 1. Download latest 2025 data
python src/update_data.py --season 2025

# 2. Build 2025 games dataset
python src/build_games_dataset.py --season 2025

# 3. Engineer features for 2025
python src/build_features.py --season 2025

# 4. Train model (including 2025 data for best current-season accuracy)
python src/train_model.py --include-current 2025

# 5. Make predictions!
python src/predict_game.py "KC" "BUF" --season 2025
```

**Update weekly:** Simply re-run steps 1-3 weekly to get the latest game results, then make new predictions!

---

### 📚 Standard Workflow: Historical Data

### Step 0: Download Data (NEW!)

Download the latest NFL data automatically:

```bash
python src/update_data.py --season 2025
```

Or download multiple seasons:
```bash
python src/update_data.py --season 2024
python src/update_data.py --season 2023
```

### Step 1: Build the Dataset

Process raw play-by-play data into a game-level dataset:

```bash
# All available seasons:
python src/build_games_dataset.py

# Specific season only:
python src/build_games_dataset.py --season 2025

# Multiple seasons:
python src/build_games_dataset.py --seasons 2023 2024 2025
```

**Output:** `data/processed/games.csv` (one row per game with final scores)

### Step 2: Engineer Features

Create predictive features from historical game data:

```bash
# All seasons:
python src/build_features.py

# Specific season:
python src/build_features.py --season 2025
```

**Output:** `data/processed/games_with_features.csv` with features:
- Average points scored/allowed per team
- Recent form (last 5 games)
- Home-field advantage indicator

### Step 3: Train the Model

Train the logistic regression model:

```bash
# Historical data only (most stable):
python src/train_model.py

# Include current season (adapts to 2025 trends):
python src/train_model.py --include-current 2025
```

**Output:** 
- `models/logistic_regression.pkl` (trained model)
- `models/scaler.pkl` (feature scaler)
- `models/model_metadata.json` (training info)
- Training metrics and evaluation results

**Training Strategy Notes:**
- **Historical only**: Best for general predictions, most stable
- **Include current season**: Best for in-season predictions, adapts to current trends

### Step 4: Make Predictions

Predict the outcome of a game:

```bash
# Basic prediction (uses all historical data):
python src/predict_game.py "SEA" "SF"

# 2025 season prediction (uses 2025 context):
python src/predict_game.py "KC" "BUF" --season 2025

# With week context:
python src/predict_game.py "DAL" "PHI" --season 2025 --week 10
```

**Sample Output:**
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

---

## 🔄 Live Season Workflow

### How Live 2025 Predictions Work

The predictor uses **only games played so far** in the 2025 season to compute team statistics, preventing data leakage while providing up-to-date predictions.

**Weekly Update Cycle:**

```bash
# Every Monday (after Sunday games):
python src/update_data.py --season 2025           # Download latest results
python src/build_games_dataset.py --season 2025   # Process new games
python src/build_features.py --season 2025        # Update features

# Optional: Retrain with latest data
python src/train_model.py --include-current 2025

# Make predictions for upcoming games
python src/predict_game.py "KC" "LV" --season 2025
```

### Data Leakage Prevention

**Critical:** Features for each game use ONLY games played before it:
- Week 1 games use league averages (no prior 2025 data)
- Week 2 games use Week 1 results
- Week 10 games use Weeks 1-9 results
- This ensures fair, realistic predictions

### Example: Predicting Week 10 Game

```bash
python src/predict_game.py "BUF" "KC" --season 2025 --week 10
```

The model will:
1. Load all 2025 games through Week 9
2. Calculate BUF and KC statistics from Weeks 1-9 only
3. Predict Week 10 outcome using those statistics
4. Display team performance context

## 🔍 Features Explained

The model uses seven features to predict game outcomes:

1. **home_team_avg_points_for**: Average points scored by home team across all historical games
2. **home_team_avg_points_against**: Average points allowed by home team
3. **away_team_avg_points_for**: Average points scored by away team
4. **away_team_avg_points_against**: Average points allowed by away team
5. **home_recent_form**: Average points scored by home team in last 5 games
6. **away_recent_form**: Average points scored by away team in last 5 games
7. **home_field_advantage**: Binary indicator (always 1) representing home advantage

**Data Leakage Prevention:** Features are calculated using only games that occurred *before* the target game, ensuring the model doesn't "cheat" by using future information.

## 🧠 Why Logistic Regression?

Logistic regression was chosen for several reasons:

- **Interpretability**: Coefficients show which features matter most
- **Simplicity**: Easy to understand, debug, and explain
- **Speed**: Fast training and prediction
- **Probabilistic**: Provides win probabilities, not just predictions
- **Effective baseline**: Performs well for binary classification with few features
- **Industry standard**: Commonly used for sports prediction and baselines

## 📈 Model Evaluation

The model is evaluated using:
- **Accuracy**: Percentage of correct predictions
- **Precision/Recall**: Performance on home and away wins
- **Confusion Matrix**: Breakdown of correct/incorrect predictions
- **Baseline Comparison**: Performance vs. always predicting home team wins

## 🎓 Key Learnings

1. **Data quality matters**: Clean, reliable data (nflverse) is crucial
2. **Feature engineering**: Rolling averages and recent form improve predictions
3. **Avoid data leakage**: Only use information available before each game
4. **Simple models work**: Logistic regression provides good baseline performance
5. **Home-field advantage is real**: Home teams win ~57% of NFL games

## 🔮 Future Improvements

Potential enhancements to explore:

- **Additional features**: Weather, injuries, rest days, division matchups
- **Player-level data**: Quarterback rating, key player availability
- **Advanced metrics**: EPA (Expected Points Added), DVOA ratings
- **Time series models**: Account for team performance trends
- **Ensemble methods**: Combine multiple models for better accuracy
- **Live updates**: Incorporate in-season data for real-time predictions
- **Playoff predictions**: Separate model for postseason games

## 🛠️ Technologies Used

- **Python 3.8+**: Programming language
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Scikit-learn**: Machine learning (logistic regression, preprocessing, metrics)
- **Joblib**: Model serialization

## 📄 License

This project is for educational and portfolio purposes. NFL data is provided by nflverse under their respective licenses.

## 🙏 Acknowledgments

- **nflverse** for providing comprehensive NFL data
- NFL for the game data and statistics
- The open-source data science community

## 👤 Author

Built as a portfolio project to demonstrate:
- Data processing and feature engineering
- Machine learning model development
- Clean, documented, reproducible code
- Command-line tool development

---

**Note:** This model is for educational purposes only. Predictions are based on historical statistics and should not be used for gambling or betting purposes.

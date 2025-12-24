"""
NFL Game Outcome Predictor - Model Training

This script trains a logistic regression model to predict NFL game outcomes.
Logistic regression was chosen for its interpretability, simplicity, and
effectiveness for binary classification problems.

Why Logistic Regression?
- Simple and interpretable: coefficients show feature importance
- Fast to train and predict
- Performs well with limited features
- Provides probability estimates (confidence)
- Industry standard for binary classification baselines

The model predicts whether the home team wins (1) or loses (0) based on:
- Team offensive/defensive strength (average points for/against)
- Recent form (last 5 games performance)
- Home field advantage

Training Strategies:
1. Historical only (--historical): Train on past complete seasons (2022-2024)
   - Most stable, no in-season bias
   - Best for pre-season predictions
   
2. Include current season (--include-current 2025): Train on historical + current
   - Adapts to current season trends
   - Best for in-season predictions
   - May overfit if current season data is limited

Input: data/processed/games_with_features.csv
Output: models/logistic_regression.pkl, models/scaler.pkl
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
import json

def load_training_data(historical_only=False, include_current_season=None):
    """
    Load training data based on strategy.
    
    Args:
        historical_only: If True, only use complete historical seasons
        include_current_season: Season year to include (e.g., 2025)
    
    Returns:
        tuple: (games_df, seasons_used)
    """
    processed_path = Path("data/processed")
    
    # Load main historical data
    historical_file = processed_path / "games_with_features.csv"
    
    if not historical_file.exists():
        print(f"❌ Error: Historical data not found: {historical_file}")
        print("   Please run:")
        print("   1. python src/build_games_dataset.py")
        print("   2. python src/build_features.py")
        return None, None
    
    games = pd.read_csv(historical_file)
    seasons_used = sorted(games['season'].unique().tolist())
    
    # If including current season, append it
    if include_current_season and not historical_only:
        current_file = processed_path / f"games_with_features_{include_current_season}.csv"
        if current_file.exists():
            current_games = pd.read_csv(current_file)
            # Only include if not already in historical data
            if include_current_season not in seasons_used:
                games = pd.concat([games, current_games], ignore_index=True)
                seasons_used.append(include_current_season)
                seasons_used = sorted(seasons_used)
                print(f"   Added {len(current_games)} games from {include_current_season} season")
        else:
            print(f"   ⚠️  Current season file not found: {current_file}")
            print(f"   Training without {include_current_season} data")
    
    return games, seasons_used


def main():
    """Train and evaluate the logistic regression model."""
    
    parser = argparse.ArgumentParser(
        description="Train NFL game outcome prediction model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Training Strategies:

1. Historical only (default):
   python src/train_model.py
   → Trains on all complete seasons
   → Most stable, good for general predictions

2. Include current season:
   python src/train_model.py --include-current 2025
   → Trains on historical + current season so far
   → Adapts to current season trends
   → Best for in-season predictions

Examples:
  python src/train_model.py                        # Historical only
  python src/train_model.py --include-current 2025  # With 2025 data
        """
    )
    
    parser.add_argument(
        '--include-current',
        type=int,
        help='Include current season data in training (e.g., 2025)'
    )
    
    parser.add_argument(
        '--historical-only',
        action='store_true',
        help='Train only on historical complete seasons'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("  NFL Game Outcome Predictor - Model Training")
    print("="*70 + "\n")
    
    # Load training data based on strategy
    print("Loading training data...")
    games, seasons_used = load_training_data(
        historical_only=args.historical_only,
        include_current_season=args.include_current
    )
    
    if games is None:
        return
    
    print(f"✅ Loaded {len(games)} games from seasons: {seasons_used}\n")
    
    # Define features (X) and target (y)
    feature_columns = [
        "home_team_avg_points_for",       # Home team offensive strength
        "home_team_avg_points_against",   # Home team defensive strength
        "away_team_avg_points_for",       # Away team offensive strength
        "away_team_avg_points_against",   # Away team defensive strength
        "home_recent_form",               # Home team recent performance
        "away_recent_form",               # Away team recent performance
        "home_field_advantage"            # Home field advantage (always 1)
    ]
    
    X = games[feature_columns]
    y = games["home_win"]  # Target: 1 if home team wins, 0 if away team wins
    
    # Drop rows with missing values (early season games may have no history)
    print("Cleaning data...")
    original_size = len(X)
    X = X.dropna()
    y = y.loc[X.index]
    print(f"  Removed {original_size - len(X)} games with missing features")
    print(f"  Training set: {len(X)} games\n")
    
    # Split into training and test sets (80/20 split)
    # random_state=42 ensures reproducibility
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Train set: {len(X_train)} games")
    print(f"Test set:  {len(X_test)} games")
    print(f"Home win rate in training: {y_train.mean():.1%}\n")
    
    # Feature scaling: Standardize features to have mean=0 and std=1
    # This helps logistic regression converge faster and improves performance
    print("Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print("✅ Features scaled (mean=0, std=1)\n")
    
    # Train logistic regression model
    # max_iter=1000: sufficient iterations for convergence
    # random_state=42: reproducibility
    print("Training logistic regression model...")
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_scaled, y_train)
    print("✅ Model trained successfully\n")
    
    # Evaluate on training set
    y_train_pred = model.predict(X_train_scaled)
    train_accuracy = accuracy_score(y_train, y_train_pred)
    
    # Evaluate on test set (unseen data)
    y_test_pred = model.predict(X_test_scaled)
    test_accuracy = accuracy_score(y_test, y_test_pred)
    
    # Display results
    print("="*60)
    print("  MODEL EVALUATION RESULTS")
    print("="*60)
    print(f"\nTraining Accuracy: {train_accuracy:.1%}")
    print(f"Test Accuracy:     {test_accuracy:.1%}")
    
    # Baseline comparison (always predict home team wins)
    baseline_accuracy = y_test.mean()
    print(f"Baseline (always predict home win): {baseline_accuracy:.1%}")
    print(f"\nModel improvement over baseline: {(test_accuracy - baseline_accuracy):.1%}\n")
    
    # Detailed classification report
    print("-"*60)
    print("Classification Report:")
    print("-"*60)
    print(classification_report(y_test, y_test_pred, 
                               target_names=["Away Win", "Home Win"],
                               digits=3))
    
    # Confusion matrix
    print("-"*60)
    print("Confusion Matrix:")
    print("-"*60)
    cm = confusion_matrix(y_test, y_test_pred)
    print(f"                Predicted")
    print(f"              Away    Home")
    print(f"Actual Away   {cm[0,0]:4d}    {cm[0,1]:4d}")
    print(f"       Home   {cm[1,0]:4d}    {cm[1,1]:4d}")
    print()
    
    # Feature importance (coefficients)
    print("-"*60)
    print("Feature Importance (Logistic Regression Coefficients):")
    print("-"*60)
    coefficients = model.coef_[0]
    feature_importance = pd.DataFrame({
        'Feature': feature_columns,
        'Coefficient': coefficients,
        'Abs_Coefficient': np.abs(coefficients)
    }).sort_values('Abs_Coefficient', ascending=False)
    
    for _, row in feature_importance.iterrows():
        print(f"  {row['Feature']:35s} {row['Coefficient']:+.4f}")
    print()
    
    # Save the trained model, scaler, and metadata
    print("-"*70)
    print("Saving model...")
    print("-"*70)
    os.makedirs("models", exist_ok=True)
    
    model_path = "models/logistic_regression.pkl"
    scaler_path = "models/scaler.pkl"
    metadata_path = "models/model_metadata.json"
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    # Save metadata about what the model was trained on
    metadata = {
        "trained_on_seasons": seasons_used,
        "total_games": len(X),
        "train_games": len(X_train),
        "test_games": len(X_test),
        "train_accuracy": float(train_accuracy),
        "test_accuracy": float(test_accuracy),
        "features": feature_columns,
        "model_type": "LogisticRegression",
        "includes_current_season": args.include_current is not None,
        "current_season": args.include_current
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Model saved to: {model_path}")
    print(f"✅ Scaler saved to: {scaler_path}")
    print(f"✅ Metadata saved to: {metadata_path}")
    print("\n" + "="*70)
    print("  Training Complete!")
    print("="*70 + "\n")
    
    if args.include_current:
        print(f"Model trained with {args.include_current} season data")
        print(f"Use for in-season {args.include_current} predictions:")
        print(f'  python src/predict_game.py "KC" "BUF" --season {args.include_current}\n')
    else:
        print("Model trained on historical data only")
        print("Use for any season predictions:")
        print('  python src/predict_game.py "KC" "BUF" --season 2025\n')

if __name__ == "__main__":
    main()
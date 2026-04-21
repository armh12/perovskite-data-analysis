#!/bin/bash

# Configuration
TRIALS=100

echo "--- Starting Full Perovskite Model Training Pipeline ---"
echo "Target Trials: $TRIALS"

# 1. Regenerate Clean Data
echo "Step 1: Organizing and Enriching Data..."
python organize_and_enrich_data.py

# 2. Run Optuna Training
echo "Step 2: Running Optuna Study for all models (including Uncertainty Ranges)..."
# We use sed to inject the trials count dynamically
sed -i '' "s/n_trials = [0-9]*/n_trials = $TRIALS/g" train_models_optuna.py
python train_models_optuna.py

echo "--- Training Pipeline Complete ---"
echo "All models saved to ml_models/ folder."

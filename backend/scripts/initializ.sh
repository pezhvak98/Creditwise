#!/bin/bash
# ============================================
# CreditWise - Initialization Script
# Generates synthetic data and trains the model
# if they don't already exist.
# ============================================

set -e

echo "=========================================="
echo "CreditWise Initialization"
echo "=========================================="

# Check if model exists
if [ ! -f "/app/models/credit_scoring_pipeline.joblib" ]; then
    echo "[INIT] Model not found. Generating synthetic data and training model..."
    
    # Generate synthetic data if not exists
    if [ ! -f "/app/data/raw/synthetic_alternative_credit_dataset.csv" ]; then
        echo "[INIT] Generating synthetic data..."
        python /app/scripts/generate_synthetic_data.py --rows 10000 --seed 42
    fi
    
    # Train the model
    echo "[INIT] Training model..."
    python /app/scripts/train_credit_model.py --model logistic --seed 42
    
    echo "[INIT] Model training complete!"
else
    echo "[INIT] Model already exists. Skipping initialization."
fi

echo "=========================================="
echo "CreditWise initialization finished."
echo "=========================================="
#!/bin/bash

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Create models directory
mkdir -p models

# Train the model
python train_model.py

echo "Setup complete! Virtual environment is ready."
echo "To activate the virtual environment, run: source venv/bin/activate" 
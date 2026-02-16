"""
Complete ML training pipeline for EmberAlert.
Run this to train the model from scratch.
"""

import logging
from pathlib import Path
from data.training_data import TrainingDataLoader
from models.xgboost_model import FireRiskXGBoost
from evaluation.metrics import ModelEvaluator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
  """run ML training pipeline"""
  print("\n" + "="*60)
  print("EmberAlert ML Training Pipeline")
  print("="*60 + "\n")

  # STEP 1: Load data
  logger.info("Step 1: Loading training data...")
  loader = TrainingDataLoader()
  df = loader.create_synthetic_data(n_samples=5000)
  X_train, X_test, y_train, y_test = loader.prepare_data(df)

  # STEP 2: Train mode
  logger.info("\nStep 2: Training XGBoost model...")
  model = FireRiskXGBoost()
  model.train(X_train, y_train, X_test, y_test)

  # STEP 3: Evaluate
  logger.info("\nStep 3: Evaluating model...")
  y_pred = model.predict(X_test)
  metrics = ModelEvaluator.evaluate(y_test, y_pred)

  # STEP 4: Feature importance
  logger.info("\nStep 4: Feature importance:")
  importance = model.get_feature_importance()
  sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)

  for feature, score in sorted_features:
    logger.info(f"  {feature}: {score:.4f}")
  
  # STEP 5: Save model
  logger.info("\nStep 5: Saving model...")
  save_dir = Path('saved_models')
  save_dir.mkdir(exist_ok=True)
    
  model_path = save_dir / 'fire_risk_xgboost_v1.pkl'
  model.save(str(model_path))
    
  print("\n" + "="*60)
  print(f"✓ Training Complete!")
  print(f"✓ Model saved: {model_path}")
  print(f"✓ Test R²: {metrics['r2_score']:.4f}")
  print(f"✓ Test RMSE: {metrics['rmse']:.4f}")
  print("="*60 + "\n")

if __name__ == "__main__":
    main()


"""
Model evaluation metrics. Evaluate how well the model is. 
"""

import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class ModelEvaluator:
    """Calculate performance metrics"""

    @staticmethod
    def evaluate(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        """
        Comprehensive model evaluation.
        
        Metrics:
        - RMSE: Root Mean Squared Error (lower is better)
        - MAE: Mean Absolute Error (more interpretable)
        - R²: Variance explained (1.0 = perfect)
        - MAPE: Mean Absolute Percentage Error
        """

        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        # MAPE with clipping to avoid division by zero
        mape = np.mean(np.abs((y_true - y_pred) / np.clip(y_true, 0.01, None))) * 100
    
        metrics = {
            'rmse': float(rmse),
            'mae': float(mae),
            'r2_score': float(r2),
            'mape': float(mape)
          }

        logger.info("Model Performance:")
        logger.info(f"  RMSE: {rmse:.4f}")
        logger.info(f"  MAE: {mae:.4f}")
        logger.info(f"  R²: {r2:.4f}")
        logger.info(f"  MAPE: {mape:.2f}%")
        
        return metrics
        

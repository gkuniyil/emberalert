"""XGBoost model for fire risk prediction"""

import xgboost as xgb 
import numpy as np 
from typing import Dict 
import joblib 
import logging 

logger = logging.getLogger(__name__)

class FireRiskXGBoost:
  """xgboost regressor for fire risk score"""

  def __init__(self, params: Dict = None):
    """
     Initialize XGBoost model.
        
        Key hyperparameters:
        - max_depth: Tree depth (prevents overfitting)
        - learning_rate: Step size (smaller = more cautious)
        - n_estimators: Number of trees
        - subsample: Row sampling ratio
        - colsample_bytree: Column sampling ratio
    """

    default_params = {
            'objective': 'reg:squarederror',
            'max_depth': 6,
            'learning_rate': 0.1, # Step size for corrections
            'n_estimators': 100, #number of trees to build 
            'subsample': 0.8, #use 80% of rows per tree to prevent overfitting
            'colsample_bytree': 0.8, # Use 80% of features per tree & also prevents overfitting
            'random_state': 42
        }

    #an override default by passing in thier own params 
    if params:
       default_params.update(params)
        
    self.params = default_params #store params in object 
    self.model = xgb.XGBRegressor(**self.params) #create model with parameters 
    self.feature_names = None #store column names later for feature importance 
  

  def train(self, X_train, y_train, X_val=None, y_val=None):
    """Train the model"""
    logger.info("Training XGBoost model")

    if hasattr(X_train, 'columns'):
      #save feature names for importance 
      self.feature_names = X_train.columns.tolist()

      eval_set = [(X_train, y_train)]
      # Track validation error during training
      # If validation error stops improving → model starting to overfit
      if X_val is not None and y_val is not None:
        eval_set.append((X_val, y_val))

      #model studies examples based on training info 
      self.model.fit(
            X_train, y_train,
            eval_set=eval_set,
            verbose=False
      )
      
      logger.info("Training completed")
      return self.model
    
  def predict(self, X) -> np.ndarray:
    # make predictions 
    #X is run through all the trees 
    predictions = self.model.predict(X)

    #make predictions into valid range between 0 and 1 
    return np.clip(predictions, 0, 1)

  def get_feature_importance(self) -> Dict[str, float]:
    """Get feature importance scores"""
    # XGBoost counts how many times each feature was used to split trees
    # Higher = more important for predictions (model discovered this)
    importances = self.model.feature_importances_

  
    if self.feature_names:
      return dict(zip(self.feature_names, importances))
      # Return with column names: {'temp': 0.34, 'humidity': 0.29, ...}
    else:
      return dict(enumerate(importances))
  
  def save(self, filepath: str):
        """Save model to disk and joblib saves python object to a file"""
        joblib.dump({
            'model': self.model,
            'params': self.params,
            'feature_names': self.feature_names
        }, filepath)
        # Save everything needed to recreate this exact model, so no need to retrain every time 
        
        logger.info(f"Model saved to {filepath}")
  
  @classmethod
  def load(cls, filepath: str):
    """load model from disk"""
    #load dictionary into model 
    data = joblib.load(filepath)

    # create new fireriskxgboost instance with original params 
    instance = cls(params=data['params'])

    #restore trained model 
    instance.model = data['model']

    # Restore feature names
    instance.feature_names = data['feature_names']

    logger.info(f"Model loaded from {filepath}")
    return instance





  



      
    
    
  





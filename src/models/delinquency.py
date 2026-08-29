import logging
from sklearn.ensemble import HistGradientBoostingClassifier
from src.models.base import BaseModel

logger = logging.getLogger(__name__)

class DelinquencyModel(BaseModel):
    """Predicts future loan delinquency (next 3 months or next 6 months)."""
    
    def __init__(self, model_name: str = "DelinquencyModel", horizon_months: int = 3, model_version: str = "1.0"):
        super().__init__(model_name=f"{model_name}_{horizon_months}m", model_version=model_version)
        self.horizon_months = horizon_months
        
    def fit(self, X, y):
        logger.info(f"Training delinquency model for horizon={self.horizon_months}m on {X.shape[0]} records...")
        
        # HistGradientBoostingClassifier handles missing values and categorical data natively
        self.model = HistGradientBoostingClassifier(
            max_iter=100,
            learning_rate=0.08,
            max_depth=5,
            class_weight="balanced",
            random_state=42
        )
        self.model.fit(X, y)
        logger.info("Delinquency model training completed.")
        return self

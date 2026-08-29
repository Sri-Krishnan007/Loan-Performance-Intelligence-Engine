import logging
from sklearn.ensemble import HistGradientBoostingClassifier
from src.models.base import BaseModel

logger = logging.getLogger(__name__)

class PrepaymentModel(BaseModel):
    """Predicts future loan prepayment (early payoff) events in the next 12 months."""
    
    def __init__(self, model_name: str = "PrepaymentModel", model_version: str = "1.0"):
        super().__init__(model_name=model_name, model_version=model_version)
        
    def fit(self, X, y):
        logger.info(f"Training prepayment model (12m horizon) on {X.shape[0]} records...")
        
        self.model = HistGradientBoostingClassifier(
            max_iter=100,
            learning_rate=0.08,
            max_depth=5,
            class_weight="balanced",
            random_state=42
        )
        self.model.fit(X, y)
        logger.info("Prepayment model training completed.")
        return self

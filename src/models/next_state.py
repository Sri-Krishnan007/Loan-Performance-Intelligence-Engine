import logging
from sklearn.ensemble import HistGradientBoostingClassifier
from src.models.base import BaseModel

logger = logging.getLogger(__name__)

class NextStateModel(BaseModel):
    """Predicts the specific loan credit state (Current, Delinquent, Default, Prepaid) in month t+1."""
    
    def __init__(self, model_name: str = "NextStateModel", model_version: str = "1.0"):
        super().__init__(model_name=model_name, model_version=model_version)
        
    def fit(self, X, y):
        logger.info(f"Training next state transition multiclass model on {X.shape[0]} records...")
        
        self.model = HistGradientBoostingClassifier(
            max_iter=100,
            learning_rate=0.08,
            max_depth=5,
            class_weight="balanced",
            random_state=42
        )
        self.model.fit(X, y)
        logger.info("Next state model training completed.")
        return self

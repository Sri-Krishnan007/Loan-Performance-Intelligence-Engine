import joblib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class BaseModel:
    """Standard base interface wrapper for all portfolio credit risk models."""
    
    def __init__(self, model_name: str, model_version: str = "1.0"):
        self.model_name = model_name
        self.model_version = model_version
        self.model = None

    def fit(self, X, y):
        """Fits model parameters."""
        raise NotImplementedError("Subclasses must implement fit()")

    def predict(self, X):
        """Predicts binary or multiclass states."""
        if self.model is None:
            raise ValueError("Model has not been trained yet.")
        return self.model.predict(X)

    def predict_proba(self, X):
        """Predicts numeric probabilities."""
        if self.model is None:
            raise ValueError("Model has not been trained yet.")
        return self.model.predict_proba(X)

    def save(self, path: Path) -> None:
        """Saves model joblib binary."""
        logger.info(f"Saving model '{self.model_name}' (v{self.model_version}) to {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "model_name": self.model_name,
            "model_version": self.model_version
        }, path)

    def load(self, path: Path):
        """Loads model joblib binary."""
        logger.info(f"Loading model from {path}")
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        data = joblib.load(path)
        self.model = data["model"]
        self.model_name = data.get("model_name", self.model_name)
        self.model_version = data.get("model_version", self.model_version)
        return self

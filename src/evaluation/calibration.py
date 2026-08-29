import logging
from sklearn.calibration import CalibratedClassifierCV

logger = logging.getLogger(__name__)

class ProbabilityCalibrator:
    """Calibrates classifier output probabilities using Platt scaling or Isotonic regression."""
    
    def __init__(self, method: str = "isotonic"):
        """
        Args:
            method: 'sigmoid' (Platt scaling) or 'isotonic' (Isotonic regression).
        """
        self.method = method
        self.calibrator = None

    def fit_calibration(self, fitted_model, X_val, y_val):
        """Fits calibration on validation features and labels using a pre-fitted model."""
        logger.info(f"Fitting probability calibration using {self.method} method...")
        from sklearn.calibration import FrozenEstimator
        self.calibrator = CalibratedClassifierCV(estimator=FrozenEstimator(fitted_model), method=self.method)
        self.calibrator.fit(X_val, y_val)
        logger.info("Probability calibration completed.")
        return self.calibrator

    def predict_calibrated_proba(self, X) -> float:
        """Predicts calibrated probabilities."""
        if self.calibrator is None:
            raise ValueError("Calibrator has not been fitted yet.")
        # Returns probability of class 1
        return self.calibrator.predict_proba(X)[:, 1]

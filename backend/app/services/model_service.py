import json
from pathlib import Path
from src.config import settings

class ModelService:
    @staticmethod
    def get_artifacts_status() -> dict:
        """Checks availability of core serialized model files."""
        model_files = {
            "delinquency_3m": settings.MODEL_DIR / "trained/delinquency_3m_model.joblib",
            "delinquency_6m": settings.MODEL_DIR / "trained/delinquency_6m_model.joblib",
            "default_12m": settings.MODEL_DIR / "trained/default_model.joblib",
            "prepayment_12m": settings.MODEL_DIR / "trained/prepayment_model.joblib",
            "next_state": settings.MODEL_DIR / "trained/next_state_model.joblib",
            "anomaly_detector": settings.MODEL_DIR / "trained/anomaly_model.joblib"
        }
        return {name: path.exists() for name, path in model_files.items()}

    @staticmethod
    def get_model_health() -> dict:
        """Retrieves trained model metrics and OOT validation configs."""
        metrics_path = settings.MODEL_DIR / "metrics/model_performance.json"
        
        models = []
        if metrics_path.exists():
            with open(metrics_path, "r", encoding="utf-8") as f:
                perf = json.load(f)
                
                # delinquency_3m
                del3 = perf.get("delinquency_3m", {}).get("improved_calibrated", {})
                models.append({
                    "name": "delinquency_3m",
                    "version": "v1.0",
                    "roc_auc": float(del3.get("roc_auc", 0.0)),
                    "pr_auc": float(del3.get("pr_auc", 0.0)),
                    "f1": float(del3.get("f1_score", 0.0)),
                    "brier_score": float(del3.get("brier_score", 0.0)),
                    "calibrated": True
                })
                
                # delinquency_6m
                del6 = perf.get("delinquency_6m", {}).get("improved_calibrated", {})
                models.append({
                    "name": "delinquency_6m",
                    "version": "v1.0",
                    "roc_auc": float(del6.get("roc_auc", 0.0)),
                    "pr_auc": float(del6.get("pr_auc", 0.0)),
                    "f1": float(del6.get("f1_score", 0.0)),
                    "brier_score": float(del6.get("brier_score", 0.0)),
                    "calibrated": True
                })
                
                # default_12m
                df12 = perf.get("default_12m", {}).get("improved_calibrated", {})
                models.append({
                    "name": "default_12m",
                    "version": "v1.0",
                    "roc_auc": float(df12.get("roc_auc", 0.0)),
                    "pr_auc": float(df12.get("pr_auc", 0.0)),
                    "f1": float(df12.get("f1_score", 0.0)),
                    "brier_score": float(df12.get("brier_score", 0.0)),
                    "calibrated": True
                })
                
                # prepayment_12m
                pr12 = perf.get("prepayment_12m", {}).get("improved_calibrated", {})
                models.append({
                    "name": "prepayment_12m",
                    "version": "v1.0",
                    "roc_auc": float(pr12.get("roc_auc", 0.0)),
                    "pr_auc": float(pr12.get("pr_auc", 0.0)),
                    "f1": float(pr12.get("f1_score", 0.0)),
                    "brier_score": float(pr12.get("brier_score", 0.0)),
                    "calibrated": True
                })
                
                # next_state
                ns = perf.get("next_state", {}).get("improved", {})
                models.append({
                    "name": "next_state",
                    "version": "v1.0",
                    "roc_auc": 0.0,
                    "pr_auc": 0.0,
                    "f1": float(ns.get("macro_f1", 0.0)),
                    "brier_score": 0.0,
                    "calibrated": False
                })
        
        artifacts = ModelService.get_artifacts_status()
        for m in models:
            m["artifact_available"] = artifacts.get(m["name"], False)
            
        return {
            "models": models,
            "validation": {
                "method": "time-aware-split",
                "train_period": "2018-01-01 to 2024-12-01",
                "validation_period": "2025-01-01 to 2026-07-01"
            }
        }

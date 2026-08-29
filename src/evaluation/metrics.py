import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score, precision_recall_curve, auc, f1_score, 
    brier_score_loss, confusion_matrix, classification_report
)

class EvaluationMetrics:
    """Calculates credit risk performance metrics, classification, and calibration checks."""
    
    @staticmethod
    def calculate_binary_metrics(y_true: pd.Series, y_prob: np.ndarray, threshold: float = 0.5) -> dict:
        """Computes comprehensive binary classification and calibration metrics."""
        # Clean inputs
        y_true = np.array(y_true, dtype=int)
        y_prob = np.array(y_prob, dtype=float)
        
        # Binary prediction based on threshold
        y_pred = (y_prob >= threshold).astype(int)
        
        # ROC and PR AUC
        roc_auc = roc_auc_score(y_true, y_prob) if len(np.unique(y_true)) > 1 else 0.5
        precision, recall, _ = precision_recall_curve(y_true, y_prob)
        pr_auc = auc(recall, precision)
        
        # Brier Score (lower is better, represents probability calibration quality)
        brier = brier_score_loss(y_true, y_prob)
        
        # Standard metrics
        f1 = f1_score(y_true, y_pred, zero_division=0)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        
        precision_val = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall_val = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        
        # Recall at fixed precision (e.g., at 90% precision)
        recall_at_90_prec = 0.0
        for p, r in zip(precision, recall):
            if p >= 0.90:
                recall_at_90_prec = max(recall_at_90_prec, r)
                
        return {
            "roc_auc": float(roc_auc),
            "pr_auc": float(pr_auc),
            "brier_score": float(brier),
            "f1_score": float(f1),
            "precision": float(precision_val),
            "recall": float(recall_val),
            "recall_at_90_precision": float(recall_at_90_prec),
            "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}
        }

    @staticmethod
    def calculate_multiclass_metrics(y_true: pd.Series, y_pred: pd.Series) -> dict:
        """Computes macro-F1 and confusion matrix for multiclass next-state predictions."""
        y_true = np.array(y_true, dtype=str)
        y_pred = np.array(y_pred, dtype=str)
        
        macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
        report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
        
        unique_labels = sorted(list(set(y_true).union(set(y_pred))))
        cm = confusion_matrix(y_true, y_pred, labels=unique_labels)
        
        cm_dict = {}
        for i, label_from in enumerate(unique_labels):
            cm_dict[label_from] = {}
            for j, label_to in enumerate(unique_labels):
                cm_dict[label_from][label_to] = int(cm[i, j])
                
        return {
            "macro_f1": float(macro_f1),
            "confusion_matrix": cm_dict,
            "classification_report": report
        }

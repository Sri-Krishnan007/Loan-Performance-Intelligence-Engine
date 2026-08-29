import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score, precision_recall_curve, auc, f1_score, 
    brier_score_loss, confusion_matrix, classification_report
)

class EvaluationMetrics:
    """Calculates credit risk performance metrics, classification, and calibration checks."""
    
    @staticmethod
    def calculate_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
        """Computes Expected Calibration Error (ECE)."""
        y_true = np.array(y_true, dtype=int)
        y_prob = np.array(y_prob, dtype=float)
        
        bin_edges = np.linspace(0, 1, n_bins + 1)
        ece = 0.0
        n_samples = len(y_true)
        
        for i in range(n_bins):
            bin_lower = bin_edges[i]
            bin_upper = bin_edges[i+1]
            
            # Catch samples in current bin
            in_bin = (y_prob >= bin_lower) & (y_prob < bin_upper)
            if i == n_bins - 1:
                # Include upper boundary in the last bin
                in_bin = in_bin | (y_prob == bin_upper)
                
            bin_size = np.sum(in_bin)
            if bin_size > 0:
                accuracy_in_bin = np.mean(y_true[in_bin])
                avg_confidence_in_bin = np.mean(y_prob[in_bin])
                ece += (bin_size / n_samples) * np.abs(avg_confidence_in_bin - accuracy_in_bin)
                
        return float(ece)

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
        
        # ECE
        ece = EvaluationMetrics.calculate_ece(y_true, y_prob)
        
        # Standard metrics
        f1 = f1_score(y_true, y_pred, zero_division=0)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        
        precision_val = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall_val = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        
        # Recall at fixed precisions
        recall_at_10_prec = 0.0
        recall_at_20_prec = 0.0
        recall_at_50_prec = 0.0
        recall_at_90_prec = 0.0
        for p, r in zip(precision, recall):
            if p >= 0.10:
                recall_at_10_prec = max(recall_at_10_prec, r)
            if p >= 0.20:
                recall_at_20_prec = max(recall_at_20_prec, r)
            if p >= 0.50:
                recall_at_50_prec = max(recall_at_50_prec, r)
            if p >= 0.90:
                recall_at_90_prec = max(recall_at_90_prec, r)
                
        return {
            "roc_auc": float(roc_auc),
            "pr_auc": float(pr_auc),
            "brier_score": float(brier),
            "ece": float(ece),
            "f1_score": float(f1),
            "precision": float(precision_val),
            "recall": float(recall_val),
            "recall_at_10_precision": float(recall_at_10_prec),
            "recall_at_20_precision": float(recall_at_20_prec),
            "recall_at_50_precision": float(recall_at_50_prec),
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

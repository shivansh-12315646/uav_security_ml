"""
Training service for supervised learning with progress tracking.
Supports multiple ML algorithms.
"""
import os
import time
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from django.utils import timezone
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score
)
from xgboost import XGBClassifier
import logging

logger = logging.getLogger(__name__)


class TrainingService:
    """Service for training ML models with progress logging."""

    SUPPORTED_ALGORITHMS = {
        'RandomForest': RandomForestClassifier,
        'XGBoost': XGBClassifier,
        'SVM': SVC,
        'NeuralNetwork': MLPClassifier,
        'GradientBoosting': GradientBoostingClassifier
    }

    def __init__(self):
        """Initialize training service."""
        self.training_in_progress = False
        self.current_training_id = None

    def _emit_progress(self, event_type, data):
        """Log training progress."""
        logger.info(f"[{event_type}] {data}")

    def preprocess_dataset(self, file_path):
        """
        Preprocess uploaded dataset.

        Args:
            file_path: Path to CSV file

        Returns:
            dict: Preprocessed data info
        """
        try:
            df = pd.read_csv(file_path)

            # Auto-detect feature columns (support both UAV and legacy schemas)
            uav_cols = ['altitude', 'speed', 'direction', 'signal_strength',
                        'distance_from_base', 'flight_time', 'battery_level',
                        'temperature', 'vibration', 'gps_accuracy']
            legacy_cols = ['packet_size', 'inter_arrival_time', 'packet_rate',
                          'connection_duration', 'failed_logins']

            if all(c in df.columns for c in uav_cols):
                feature_cols = uav_cols
            elif all(c in df.columns for c in legacy_cols):
                feature_cols = legacy_cols
            else:
                return {
                    'success': False,
                    'error': f'Dataset must contain UAV features {uav_cols} or legacy features {legacy_cols}'
                }

            # Detect label column
            label_col = None
            for lc in ['threat_type', 'label', 'is_threat']:
                if lc in df.columns:
                    label_col = lc
                    break

            label_counts = {}
            if label_col:
                label_counts = df[label_col].value_counts().to_dict()

            stats = {
                'success': True,
                'total_samples': len(df),
                'features': len(feature_cols),
                'feature_columns': feature_cols,
                'label_column': label_col,
                'label_distribution': {str(k): int(v) for k, v in label_counts.items()},
                'feature_stats': df[feature_cols].describe().to_dict(),
                'null_values': df.isnull().sum().to_dict()
            }

            return stats

        except Exception as e:
            logger.error(f"Error preprocessing dataset: {e}")
            return {'success': False, 'error': str(e)}

    def train_model(self, algorithm, dataset_path, hyperparameters=None,
                    test_size=0.2, user_id=None):
        """
        Train ML model with progress logging.

        Args:
            algorithm: Algorithm name (RandomForest, XGBoost, etc.)
            dataset_path: Path to training dataset CSV
            hyperparameters: Dict of hyperparameters
            test_size: Test split ratio
            user_id: ID of user initiating training

        Returns:
            dict: Training results
        """
        if self.training_in_progress:
            return {'success': False, 'error': 'Another training is already in progress'}

        self.training_in_progress = True
        training_id = f"train_{int(time.time())}"
        self.current_training_id = training_id

        try:
            self._emit_progress('training_started', {
                'training_id': training_id,
                'algorithm': algorithm,
                'timestamp': timezone.now().isoformat()
            })

            self._emit_progress('training_update', {'stage': 'loading', 'progress': 10, 'message': 'Loading dataset...'})
            df = pd.read_csv(dataset_path)

            self._emit_progress('training_update', {'stage': 'preprocessing', 'progress': 20, 'message': 'Preprocessing features...'})

            # Auto-detect feature columns
            uav_cols = ['altitude', 'speed', 'direction', 'signal_strength',
                        'distance_from_base', 'flight_time', 'battery_level',
                        'temperature', 'vibration', 'gps_accuracy']
            legacy_cols = ['packet_size', 'inter_arrival_time', 'packet_rate',
                          'connection_duration', 'failed_logins']

            if all(c in df.columns for c in uav_cols):
                feature_columns = uav_cols
            elif all(c in df.columns for c in legacy_cols):
                feature_columns = legacy_cols
            else:
                raise ValueError('Dataset does not contain recognized feature columns')

            X = df[feature_columns]

            # Auto-detect and encode labels
            if 'threat_type' in df.columns:
                from sklearn.preprocessing import LabelEncoder
                le = LabelEncoder()
                y = pd.Series(le.fit_transform(df['threat_type']))
            elif 'label' in df.columns:
                y = df['label'].map({'normal': 0, 'attack': 1})
            elif 'is_threat' in df.columns:
                y = df['is_threat']
            else:
                raise ValueError('Dataset must contain a label column (threat_type, label, or is_threat)')

            self._emit_progress('training_update', {
                'stage': 'splitting', 'progress': 30,
                'message': f'Splitting data ({int((1-test_size)*100)}% train, {int(test_size*100)}% test)...'
            })
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )

            self._emit_progress('training_update', {'stage': 'scaling', 'progress': 40, 'message': 'Scaling features...'})
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            self._emit_progress('training_update', {'stage': 'initializing', 'progress': 50, 'message': f'Initializing {algorithm} model...'})
            model = self._create_model(algorithm, hyperparameters)

            self._emit_progress('training_update', {'stage': 'training', 'progress': 60, 'message': f'Training {algorithm} model...'})
            start_time = time.time()
            model.fit(X_train_scaled, y_train)
            training_duration = time.time() - start_time

            self._emit_progress('training_update', {'stage': 'evaluating', 'progress': 80, 'message': 'Evaluating model performance...'})
            y_pred = model.predict(X_test_scaled)

            accuracy = accuracy_score(y_test, y_pred) * 100
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)

            if hasattr(model, 'predict_proba'):
                y_proba = model.predict_proba(X_test_scaled)[:, 1]
                roc_auc = roc_auc_score(y_test, y_proba)
            else:
                roc_auc = None

            cm = confusion_matrix(y_test, y_pred)

            self._emit_progress('training_update', {'stage': 'saving', 'progress': 90, 'message': 'Saving model...'})

            models_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'ml_models', 'saved_models'
            )
            os.makedirs(models_dir, exist_ok=True)

            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            model_filename = f"{algorithm}_{timestamp}.pkl"
            model_path = os.path.join(models_dir, model_filename)
            scaler_filename = f"scaler_{algorithm}_{timestamp}.pkl"
            scaler_path = os.path.join(models_dir, scaler_filename)

            joblib.dump(model, model_path)
            joblib.dump(scaler, scaler_path)

            result = {
                'success': True,
                'training_id': training_id,
                'algorithm': algorithm,
                'metrics': {
                    'accuracy': float(accuracy),
                    'precision': float(precision),
                    'recall': float(recall),
                    'f1_score': float(f1),
                    'roc_auc': float(roc_auc) if roc_auc else None
                },
                'confusion_matrix': cm.tolist(),
                'training_duration': training_duration,
                'model_path': model_path,
                'scaler_path': scaler_path,
                'dataset_size': {
                    'train': len(X_train),
                    'test': len(X_test),
                    'total': len(df)
                }
            }

            self._emit_progress('training_complete', {**result, 'progress': 100, 'message': 'Training completed successfully!'})
            return result

        except Exception as e:
            logger.error(f"Training error: {e}")
            self._emit_progress('training_error', {'training_id': training_id, 'error': str(e)})
            return {'success': False, 'error': str(e)}
        finally:
            self.training_in_progress = False
            self.current_training_id = None

    def _create_model(self, algorithm, hyperparameters=None):
        """Create model instance with hyperparameters."""
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        model_class = self.SUPPORTED_ALGORITHMS[algorithm]
        default_params = self._get_default_params(algorithm)

        if hyperparameters:
            default_params.update(hyperparameters)

        return model_class(**default_params)

    def _get_default_params(self, algorithm):
        """Get default hyperparameters for each algorithm."""
        defaults = {
            'RandomForest': {'n_estimators': 100, 'random_state': 42, 'n_jobs': -1},
            'XGBoost': {
                'n_estimators': 100, 'random_state': 42, 'n_jobs': -1,
                'eval_metric': 'logloss'
            },
            'SVM': {'kernel': 'rbf', 'probability': True, 'random_state': 42},
            'NeuralNetwork': {'hidden_layer_sizes': (100, 50), 'random_state': 42, 'max_iter': 500},
            'GradientBoosting': {'n_estimators': 100, 'random_state': 42}
        }
        return defaults.get(algorithm, {})

    def compare_models(self, model_ids):
        """
        Compare multiple trained models.

        Args:
            model_ids: List of model IDs to compare

        Returns:
            dict: Comparison results
        """
        from core.models import MLModel

        models = MLModel.objects.filter(id__in=model_ids)

        comparison = {
            'models': [],
            'best_accuracy': None,
            'best_f1': None,
            'best_precision': None,
            'best_recall': None
        }

        best_acc = best_f1 = best_prec = best_rec = 0

        for model in models:
            model_dict = model.to_dict()
            comparison['models'].append(model_dict)

            if model.accuracy and model.accuracy > best_acc:
                best_acc = model.accuracy
                comparison['best_accuracy'] = model.name

            if model.f1_score and model.f1_score > best_f1:
                best_f1 = model.f1_score
                comparison['best_f1'] = model.name

            if model.precision and model.precision > best_prec:
                best_prec = model.precision
                comparison['best_precision'] = model.name

            if model.recall and model.recall > best_rec:
                best_rec = model.recall
                comparison['best_recall'] = model.name

        return comparison


# Global training service instance
training_service = TrainingService()

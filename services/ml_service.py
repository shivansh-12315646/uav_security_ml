"""
Machine Learning service for UAV threat detection.
Handles model loading, prediction, and model management.
"""
import os
import joblib
import numpy as np
import logging

logger = logging.getLogger(__name__)


class MLService:
    """Service for ML operations."""

    def __init__(self):
        """Initialize ML service."""
        self.models = {}
        self.scaler = None
        self.label_encoder = None
        self.active_model_name = None

    def load_models(self):
        """Load all available models and scaler."""
        try:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            # Try loading scaler
            scaler_paths = [
                os.path.join(base_path, 'ml_models', 'scaler.pkl'),
                os.path.join(base_path, 'scaler.pkl')
            ]
            for scaler_path in scaler_paths:
                if os.path.exists(scaler_path):
                    self.scaler = joblib.load(scaler_path)
                    logger.info(f"Scaler loaded from {scaler_path}")
                    break

            # Try loading label encoder
            encoder_paths = [
                os.path.join(base_path, 'ml_models', 'label_encoder.pkl'),
                os.path.join(base_path, 'label_encoder.pkl')
            ]
            for encoder_path in encoder_paths:
                if os.path.exists(encoder_path):
                    self.label_encoder = joblib.load(encoder_path)
                    logger.info(f"Label encoder loaded from {encoder_path}")
                    break

            # Load models from ml_models directory
            models_dir = os.path.join(base_path, 'ml_models')
            if os.path.exists(models_dir):
                model_files = {
                    'RandomForest': 'random_forest.pkl',
                    'SVM': 'svm.pkl',
                    'GradientBoosting': 'gradient_boosting.pkl',
                    'XGBoost': 'xgboost.pkl'
                }
                for model_name, filename in model_files.items():
                    model_path = os.path.join(models_dir, filename)
                    if os.path.exists(model_path):
                        try:
                            self.models[model_name] = joblib.load(model_path)
                            logger.info(f"Model {model_name} loaded from {model_path}")
                        except Exception as e:
                            logger.error(f"Error loading model {model_name}: {e}")

            # Fallback: Load from old location
            old_model_path = os.path.join(base_path, 'model', 'uav_security_model.pkl')
            if os.path.exists(old_model_path) and 'RandomForest' not in self.models:
                try:
                    self.models['RandomForest'] = joblib.load(old_model_path)
                    logger.info(f"Legacy model loaded from {old_model_path}")
                except Exception as e:
                    logger.error(f"Error loading legacy model: {e}")

            # Set active model
            if not self.active_model_name and self.models:
                if 'RandomForest' in self.models:
                    self.active_model_name = 'RandomForest'
                else:
                    self.active_model_name = list(self.models.keys())[0]
                logger.info(f"Active model set to: {self.active_model_name}")

            logger.info(f"Loaded {len(self.models)} models: {list(self.models.keys())}")

        except Exception as e:
            logger.error(f"Error loading models: {e}")

    def predict(self, features, model_name=None):
        """
        Make prediction using specified model or active model.

        Args:
            features: List of feature values
            model_name: Optional model name to use

        Returns:
            dict: Prediction result with confidence
        """
        if model_name is None:
            model_name = self.active_model_name

        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found")

        model = self.models[model_name]

        features_array = np.array(features).reshape(1, -1)
        if self.scaler:
            features_scaled = self.scaler.transform(features_array)
        else:
            features_scaled = features_array

        prediction = model.predict(features_scaled)[0]

        confidence = 0.5
        probabilities_dict = {}
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(features_scaled)[0]
            confidence = float(max(probabilities))
            if self.label_encoder is not None:
                class_names = list(self.label_encoder.classes_)
            else:
                class_names = [str(i) for i in range(len(probabilities))]
            probabilities_dict = {
                name: float(prob) for name, prob in zip(class_names, probabilities)
            }
        elif hasattr(model, 'decision_function'):
            decision = model.decision_function(features_scaled)[0]
            confidence = float(1 / (1 + np.exp(-decision)))

        if self.label_encoder is not None:
            prediction_label = self.label_encoder.inverse_transform([prediction])[0]
        else:
            class_names_fallback = [
                'normal', 'jamming_attack', 'gps_spoofing',
                'unauthorized_access', 'signal_interference', 'physical_tampering'
            ]
            prediction_label = (class_names_fallback[prediction]
                                if prediction < len(class_names_fallback) else 'unknown')

        display_label = self._normalise_label(prediction_label)
        threat_category = 'normal' if display_label == 'Normal' else 'attack'

        return {
            'prediction': display_label,
            'threat_category': threat_category,
            'confidence': confidence,
            'model_used': model_name,
            'raw_prediction': int(prediction),
            'all_probabilities': probabilities_dict
        }

    def _normalise_label(self, raw_label):
        """Convert raw dataset label to display-friendly name."""
        label_map = {
            'normal': 'Normal',
            'jamming_attack': 'Jamming Attack',
            'gps_spoofing': 'GPS Spoofing',
            'unauthorized_access': 'Unauthorized Access',
            'signal_interference': 'Signal Interference',
            'physical_tampering': 'Physical Tampering',
        }
        return label_map.get(str(raw_label).lower(), str(raw_label).replace('_', ' ').title())

    def get_feature_importance(self, model_name=None):
        """Get feature importance for tree-based models."""
        if model_name is None:
            model_name = self.active_model_name

        if model_name not in self.models:
            return {}

        model = self.models[model_name]

        if hasattr(model, 'feature_importances_'):
            feature_names = [
                'Altitude', 'Speed', 'Direction', 'Signal Strength',
                'Distance from Base', 'Flight Time', 'Battery Level',
                'Temperature', 'Vibration', 'GPS Accuracy'
            ]
            importances = model.feature_importances_
            return dict(zip(feature_names, [float(imp) for imp in importances]))

        return {}

    def get_available_models(self):
        """Get list of available model names."""
        return list(self.models.keys())

    def set_active_model(self, model_name):
        """Set active model for predictions."""
        if model_name in self.models:
            self.active_model_name = model_name
            return True
        return False

    def calculate_threat_level(self, prediction, confidence):
        """Calculate threat level based on prediction and confidence."""
        lookup_key = str(prediction).lower().replace(' ', '_')

        base_level_map = {
            'normal': 'Low',
            'signal_interference': 'Medium',
            'jamming_attack': 'High',
            'gps_spoofing': 'Critical',
            'unauthorized_access': 'Critical',
            'physical_tampering': 'Critical',
        }

        base = base_level_map.get(lookup_key)
        if base is None:
            base = 'High'

        if base == 'Low':
            return 'Low'
        if base == 'Critical':
            return 'Critical'
        if base == 'High':
            return 'Critical' if confidence >= 0.9 else 'High'
        return 'High' if confidence >= 0.8 else 'Medium'


# Global ML service instance
ml_service = MLService()

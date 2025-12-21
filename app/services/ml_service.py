"""
Machine Learning service for UAV threat detection.
Handles model loading, prediction, and model management.
"""
import os
import joblib
import numpy as np
import logging

# Set up logging
logger = logging.getLogger(__name__)


class MLService:
    """Service for ML operations."""
    
    def __init__(self):
        """Initialize ML service."""
        self.models = {}
        self.scaler = None
        self.active_model_name = None
        self._app = None
    
    def init_app(self, app):
        """Initialize with Flask app context."""
        self._app = app
        with app.app_context():
            self.load_models()
    
    def load_models(self):
        """Load all available models and scaler."""
        try:
            # Determine base path
            if self._app:
                base_path = os.path.dirname(self._app.root_path)
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # Try loading scaler from new location first
            scaler_paths = [
                os.path.join(base_path, 'ml_models', 'scaler.pkl'),
                os.path.join(base_path, 'scaler.pkl')
            ]
            
            for scaler_path in scaler_paths:
                if os.path.exists(scaler_path):
                    self.scaler = joblib.load(scaler_path)
                    logger.info(f"Scaler loaded from {scaler_path}")
                    break
            
            # Load models from new ml_models directory
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
                # Prefer RandomForest as default
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
            features: List of feature values [packet_size, inter_arrival, packet_rate, duration, failed_logins]
            model_name: Optional model name to use
        
        Returns:
            dict: Prediction result with confidence
        """
        if model_name is None:
            model_name = self.active_model_name
        
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found")
        
        model = self.models[model_name]
        
        # Scale features
        features_array = np.array(features).reshape(1, -1)
        if self.scaler:
            features_scaled = self.scaler.transform(features_array)
        else:
            features_scaled = features_array
        
        # Make prediction
        prediction = model.predict(features_scaled)[0]
        
        # Get probability/confidence if available
        confidence = 0.5  # Default confidence
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(features_scaled)[0]
            confidence = float(max(probabilities))
        elif hasattr(model, 'decision_function'):
            decision = model.decision_function(features_scaled)[0]
            # Convert decision function to probability-like score
            confidence = float(1 / (1 + np.exp(-decision)))
        
        # Map prediction to readable format
        prediction_label = 'Threat' if prediction == 'attack' or prediction == 1 else 'Normal'
        
        return {
            'prediction': prediction_label,
            'confidence': confidence,
            'model_used': model_name,
            'raw_prediction': str(prediction)
        }
    
    def get_feature_importance(self, model_name=None):
        """
        Get feature importance for tree-based models.
        
        Args:
            model_name: Optional model name
        
        Returns:
            dict: Feature names and their importance scores
        """
        if model_name is None:
            model_name = self.active_model_name
        
        if model_name not in self.models:
            return {}
        
        model = self.models[model_name]
        
        # Check if model has feature_importances_
        if hasattr(model, 'feature_importances_'):
            # UAV-specific features from new dataset
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
        """
        Set active model for predictions.
        
        Args:
            model_name: Name of model to activate
        """
        if model_name in self.models:
            self.active_model_name = model_name
            return True
        return False
    
    def calculate_threat_level(self, prediction, confidence):
        """
        Calculate threat level based on prediction and confidence.
        
        Args:
            prediction: Prediction label ('Normal' or 'Threat')
            confidence: Confidence score (0-1)
        
        Returns:
            str: Threat level ('Low', 'Medium', 'High', 'Critical')
        """
        if prediction == 'Normal':
            return 'Low'
        
        if confidence >= 0.9:
            return 'Critical'
        elif confidence >= 0.75:
            return 'High'
        elif confidence >= 0.6:
            return 'Medium'
        else:
            return 'Low'


# Global ML service instance
ml_service = MLService()

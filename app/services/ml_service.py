"""
Machine Learning service for UAV threat detection.
Handles model loading, prediction, and model management.
"""
import os
import joblib
import numpy as np
from datetime import datetime


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
            # Load scaler from old location
            if self._app:
                base_path = os.path.dirname(self._app.root_path)
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            scaler_path = os.path.join(base_path, 'scaler.pkl')
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
            
            # Load default model from old location
            old_model_path = os.path.join(base_path, 'model', 'uav_security_model.pkl')
            if os.path.exists(old_model_path):
                self.models['RandomForest'] = joblib.load(old_model_path)
                self.active_model_name = 'RandomForest'
            
            # Load models from new location if app context available
            if self._app and self._app.config.get('ML_MODELS_FOLDER'):
                models_dir = self._app.config.get('ML_MODELS_FOLDER')
                if os.path.exists(models_dir):
                    for filename in os.listdir(models_dir):
                        if filename.endswith('.pkl') or filename.endswith('.joblib'):
                            model_name = filename.rsplit('.', 1)[0]
                            model_path = os.path.join(models_dir, filename)
                            try:
                                self.models[model_name] = joblib.load(model_path)
                            except Exception as e:
                                print(f"Error loading model {model_name}: {e}")
            
            if not self.active_model_name and self.models:
                self.active_model_name = list(self.models.keys())[0]
                
        except Exception as e:
            print(f"Error loading models: {e}")
    
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
            feature_names = ['Packet Size', 'Inter-arrival Time', 'Packet Rate', 
                           'Connection Duration', 'Failed Logins']
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

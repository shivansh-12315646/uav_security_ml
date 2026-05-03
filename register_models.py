import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uav_project.settings')
django.setup()

from core.models import MLModel
from django.contrib.auth import get_user_model
import json

User = get_user_model()
admin = User.objects.filter(is_superuser=True).first()

models_info = [
    {
        'name': 'Random Forest',
        'file_path': 'ml_models/random_forest.pkl',
        'accuracy': 99.2,
        'precision': 98.8,
        'recall': 99.1,
        'f1_score': 98.9,
        'is_active': False
    },
    {
        'name': 'XGBoost',
        'file_path': 'ml_models/xgboost.pkl',
        'accuracy': 99.5,
        'precision': 99.2,
        'recall': 99.3,
        'f1_score': 99.2,
        'is_active': True  # Active model
    },
    {
        'name': 'Gradient Boosting',
        'file_path': 'ml_models/gradient_boosting.pkl',
        'accuracy': 99.1,
        'precision': 98.7,
        'recall': 99.0,
        'f1_score': 98.8,
        'is_active': False
    }
]

for model_info in models_info:
    if os.path.exists(model_info['file_path']):
        MLModel.objects.update_or_create(
            name=model_info['name'],
            defaults={
                'version': '1.0',
                'accuracy': model_info['accuracy'],
                'precision': model_info['precision'],
                'recall': model_info['recall'],
                'f1_score': model_info['f1_score'],
                'is_active': model_info['is_active'],
                'file_path': model_info['file_path'],
                'trained_by': admin,
                'training_dataset_size': 20000,
                'description': f'{model_info["name"]} trained on UAV security dataset',
                'hyperparameters': json.dumps({'n_estimators': 100})
            }
        )
        print(f"✅ Registered {model_info['name']}")
    else:
        print(f"⚠️  Model file not found: {model_info['file_path']}")

print("\n✅ Model registration complete!")
"""
Training routes for model training and management.
"""
import os
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db, socketio
from app.models.ml_model import MLModel
from app.models.audit import AuditLog
from app.services.training_service import training_service
from app.utils.decorators import admin_required
from app.utils.helpers import get_client_ip
import threading

training_bp = Blueprint('training', __name__, url_prefix='/training')

ALLOWED_EXTENSIONS = {'csv'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@training_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Training dashboard page."""
    # Get all trained models
    models = MLModel.query.order_by(MLModel.created_at.desc()).all()
    
    # Get available algorithms
    algorithms = list(training_service.SUPPORTED_ALGORITHMS.keys())
    
    return render_template('training/dashboard.html', 
                         models=models,
                         algorithms=algorithms)


@training_bp.route('/upload-dataset', methods=['POST'])
@login_required
@admin_required
def upload_dataset():
    """Upload and validate training dataset."""
    try:
        if 'dataset' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['dataset']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Only CSV files are allowed.'
            }), 400
        
        # Save file
        filename = secure_filename(file.filename)
        upload_dir = os.path.join(
            os.path.dirname(current_user._app.root_path if hasattr(current_user, '_app') else __file__),
            'uploads'
        )
        os.makedirs(upload_dir, exist_ok=True)
        
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Preprocess and validate
        result = training_service.preprocess_dataset(filepath)
        
        if result['success']:
            result['filepath'] = filepath
            
            # Log action
            audit = AuditLog(
                user_id=current_user.id,
                action='dataset_upload',
                details=f"Uploaded dataset: {filename}",
                ip_address=get_client_ip()
            )
            db.session.add(audit)
            db.session.commit()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@training_bp.route('/start-training', methods=['POST'])
@login_required
@admin_required
def start_training():
    """Start model training."""
    try:
        data = request.get_json()
        
        algorithm = data.get('algorithm')
        dataset_path = data.get('dataset_path')
        test_size = float(data.get('test_size', 0.2))
        hyperparameters = data.get('hyperparameters', {})
        
        if not algorithm or not dataset_path:
            return jsonify({
                'success': False,
                'error': 'Algorithm and dataset path are required'
            }), 400
        
        if algorithm not in training_service.SUPPORTED_ALGORITHMS:
            return jsonify({
                'success': False,
                'error': f'Unsupported algorithm: {algorithm}'
            }), 400
        
        # Start training in background thread
        def train_async():
            with training_bp.app.app_context():
                result = training_service.train_model(
                    algorithm=algorithm,
                    dataset_path=dataset_path,
                    hyperparameters=hyperparameters,
                    test_size=test_size,
                    user_id=current_user.id
                )
                
                if result['success']:
                    # Save model metadata to database
                    model = MLModel(
                        name=algorithm,
                        version='1.0',
                        file_path=result['model_path'],
                        accuracy=result['metrics']['accuracy'],
                        precision=result['metrics']['precision'],
                        recall=result['metrics']['recall'],
                        f1_score=result['metrics']['f1_score'],
                        trained_by=current_user.id,
                        is_active=False
                    )
                    model.training_dataset_size = result['dataset_size']['total']
                    model.training_duration = result['training_duration']
                    model.description = f"Trained on {result['dataset_size']['total']} samples"
                    
                    db.session.add(model)
                    
                    # Log action
                    audit = AuditLog(
                        user_id=current_user.id,
                        action='model_training',
                        details=f"Trained {algorithm} model with {result['metrics']['accuracy']:.4f} accuracy",
                        ip_address=get_client_ip()
                    )
                    db.session.add(audit)
                    db.session.commit()
        
        # Store app context for thread
        training_bp.app = request._get_current_object().app._get_current_object()
        
        thread = threading.Thread(target=train_async)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Training started successfully',
            'training_id': training_service.current_training_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@training_bp.route('/models')
@login_required
@admin_required
def list_models():
    """List all trained models."""
    models = MLModel.query.order_by(MLModel.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'models': [model.to_dict() for model in models]
    })


@training_bp.route('/models/<int:model_id>/activate', methods=['POST'])
@login_required
@admin_required
def activate_model(model_id):
    """Activate a trained model."""
    try:
        model = MLModel.query.get_or_404(model_id)
        model.activate()
        
        # Log action
        audit = AuditLog(
            user_id=current_user.id,
            action='model_activation',
            details=f"Activated model: {model.name} v{model.version}",
            ip_address=get_client_ip()
        )
        db.session.add(audit)
        db.session.commit()
        
        flash(f'Model {model.name} v{model.version} activated successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Model activated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@training_bp.route('/models/<int:model_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_model(model_id):
    """Delete a trained model."""
    try:
        model = MLModel.query.get_or_404(model_id)
        
        # Delete model file if it exists
        if os.path.exists(model.file_path):
            os.remove(model.file_path)
        
        model_name = f"{model.name} v{model.version}"
        
        db.session.delete(model)
        
        # Log action
        audit = AuditLog(
            user_id=current_user.id,
            action='model_deletion',
            details=f"Deleted model: {model_name}",
            ip_address=get_client_ip()
        )
        db.session.add(audit)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Model deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@training_bp.route('/compare')
@login_required
@admin_required
def compare_models_page():
    """Model comparison page."""
    models = MLModel.query.order_by(MLModel.created_at.desc()).all()
    return render_template('training/compare.html', models=models)


@training_bp.route('/compare-models', methods=['POST'])
@login_required
@admin_required
def compare_models():
    """Compare multiple models."""
    try:
        data = request.get_json()
        model_ids = data.get('model_ids', [])
        
        if len(model_ids) < 2:
            return jsonify({
                'success': False,
                'error': 'Please select at least 2 models to compare'
            }), 400
        
        comparison = training_service.compare_models(model_ids)
        
        return jsonify({
            'success': True,
            'comparison': comparison
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@training_bp.route('/dataset-analyzer')
@login_required
@admin_required
def dataset_analyzer():
    """Dataset analyzer page."""
    return render_template('training/dataset_analyzer.html')


@training_bp.route('/analyze-dataset', methods=['POST'])
@login_required
@admin_required
def analyze_dataset():
    """Analyze uploaded dataset."""
    try:
        if 'dataset' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['dataset']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Only CSV files are allowed.'
            }), 400
        
        # Save temporarily
        filename = secure_filename(file.filename)
        upload_dir = os.path.join(
            os.path.dirname(request._get_current_object().app.root_path),
            'uploads'
        )
        os.makedirs(upload_dir, exist_ok=True)
        
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Analyze dataset
        result = training_service.preprocess_dataset(filepath)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# WebSocket event handlers
@socketio.on('connect', namespace='/training')
def handle_training_connect():
    """Handle WebSocket connection for training updates."""
    print('Client connected to training namespace')


@socketio.on('disconnect', namespace='/training')
def handle_training_disconnect():
    """Handle WebSocket disconnection."""
    print('Client disconnected from training namespace')

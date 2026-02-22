import os
import threading
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from core.models import MLModel, AuditLog
from core.decorators import admin_required
from services.training_service import training_service


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0]
    return request.META.get('REMOTE_ADDR', 'Unknown')


@login_required
@admin_required
def training_dashboard(request):
    models = MLModel.objects.order_by('-created_at')
    algorithms = list(training_service.SUPPORTED_ALGORITHMS.keys())
    return render(request, 'training/dashboard.html', {'models': models, 'algorithms': algorithms})


@login_required
@admin_required
@csrf_exempt
@require_http_methods(['POST'])
def upload_dataset(request):
    try:
        if 'dataset' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No file uploaded'}, status=400)
        file = request.FILES['dataset']
        if not file.name.endswith('.csv'):
            return JsonResponse({'success': False, 'error': 'Only CSV files allowed'}, status=400)

        from django.conf import settings
        upload_dir = settings.MEDIA_ROOT
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, file.name)
        with open(filepath, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

        result = training_service.preprocess_dataset(filepath)
        if result.get('success'):
            result['filepath'] = filepath
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@admin_required
@csrf_exempt
@require_http_methods(['POST'])
def start_training(request):
    import json
    try:
        data = json.loads(request.body)
        algorithm = data.get('algorithm')
        dataset_path = data.get('dataset_path')
        test_size = float(data.get('test_size', 0.2))

        if not algorithm or not dataset_path:
            return JsonResponse({'success': False, 'error': 'Algorithm and dataset_path required'}, status=400)

        def train_async():
            result = training_service.train_model(
                algorithm=algorithm, dataset_path=dataset_path,
                test_size=test_size, user_id=request.user.id
            )
            if result.get('success'):
                MLModel.objects.create(
                    name=algorithm, version='1.0',
                    file_path=result['model_path'],
                    accuracy=result['metrics']['accuracy'],
                    precision=result['metrics']['precision'],
                    recall=result['metrics']['recall'],
                    f1_score=result['metrics']['f1_score'],
                    trained_by=request.user,
                    training_dataset_size=result['dataset_size']['total'],
                    training_duration=result['training_duration'],
                    description=f"Trained on {result['dataset_size']['total']} samples",
                )

        thread = threading.Thread(target=train_async)
        thread.daemon = True
        thread.start()

        return JsonResponse({'success': True, 'message': 'Training started'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@admin_required
def list_models(request):
    models = MLModel.objects.order_by('-created_at')
    return JsonResponse({'success': True, 'models': [m.to_dict() for m in models]})


@login_required
@admin_required
@csrf_exempt
@require_http_methods(['POST'])
def activate_model(request, model_id):
    try:
        model = get_object_or_404(MLModel, id=model_id)
        model.activate()
        return JsonResponse({'success': True, 'message': 'Model activated'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@admin_required
@csrf_exempt
@require_http_methods(['DELETE'])
def delete_model(request, model_id):
    try:
        model = get_object_or_404(MLModel, id=model_id)
        if os.path.exists(model.file_path):
            os.remove(model.file_path)
        model.delete()
        return JsonResponse({'success': True, 'message': 'Model deleted'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@admin_required
def compare_models_page(request):
    models = MLModel.objects.order_by('-created_at')
    return render(request, 'training/compare.html', {'models': models})


@login_required
@admin_required
def dataset_analyzer(request):
    return render(request, 'training/dataset_analyzer.html')

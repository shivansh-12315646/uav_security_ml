"""
Views for unsupervised ML analysis:
  - Clustering dashboard (K-Means, DBSCAN)
  - Anomaly detection (Isolation Forest)
  - API endpoints for chart data
"""
import os
import json
import pandas as pd
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from services.unsupervised_service import (
    unsupervised_service,
    UAV_FEATURE_COLUMNS,
    FEATURE_DISPLAY_NAMES,
)

import logging

logger = logging.getLogger(__name__)


def _load_dataset():
    """Load the UAV dataset from disk."""
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    candidates = [
        os.path.join(base, 'data', 'uav_security_dataset.csv'),
        os.path.join(base, 'uav_data.csv'),
    ]
    for path in candidates:
        if os.path.exists(path):
            return pd.read_csv(path)
    return None


def _load_saved_results():
    """Load previously saved unsupervised results JSON."""
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(base, 'exports', 'unsupervised_results.json')
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return None


# ──────────────────────────────────────────────────────────────────────
# Page views
# ──────────────────────────────────────────────────────────────────────

@login_required
def unsupervised_dashboard(request):
    """Main unsupervised analysis dashboard."""
    saved = _load_saved_results()

    context = {
        'has_results': saved is not None,
        'results_json': saved if saved else {},
    }

    # Extract summary metrics for cards
    if saved:
        km = saved.get('kmeans', {})
        iso = saved.get('isolation_forest', {})
        pca = saved.get('pca', {})
        db = saved.get('dbscan', {})

        context.update({
            'kmeans_k': km.get('best_k', '—'),
            'kmeans_silhouette': round(km.get('metrics', {}).get('silhouette_score', 0), 4),
            'kmeans_ch': round(km.get('metrics', {}).get('calinski_harabasz_index', 0), 2),
            'kmeans_db': round(km.get('metrics', {}).get('davies_bouldin_index', 0), 4),
            'dbscan_clusters': db.get('n_clusters', '—'),
            'dbscan_noise': db.get('n_noise', '—'),
            'dbscan_silhouette': round(db.get('metrics', {}).get('silhouette_score', 0), 4),
            'anomaly_count': iso.get('n_anomalies', 0),
            'anomaly_rate': iso.get('anomaly_rate', 0),
            'normal_count': iso.get('n_normal', 0),
            'pca_variance': round(pca.get('total_explained_variance', 0) * 100, 2),
        })

    return render(request, 'unsupervised/dashboard.html', context)


# ──────────────────────────────────────────────────────────────────────
# API endpoints (return JSON for charts)
# ──────────────────────────────────────────────────────────────────────

@login_required
def api_run_analysis(request):
    """Run the full unsupervised analysis pipeline (POST)."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    df = _load_dataset()
    if df is None:
        return JsonResponse({'error': 'Dataset not found'}, status=404)

    try:
        results = unsupervised_service.run_full_analysis(df)

        # Save summary to disk
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        out_dir = os.path.join(base, 'exports')
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, 'unsupervised_results.json')

        save_results = {}
        for key, val in results.items():
            if isinstance(val, dict):
                save_results[key] = {
                    k: v for k, v in val.items()
                    if k not in ('labels', 'predictions', 'anomaly_scores',
                                 'coordinates', 'centroids', 'components', 'indices')
                }
            else:
                save_results[key] = val

        with open(out_path, 'w') as f:
            json.dump(save_results, f, indent=2, default=str)

        return JsonResponse({'success': True, 'results': save_results})
    except Exception as e:
        logger.error(f"Unsupervised analysis error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_cluster_data(request):
    """Return PCA-reduced cluster visualization data."""
    df = _load_dataset()
    if df is None:
        return JsonResponse({'error': 'Dataset not found'}, status=404)

    try:
        unsupervised_service.load_models()
        X = unsupervised_service.prepare_data(df, fit_scaler=False)

        # Get cluster labels
        if unsupervised_service.kmeans_model is None:
            return JsonResponse({'error': 'K-Means model not trained yet'}, status=404)

        labels = unsupervised_service.kmeans_model.predict(X).tolist()

        # PCA for visualization
        if unsupervised_service.pca_model is None:
            from sklearn.decomposition import PCA
            pca = PCA(n_components=2, random_state=42)
            coords = pca.fit_transform(X).tolist()
        else:
            coords = unsupervised_service.pca_model.transform(X).tolist()

        # Subsample for frontend performance
        import numpy as np
        max_points = 3000
        if len(coords) > max_points:
            rng = np.random.RandomState(42)
            idx = rng.choice(len(coords), max_points, replace=False).tolist()
            coords = [coords[i] for i in idx]
            labels = [labels[i] for i in idx]

        return JsonResponse({
            'coordinates': coords,
            'labels': labels,
            'n_clusters': int(max(labels) + 1) if labels else 0,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_elbow_data(request):
    """Return elbow analysis data from saved results."""
    saved = _load_saved_results()
    if saved and 'kmeans' in saved:
        elbow = saved['kmeans'].get('elbow', {})
        return JsonResponse(elbow)
    return JsonResponse({'error': 'No elbow data available'}, status=404)


@login_required
def api_anomaly_data(request):
    """Return anomaly detection summary data."""
    saved = _load_saved_results()
    if saved and 'isolation_forest' in saved:
        return JsonResponse(saved['isolation_forest'])
    return JsonResponse({'error': 'No anomaly data available'}, status=404)

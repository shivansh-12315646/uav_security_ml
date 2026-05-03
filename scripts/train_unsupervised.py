"""
Unsupervised ML Training Pipeline
===================================

Trains unsupervised models on the UAV security dataset:
- K-Means Clustering (with elbow analysis)
- DBSCAN Density-Based Clustering
- Isolation Forest Anomaly Detection
- PCA / t-SNE Dimensionality Reduction

All algorithms operate WITHOUT labels — this is the key distinction
from the supervised pipeline.  Labels are only used AFTER clustering
to evaluate how well the unsupervised methods discover the true groups.
"""
import os
import sys
import json
import time
import warnings
import numpy as np
import pandas as pd
from datetime import datetime

warnings.filterwarnings('ignore')

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from services.unsupervised_service import (
    UnsupervisedService,
    UAV_FEATURE_COLUMNS,
    FEATURE_DISPLAY_NAMES,
)

# ── Configuration ──────────────────────────────────────────────────────
DATA_FILE = os.path.join(PROJECT_ROOT, 'data', 'uav_security_dataset.csv')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'exports')


def load_dataset(path):
    """Load and validate the UAV dataset."""
    if not os.path.exists(path):
        print(f"❌ Dataset not found: {path}")
        print("   Run: python scripts/generate_dataset.py")
        sys.exit(1)
    df = pd.read_csv(path)
    print(f"✓ Loaded {len(df):,} samples, {len(df.columns)} columns")
    return df


def print_header(title):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def main():
    print_header("🚁 UAV SECURITY — UNSUPERVISED ML TRAINING PIPELINE")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ── Load data ──────────────────────────────────────────────────────
    print_header("📂 LOADING DATASET")
    df = load_dataset(DATA_FILE)

    # Show label distribution (for post-hoc evaluation only)
    if 'threat_type' in df.columns:
        print("\n📊 True label distribution (used ONLY for evaluation, not training):")
        for label, count in df['threat_type'].value_counts().items():
            pct = count / len(df) * 100
            print(f"   {label:30s} {count:6,} ({pct:5.1f}%)")
    print()

    # ── Initialize service ─────────────────────────────────────────────
    svc = UnsupervisedService()

    # ── Prepare data (scale features, NO labels) ───────────────────────
    print_header("⚙️  PREPARING FEATURES (No Labels)")
    X = svc.prepare_data(df, fit_scaler=True)
    print(f"   Feature matrix shape: {X.shape}")
    print(f"   Features: {', '.join(FEATURE_DISPLAY_NAMES[:X.shape[1]])}")

    all_results = {}
    total_start = time.time()

    # ── 1. K-MEANS CLUSTERING ──────────────────────────────────────────
    print_header("🎯 K-MEANS CLUSTERING")
    t0 = time.time()
    km_result = svc.run_kmeans(X)
    km_time = time.time() - t0

    print(f"\n   Best k: {km_result['best_k']}")
    print(f"   Silhouette Score:       {km_result['metrics']['silhouette_score']:.4f}")
    print(f"   Calinski-Harabasz Index: {km_result['metrics']['calinski_harabasz_index']:.2f}")
    print(f"   Davies-Bouldin Index:    {km_result['metrics']['davies_bouldin_index']:.4f}")
    print(f"   Training time:          {km_time:.2f}s")
    print(f"\n   Cluster sizes:")
    for cid, sz in sorted(km_result['cluster_sizes'].items()):
        print(f"      Cluster {cid}: {sz:,} samples ({sz / len(X) * 100:.1f}%)")

    # Elbow summary
    print(f"\n   Elbow analysis (k → inertia → silhouette):")
    for k_val, inertia, sil in zip(
        km_result['elbow']['k_values'],
        km_result['elbow']['inertias'],
        km_result['elbow']['silhouette_scores'],
    ):
        marker = " ← BEST" if k_val == km_result['best_k'] else ""
        print(f"      k={k_val:2d}  inertia={inertia:12.1f}  silhouette={sil:.4f}{marker}")

    km_result['training_time'] = km_time
    all_results['kmeans'] = km_result

    # ── 2. DBSCAN CLUSTERING ───────────────────────────────────────────
    print_header("🔷 DBSCAN DENSITY-BASED CLUSTERING")

    # Try several eps values
    best_dbscan = None
    best_dbscan_sil = -1
    print("\n   Scanning eps values...")
    for eps_val in [0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 3.0]:
        t0 = time.time()
        db_result = svc.run_dbscan(X, eps=eps_val, min_samples=5)
        db_time = time.time() - t0
        sil = db_result['metrics']['silhouette_score']
        nc = db_result['n_clusters']
        nn = db_result['n_noise']
        print(f"      eps={eps_val:.1f}  clusters={nc:3d}  noise={nn:5d}  "
              f"silhouette={sil:.4f}  time={db_time:.2f}s")
        if nc > 1 and sil > best_dbscan_sil:
            best_dbscan_sil = sil
            best_dbscan = db_result
            best_dbscan['training_time'] = db_time

    if best_dbscan is None:
        # Fallback: use eps=1.5
        best_dbscan = svc.run_dbscan(X, eps=1.5, min_samples=5)
        best_dbscan['training_time'] = 0

    print(f"\n   ✓ Best DBSCAN: eps={best_dbscan['eps']}, "
          f"{best_dbscan['n_clusters']} clusters, "
          f"{best_dbscan['n_noise']} noise, "
          f"silhouette={best_dbscan['metrics']['silhouette_score']:.4f}")
    all_results['dbscan'] = best_dbscan

    # ── 3. ISOLATION FOREST ────────────────────────────────────────────
    print_header("🛡️ ISOLATION FOREST ANOMALY DETECTION")
    t0 = time.time()
    if_result = svc.run_isolation_forest(X, contamination=0.15)
    if_time = time.time() - t0

    print(f"\n   Anomalies detected: {if_result['n_anomalies']:,} "
          f"({if_result['anomaly_rate']:.1f}%)")
    print(f"   Normal samples:     {if_result['n_normal']:,}")
    print(f"   Score stats:")
    print(f"      Mean:  {if_result['score_stats']['mean']:.4f}")
    print(f"      Std:   {if_result['score_stats']['std']:.4f}")
    print(f"      Min:   {if_result['score_stats']['min']:.4f}")
    print(f"      Max:   {if_result['score_stats']['max']:.4f}")
    print(f"   Training time: {if_time:.2f}s")

    if_result['training_time'] = if_time
    all_results['isolation_forest'] = if_result

    # ── 4. PCA DIMENSIONALITY REDUCTION ────────────────────────────────
    print_header("📊 PCA DIMENSIONALITY REDUCTION")
    t0 = time.time()
    pca_result = svc.run_pca(X, n_components=2)
    pca_time = time.time() - t0

    print(f"\n   Components: 2")
    print(f"   Explained variance:")
    for i, ev in enumerate(pca_result['explained_variance_ratio']):
        print(f"      PC{i + 1}: {ev * 100:.2f}%")
    print(f"   Total explained: {pca_result['total_explained_variance'] * 100:.2f}%")
    print(f"   Time: {pca_time:.2f}s")

    pca_result['training_time'] = pca_time
    all_results['pca'] = pca_result

    # ── 5. t-SNE VISUALIZATION ─────────────────────────────────────────
    print_header("🌌 t-SNE VISUALIZATION")
    t0 = time.time()
    tsne_result = svc.run_tsne(X, max_samples=5000)
    tsne_time = time.time() - t0

    print(f"\n   Samples used: {tsne_result['n_samples']:,}")
    print(f"   Perplexity: {tsne_result['perplexity']}")
    print(f"   Time: {tsne_time:.2f}s")

    tsne_result['training_time'] = tsne_time
    all_results['tsne'] = tsne_result

    # ── 6. POST-HOC EVALUATION (compare clusters to true labels) ───────
    if 'threat_type' in df.columns:
        print_header("🔍 POST-HOC EVALUATION (Clusters vs True Labels)")
        true_labels = df['threat_type'].values

        # Use t-SNE indices for alignment
        indices = np.array(tsne_result['indices'])
        km_labels_sub = np.array(km_result['labels'])[indices]
        true_sub = true_labels[indices]

        # Build confusion-like table
        unique_true = sorted(set(true_sub))
        unique_km = sorted(set(km_labels_sub))

        print(f"\n   K-Means cluster composition (sampled {len(indices):,} points):")
        print(f"   {'Cluster':<10}", end="")
        for tl in unique_true:
            print(f" {tl[:12]:>12}", end="")
        print()
        print(f"   {'-' * (10 + 13 * len(unique_true))}")

        for ci in unique_km:
            mask = km_labels_sub == ci
            print(f"   {ci:<10d}", end="")
            for tl in unique_true:
                count = int(((km_labels_sub == ci) & (true_sub == tl)).sum())
                print(f" {count:>12,}", end="")
            print()

    # ── SUMMARY ────────────────────────────────────────────────────────
    total_time = time.time() - total_start

    print_header("📋 SUMMARY")
    print(f"""
    ┌─────────────────────────┬──────────────────────┐
    │ K-Means Clusters        │ {km_result['best_k']:<20d} │
    │ K-Means Silhouette      │ {km_result['metrics']['silhouette_score']:<20.4f} │
    │ DBSCAN Clusters         │ {best_dbscan['n_clusters']:<20d} │
    │ DBSCAN Noise Points     │ {best_dbscan['n_noise']:<20d} │
    │ Anomalies Detected      │ {if_result['n_anomalies']:<20d} │
    │ Anomaly Rate            │ {if_result['anomaly_rate']:<19.1f}% │
    │ PCA Explained Var.      │ {pca_result['total_explained_variance'] * 100:<19.1f}% │
    │ Total Training Time     │ {total_time:<19.2f}s │
    └─────────────────────────┴──────────────────────┘
    """)

    # ── Save results ───────────────────────────────────────────────────
    os.makedirs(RESULTS_DIR, exist_ok=True)
    results_path = os.path.join(RESULTS_DIR, 'unsupervised_results.json')

    # Strip large arrays for JSON (keep summary only)
    save_results = {}
    for key, val in all_results.items():
        save_results[key] = {
            k: v for k, v in val.items()
            if k not in ('labels', 'predictions', 'anomaly_scores',
                         'coordinates', 'centroids', 'components', 'indices')
        }

    with open(results_path, 'w') as f:
        json.dump(save_results, f, indent=2, default=str)
    print(f"💾 Results saved to {results_path}")

    print(f"\n🎉 Unsupervised training pipeline complete!")
    print(f"   Models saved in: ml_models/")
    print(f"   Results saved in: exports/")
    return all_results


if __name__ == '__main__':
    main()

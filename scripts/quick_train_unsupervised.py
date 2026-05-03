"""Quick training script that subsamples for speed, then saves results."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from services.unsupervised_service import UnsupervisedService, FEATURE_DISPLAY_NAMES

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'uav_security_dataset.csv')
EXPORTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'exports')

df = pd.read_csv(DATA)
print(f"Loaded {len(df)} rows")

# Subsample for speed (5000 samples)
if len(df) > 5000:
    df = df.sample(5000, random_state=42).reset_index(drop=True)
    print(f"Subsampled to {len(df)} rows")

svc = UnsupervisedService()
X = svc.prepare_data(df, fit_scaler=True)
print(f"Shape: {X.shape}")

# K-Means
print("Running K-Means...")
km = svc.run_kmeans(X)
print(f"  k={km['best_k']}, silhouette={km['metrics']['silhouette_score']:.4f}")

# DBSCAN (single eps)
print("Running DBSCAN...")
db = svc.run_dbscan(X, eps=1.5, min_samples=5)
print(f"  clusters={db['n_clusters']}, noise={db['n_noise']}")

# Isolation Forest
print("Running Isolation Forest...")
iso = svc.run_isolation_forest(X, contamination=0.15)
print(f"  anomalies={iso['n_anomalies']}, rate={iso['anomaly_rate']}%")

# PCA
print("Running PCA...")
pca = svc.run_pca(X)
print(f"  variance={pca['total_explained_variance']*100:.1f}%")

# t-SNE (small sample)
print("Running t-SNE...")
tsne = svc.run_tsne(X, max_samples=2000)
print(f"  samples={tsne['n_samples']}")

# Save results
os.makedirs(EXPORTS, exist_ok=True)
save = {}
for key, val in svc.last_results.items():
    if isinstance(val, dict):
        save[key] = {k: v for k, v in val.items()
                     if k not in ('labels','predictions','anomaly_scores','coordinates','centroids','components','indices')}
    else:
        save[key] = val

with open(os.path.join(EXPORTS, 'unsupervised_results.json'), 'w') as f:
    json.dump(save, f, indent=2, default=str)

print("DONE - Results saved to exports/unsupervised_results.json")

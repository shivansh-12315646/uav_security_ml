"""
Unsupervised Machine Learning service for UAV Security.

Provides clustering (K-Means, DBSCAN), anomaly detection (Isolation Forest),
and dimensionality reduction (PCA, t-SNE) capabilities.
All methods operate WITHOUT labels — the core of unsupervised learning.
"""
import os
import joblib
import numpy as np
import pandas as pd
import logging
from sklearn.cluster import KMeans, DBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    silhouette_score,
    calinski_harabasz_score,
    davies_bouldin_score,
)

logger = logging.getLogger(__name__)

# Feature columns used across the UAV dataset
UAV_FEATURE_COLUMNS = [
    'altitude', 'speed', 'direction', 'signal_strength',
    'distance_from_base', 'flight_time', 'battery_level',
    'temperature', 'vibration', 'gps_accuracy',
]

FEATURE_DISPLAY_NAMES = [
    'Altitude', 'Speed', 'Direction', 'Signal Strength',
    'Distance from Base', 'Flight Time', 'Battery Level',
    'Temperature', 'Vibration', 'GPS Accuracy',
]


class UnsupervisedService:
    """Service for all unsupervised ML operations."""

    def __init__(self):
        self.scaler = None
        self.kmeans_model = None
        self.dbscan_model = None
        self.isolation_forest = None
        self.pca_model = None
        self.last_results = {}

    # ------------------------------------------------------------------
    # Model persistence helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _models_dir():
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ml_models',
        )

    def load_models(self):
        """Load all saved unsupervised models."""
        mdir = self._models_dir()
        pairs = [
            ('scaler_unsupervised.pkl', 'scaler'),
            ('kmeans.pkl', 'kmeans_model'),
            ('dbscan.pkl', 'dbscan_model'),
            ('isolation_forest.pkl', 'isolation_forest'),
            ('pca.pkl', 'pca_model'),
        ]
        for fname, attr in pairs:
            path = os.path.join(mdir, fname)
            if os.path.exists(path):
                try:
                    setattr(self, attr, joblib.load(path))
                    logger.info(f"Loaded {attr} from {path}")
                except Exception as e:
                    logger.error(f"Error loading {attr}: {e}")
        logger.info("Unsupervised models loading complete.")

    def _save(self, obj, filename):
        mdir = self._models_dir()
        os.makedirs(mdir, exist_ok=True)
        path = os.path.join(mdir, filename)
        joblib.dump(obj, path)
        logger.info(f"Saved {filename}")
        return path

    # ------------------------------------------------------------------
    # Data preparation
    # ------------------------------------------------------------------

    def prepare_data(self, df: pd.DataFrame, fit_scaler: bool = False):
        """
        Extract UAV feature columns, scale, and return numpy array.

        Args:
            df: DataFrame with UAV feature columns.
            fit_scaler: If True, fit a new scaler; otherwise use existing.

        Returns:
            Scaled numpy array of shape (n_samples, n_features).
        """
        # Accept either exact column names or a superset
        available = [c for c in UAV_FEATURE_COLUMNS if c in df.columns]
        if not available:
            raise ValueError(
                f"Dataset must contain at least some of: {UAV_FEATURE_COLUMNS}"
            )
        X = df[available].values.astype(np.float64)

        if fit_scaler or self.scaler is None:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            self._save(self.scaler, 'scaler_unsupervised.pkl')
        else:
            X_scaled = self.scaler.transform(X)

        return X_scaled

    # ------------------------------------------------------------------
    # K-Means Clustering
    # ------------------------------------------------------------------

    def run_kmeans(self, X, k=None, k_range=None):
        """
        Run K-Means clustering.

        If *k* is given, clusters into *k* groups.
        If *k_range* is given (e.g. (2, 11)), runs elbow analysis and picks
        the best k via silhouette score, then clusters.

        Returns:
            dict with labels, centroids, inertias, silhouette scores, etc.
        """
        if k_range is None:
            k_range = range(2, 11)

        # ── Elbow analysis ──
        inertias = []
        silhouette_scores_list = []
        ch_scores = []

        for ki in k_range:
            km = KMeans(n_clusters=ki, random_state=42, n_init=10, max_iter=300)
            labels = km.fit_predict(X)
            inertias.append(float(km.inertia_))

            if len(set(labels)) > 1:
                sil = float(silhouette_score(X, labels))
                ch = float(calinski_harabasz_score(X, labels))
            else:
                sil = 0.0
                ch = 0.0
            silhouette_scores_list.append(sil)
            ch_scores.append(ch)

        # Best k by silhouette
        best_k = list(k_range)[int(np.argmax(silhouette_scores_list))] if k is None else k

        # ── Final clustering ──
        self.kmeans_model = KMeans(
            n_clusters=best_k, random_state=42, n_init=10, max_iter=300
        )
        labels = self.kmeans_model.fit_predict(X)
        self._save(self.kmeans_model, 'kmeans.pkl')

        sil_final = float(silhouette_score(X, labels)) if len(set(labels)) > 1 else 0.0
        ch_final = float(calinski_harabasz_score(X, labels)) if len(set(labels)) > 1 else 0.0
        db_final = float(davies_bouldin_score(X, labels)) if len(set(labels)) > 1 else 0.0

        result = {
            'algorithm': 'K-Means',
            'best_k': int(best_k),
            'labels': labels.tolist(),
            'centroids': self.kmeans_model.cluster_centers_.tolist(),
            'elbow': {
                'k_values': list(k_range),
                'inertias': inertias,
                'silhouette_scores': silhouette_scores_list,
                'calinski_harabasz_scores': ch_scores,
            },
            'metrics': {
                'silhouette_score': sil_final,
                'calinski_harabasz_index': ch_final,
                'davies_bouldin_index': db_final,
                'n_clusters': int(best_k),
            },
            'cluster_sizes': {
                int(c): int(count)
                for c, count in zip(*np.unique(labels, return_counts=True))
            },
        }
        self.last_results['kmeans'] = result
        return result

    # ------------------------------------------------------------------
    # DBSCAN Clustering
    # ------------------------------------------------------------------

    def run_dbscan(self, X, eps=0.5, min_samples=5):
        """
        Run DBSCAN density-based clustering.

        Returns:
            dict with labels, n_clusters, noise points, metrics.
        """
        self.dbscan_model = DBSCAN(eps=eps, min_samples=min_samples)
        labels = self.dbscan_model.fit_predict(X)
        self._save(self.dbscan_model, 'dbscan.pkl')

        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = int((labels == -1).sum())

        if n_clusters > 1:
            # Exclude noise for silhouette
            mask = labels != -1
            sil = float(silhouette_score(X[mask], labels[mask])) if mask.sum() > 1 else 0.0
            ch = float(calinski_harabasz_score(X[mask], labels[mask])) if mask.sum() > 1 else 0.0
            db = float(davies_bouldin_score(X[mask], labels[mask])) if mask.sum() > 1 else 0.0
        else:
            sil = ch = db = 0.0

        result = {
            'algorithm': 'DBSCAN',
            'labels': labels.tolist(),
            'n_clusters': n_clusters,
            'n_noise': n_noise,
            'eps': eps,
            'min_samples': min_samples,
            'metrics': {
                'silhouette_score': sil,
                'calinski_harabasz_index': ch,
                'davies_bouldin_index': db,
                'n_clusters': n_clusters,
                'n_noise': n_noise,
            },
            'cluster_sizes': {
                int(c): int(count)
                for c, count in zip(*np.unique(labels, return_counts=True))
            },
        }
        self.last_results['dbscan'] = result
        return result

    # ------------------------------------------------------------------
    # Isolation Forest (Anomaly Detection)
    # ------------------------------------------------------------------

    def run_isolation_forest(self, X, contamination=0.1):
        """
        Run Isolation Forest anomaly detection.

        Returns:
            dict with anomaly labels (-1 = anomaly, 1 = normal),
            anomaly scores, and summary statistics.
        """
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
            n_jobs=-1,
        )
        predictions = self.isolation_forest.fit_predict(X)  # -1 anomaly, 1 normal
        scores = self.isolation_forest.decision_function(X)
        self._save(self.isolation_forest, 'isolation_forest.pkl')

        n_anomalies = int((predictions == -1).sum())
        n_normal = int((predictions == 1).sum())

        result = {
            'algorithm': 'Isolation Forest',
            'predictions': predictions.tolist(),
            'anomaly_scores': scores.tolist(),
            'contamination': contamination,
            'n_anomalies': n_anomalies,
            'n_normal': n_normal,
            'anomaly_rate': round(n_anomalies / len(predictions) * 100, 2),
            'score_stats': {
                'mean': float(np.mean(scores)),
                'std': float(np.std(scores)),
                'min': float(np.min(scores)),
                'max': float(np.max(scores)),
            },
        }
        self.last_results['isolation_forest'] = result
        return result

    # ------------------------------------------------------------------
    # PCA Dimensionality Reduction
    # ------------------------------------------------------------------

    def run_pca(self, X, n_components=2):
        """
        Run PCA for dimensionality reduction and visualization.

        Returns:
            dict with transformed coordinates and explained variance.
        """
        self.pca_model = PCA(n_components=n_components, random_state=42)
        X_pca = self.pca_model.fit_transform(X)
        self._save(self.pca_model, 'pca.pkl')

        result = {
            'algorithm': 'PCA',
            'coordinates': X_pca.tolist(),
            'explained_variance_ratio': self.pca_model.explained_variance_ratio_.tolist(),
            'total_explained_variance': float(
                sum(self.pca_model.explained_variance_ratio_)
            ),
            'components': self.pca_model.components_.tolist(),
            'n_components': n_components,
        }
        self.last_results['pca'] = result
        return result

    # ------------------------------------------------------------------
    # t-SNE Dimensionality Reduction
    # ------------------------------------------------------------------

    def run_tsne(self, X, n_components=2, perplexity=30, max_samples=5000):
        """
        Run t-SNE for visualization (on a subsample for speed).

        Returns:
            dict with transformed coordinates and indices used.
        """
        if len(X) > max_samples:
            rng = np.random.RandomState(42)
            indices = rng.choice(len(X), size=max_samples, replace=False)
            X_sub = X[indices]
        else:
            indices = np.arange(len(X))
            X_sub = X

        tsne = TSNE(
            n_components=n_components,
            perplexity=min(perplexity, len(X_sub) - 1),
            random_state=42,
            max_iter=1000,
        )
        X_tsne = tsne.fit_transform(X_sub)

        result = {
            'algorithm': 't-SNE',
            'coordinates': X_tsne.tolist(),
            'indices': indices.tolist(),
            'n_samples': len(X_sub),
            'perplexity': perplexity,
        }
        self.last_results['tsne'] = result
        return result

    # ------------------------------------------------------------------
    # Predict single sample (anomaly)
    # ------------------------------------------------------------------

    def predict_anomaly(self, features):
        """
        Predict whether a single UAV sample is an anomaly.

        Args:
            features: list of 10 feature values.

        Returns:
            dict with is_anomaly, anomaly_score.
        """
        if self.isolation_forest is None:
            raise ValueError("Isolation Forest model not loaded")

        X = np.array(features).reshape(1, -1)
        if self.scaler is not None:
            X = self.scaler.transform(X)

        pred = self.isolation_forest.predict(X)[0]
        score = float(self.isolation_forest.decision_function(X)[0])

        return {
            'is_anomaly': bool(pred == -1),
            'anomaly_score': score,
            'label': 'Anomaly' if pred == -1 else 'Normal',
        }

    def predict_cluster(self, features):
        """
        Predict the cluster assignment for a single UAV sample.

        Args:
            features: list of 10 feature values.

        Returns:
            dict with cluster_id.
        """
        if self.kmeans_model is None:
            raise ValueError("K-Means model not loaded")

        X = np.array(features).reshape(1, -1)
        if self.scaler is not None:
            X = self.scaler.transform(X)

        cluster = int(self.kmeans_model.predict(X)[0])
        return {'cluster_id': cluster}

    # ------------------------------------------------------------------
    # Full analysis pipeline
    # ------------------------------------------------------------------

    def run_full_analysis(self, df: pd.DataFrame, k=None, eps=0.5,
                          min_samples=5, contamination=0.1):
        """
        Run the complete unsupervised analysis pipeline.

        Returns:
            dict with results from all algorithms.
        """
        logger.info("Starting full unsupervised analysis pipeline...")

        X = self.prepare_data(df, fit_scaler=True)
        logger.info(f"Data prepared: {X.shape}")

        results = {}

        # K-Means
        logger.info("Running K-Means...")
        results['kmeans'] = self.run_kmeans(X, k=k)
        logger.info(f"K-Means done: k={results['kmeans']['best_k']}, "
                     f"silhouette={results['kmeans']['metrics']['silhouette_score']:.4f}")

        # DBSCAN
        logger.info("Running DBSCAN...")
        results['dbscan'] = self.run_dbscan(X, eps=eps, min_samples=min_samples)
        logger.info(f"DBSCAN done: {results['dbscan']['n_clusters']} clusters, "
                     f"{results['dbscan']['n_noise']} noise points")

        # Isolation Forest
        logger.info("Running Isolation Forest...")
        results['isolation_forest'] = self.run_isolation_forest(X, contamination=contamination)
        logger.info(f"Isolation Forest done: {results['isolation_forest']['n_anomalies']} anomalies "
                     f"({results['isolation_forest']['anomaly_rate']}%)")

        # PCA
        logger.info("Running PCA...")
        results['pca'] = self.run_pca(X)
        logger.info(f"PCA done: explained variance = "
                     f"{results['pca']['total_explained_variance']:.4f}")

        # t-SNE (subsample for speed)
        logger.info("Running t-SNE...")
        results['tsne'] = self.run_tsne(X)
        logger.info(f"t-SNE done: {results['tsne']['n_samples']} samples projected")

        results['data_shape'] = list(X.shape)
        results['feature_names'] = FEATURE_DISPLAY_NAMES[:X.shape[1]]

        self.last_results = results
        logger.info("Full unsupervised analysis pipeline complete.")
        return results


# Global unsupervised service instance
unsupervised_service = UnsupervisedService()

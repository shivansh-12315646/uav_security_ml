"""
Model Comparison and Benchmarking Tool
=======================================

Compares all trained models and generates comprehensive comparison reports:
- Side-by-side performance metrics
- Visual comparisons (charts, graphs)
- Detailed analysis and recommendations
- Export to JSON, CSV, and HTML reports
"""
import os
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configuration
RESULTS_FILE = 'exports/model_comparison.json'
EXPORTS_DIR = 'exports'
VISUALIZATIONS_DIR = 'exports/visualizations'


class ModelComparator:
    """Tool for comparing and benchmarking ML models."""
    
    def __init__(self, results_file=RESULTS_FILE):
        """Initialize comparator."""
        self.results_file = results_file
        self.results = None
        
        # Create directories
        os.makedirs(EXPORTS_DIR, exist_ok=True)
        os.makedirs(VISUALIZATIONS_DIR, exist_ok=True)
        
        # Set plot style
        sns.set_style('darkgrid')
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
    
    def load_results(self):
        """Load comparison results."""
        print("\n" + "=" * 70)
        print("📊 MODEL COMPARISON TOOL")
        print("=" * 70)
        
        if not os.path.exists(self.results_file):
            print(f"❌ Error: Results file not found: {self.results_file}")
            print("   Please run training first: python scripts/train_models.py")
            return False
        
        print(f"\n📂 Loading results from {self.results_file}...")
        with open(self.results_file, 'r') as f:
            self.results = json.load(f)
        
        print(f"✓ Loaded results for {len(self.results)} models")
        return True
    
    def create_metrics_comparison_chart(self):
        """Create bar chart comparing key metrics."""
        print("\n📊 Creating metrics comparison chart...")
        
        # Prepare data
        models = list(self.results.keys())
        metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        
        data = {metric: [self.results[m][metric] * 100 for m in models] for metric in metrics}
        
        # Create chart
        x = np.arange(len(models))
        width = 0.2
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for i, metric in enumerate(metrics):
            ax.bar(x + i * width, data[metric], width, label=metric.replace('_', ' ').title())
        
        ax.set_xlabel('Model', fontsize=12, fontweight='bold')
        ax.set_ylabel('Score (%)', fontsize=12, fontweight='bold')
        ax.set_title('Model Performance Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x + width * 1.5)
        ax.set_xticklabels(models)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # Save chart
        chart_file = os.path.join(VISUALIZATIONS_DIR, 'metrics_comparison.png')
        plt.tight_layout()
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Chart saved: {chart_file}")
    
    def create_training_time_chart(self):
        """Create chart comparing training times."""
        print("\n⏱️  Creating training time comparison chart...")
        
        # Prepare data
        models = list(self.results.keys())
        times = [self.results[m]['training_time'] for m in models]
        
        # Create chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars = ax.barh(models, times, color='steelblue')
        
        # Color fastest and slowest differently
        if times:
            min_idx = times.index(min(times))
            max_idx = times.index(max(times))
            bars[min_idx].set_color('green')
            bars[max_idx].set_color('red')
        
        ax.set_xlabel('Training Time (seconds)', fontsize=12, fontweight='bold')
        ax.set_title('Training Time Comparison', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (model, time) in enumerate(zip(models, times)):
            ax.text(time + 0.5, i, f'{time:.2f}s', va='center')
        
        # Save chart
        chart_file = os.path.join(VISUALIZATIONS_DIR, 'training_time_comparison.png')
        plt.tight_layout()
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Chart saved: {chart_file}")
    
    def create_confusion_matrices(self):
        """Create confusion matrix visualizations for all models."""
        print("\n📉 Creating confusion matrices...")
        
        n_models = len(self.results)
        fig, axes = plt.subplots(1, n_models, figsize=(5 * n_models, 4))
        
        if n_models == 1:
            axes = [axes]
        
        for ax, (model_name, results) in zip(axes, self.results.items()):
            cm = np.array(results['confusion_matrix'])
            
            # Create heatmap
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                       xticklabels=['Normal', 'Threat'],
                       yticklabels=['Normal', 'Threat'])
            
            ax.set_title(f'{model_name}\nAccuracy: {results["accuracy"]*100:.2f}%',
                        fontweight='bold')
            ax.set_ylabel('True Label', fontweight='bold')
            ax.set_xlabel('Predicted Label', fontweight='bold')
        
        plt.tight_layout()
        
        # Save chart
        chart_file = os.path.join(VISUALIZATIONS_DIR, 'confusion_matrices.png')
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Chart saved: {chart_file}")
    
    def create_cv_scores_chart(self):
        """Create cross-validation scores comparison."""
        print("\n🔄 Creating cross-validation comparison chart...")
        
        # Prepare data
        models = list(self.results.keys())
        cv_means = [self.results[m]['cv_mean'] * 100 for m in models]
        cv_stds = [self.results[m]['cv_std'] * 100 for m in models]
        
        # Create chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(models))
        ax.bar(x, cv_means, yerr=cv_stds, capsize=5, color='teal', alpha=0.7)
        
        ax.set_xlabel('Model', fontsize=12, fontweight='bold')
        ax.set_ylabel('Cross-Validation Accuracy (%)', fontsize=12, fontweight='bold')
        ax.set_title('Cross-Validation Performance', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(models)
        ax.grid(axis='y', alpha=0.3)
        
        # Save chart
        chart_file = os.path.join(VISUALIZATIONS_DIR, 'cv_scores.png')
        plt.tight_layout()
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Chart saved: {chart_file}")
    
    def export_to_csv(self):
        """Export comparison results to CSV."""
        print("\n💾 Exporting results to CSV...")
        
        # Prepare data for DataFrame
        data = []
        for model_name, results in self.results.items():
            row = {
                'Model': model_name,
                'Accuracy (%)': f"{results['accuracy'] * 100:.2f}",
                'Precision (%)': f"{results['precision'] * 100:.2f}",
                'Recall (%)': f"{results['recall'] * 100:.2f}",
                'F1-Score (%)': f"{results['f1_score'] * 100:.2f}",
                'ROC AUC': f"{results['roc_auc']:.4f}" if results['roc_auc'] else 'N/A',
                'Training Time (s)': f"{results['training_time']:.2f}",
                'CV Accuracy (%)': f"{results['cv_mean'] * 100:.2f}",
                'CV Std Dev (%)': f"{results['cv_std'] * 100:.2f}"
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Save to CSV
        csv_file = os.path.join(EXPORTS_DIR, 'model_comparison.csv')
        df.to_csv(csv_file, index=False)
        
        print(f"✓ CSV saved: {csv_file}")
        print("\n" + df.to_string(index=False))
    
    def generate_recommendation(self):
        """Generate model recommendation based on results."""
        print("\n" + "=" * 70)
        print("🏆 MODEL RECOMMENDATION")
        print("=" * 70)
        
        # Find best models for different criteria
        best_accuracy = max(self.results.items(), key=lambda x: x[1]['accuracy'])
        best_f1 = max(self.results.items(), key=lambda x: x[1]['f1_score'])
        fastest = min(self.results.items(), key=lambda x: x[1]['training_time'])
        
        print(f"\n🎯 Best Overall Accuracy:")
        print(f"   {best_accuracy[0]}: {best_accuracy[1]['accuracy'] * 100:.2f}%")
        
        print(f"\n⚖️  Best F1-Score (Balanced Performance):")
        print(f"   {best_f1[0]}: {best_f1[1]['f1_score'] * 100:.2f}%")
        
        print(f"\n⚡ Fastest Training:")
        print(f"   {fastest[0]}: {fastest[1]['training_time']:.2f}s")
        
        # Overall recommendation
        print(f"\n💡 Recommendation:")
        if best_accuracy[0] == best_f1[0]:
            print(f"   Use {best_accuracy[0]} for production deployment.")
            print(f"   - Highest accuracy and best balanced performance")
            print(f"   - Training time: {best_accuracy[1]['training_time']:.2f}s")
        else:
            print(f"   For maximum accuracy: {best_accuracy[0]} ({best_accuracy[1]['accuracy'] * 100:.2f}%)")
            print(f"   For balanced performance: {best_f1[0]} (F1: {best_f1[1]['f1_score'] * 100:.2f}%)")
            print(f"   For quick training: {fastest[0]} ({fastest[1]['training_time']:.2f}s)")
    
    def run_full_comparison(self):
        """Run complete model comparison analysis."""
        if not self.load_results():
            return
        
        print("\n" + "=" * 70)
        print("🎨 GENERATING VISUALIZATIONS")
        print("=" * 70)
        
        # Create all visualizations
        self.create_metrics_comparison_chart()
        self.create_training_time_chart()
        self.create_confusion_matrices()
        self.create_cv_scores_chart()
        
        # Export results
        self.export_to_csv()
        
        # Generate recommendation
        self.generate_recommendation()
        
        print("\n" + "=" * 70)
        print("✅ COMPARISON COMPLETE!")
        print("=" * 70)
        print(f"\n📁 Visualizations saved in: {VISUALIZATIONS_DIR}/")
        print(f"📊 CSV report saved in: {EXPORTS_DIR}/")
        print(f"\n🎉 Review the results and choose the best model for deployment!")


def main():
    """Main entry point."""
    comparator = ModelComparator()
    comparator.run_full_comparison()


if __name__ == "__main__":
    main()

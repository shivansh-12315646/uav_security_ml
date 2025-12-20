/**
 * Charts Configuration - Chart.js setup for enterprise dashboard
 * Handles all chart visualizations with cybersecurity theme
 */

// Chart.js global configuration
if (typeof Chart !== 'undefined') {
    Chart.defaults.color = '#cbd5e1';
    Chart.defaults.borderColor = 'rgba(59, 130, 246, 0.2)';
    Chart.defaults.font.family = "'Inter', 'Segoe UI', sans-serif";
}

/**
 * Create detection trend chart (line chart)
 */
function createDetectionTrendChart(elementId, data) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.date),
            datasets: [{
                label: 'Total Detections',
                data: data.map(d => d.count),
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#3b82f6',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2
            }, {
                label: 'Threats',
                data: data.map(d => d.threats || 0),
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#ef4444',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#cbd5e1',
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(30, 41, 59, 0.95)',
                    titleColor: '#f8fafc',
                    bodyColor: '#cbd5e1',
                    borderColor: 'rgba(59, 130, 246, 0.5)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += context.parsed.y;
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(59, 130, 246, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#cbd5e1',
                        padding: 10
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#cbd5e1',
                        padding: 10
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

/**
 * Create threat distribution pie chart
 */
function createThreatDistributionChart(elementId, data) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',   // Safe - Green
                    'rgba(245, 158, 11, 0.8)',   // Warning - Yellow
                    'rgba(239, 68, 68, 0.8)',    // Danger - Red
                    'rgba(220, 38, 38, 0.8)'     // Critical - Dark Red
                ],
                borderColor: [
                    '#10b981',
                    '#f59e0b',
                    '#ef4444',
                    '#dc2626'
                ],
                borderWidth: 2,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'right',
                    labels: {
                        color: '#cbd5e1',
                        padding: 15,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.95)',
                    titleColor: '#f8fafc',
                    bodyColor: '#cbd5e1',
                    borderColor: 'rgba(59, 130, 246, 0.5)',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create hourly activity heatmap (bar chart)
 */
function createHourlyActivityChart(elementId, data) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.hour + ':00'),
            datasets: [{
                label: 'Detections',
                data: data.map(d => d.count),
                backgroundColor: 'rgba(59, 130, 246, 0.8)',
                borderColor: '#3b82f6',
                borderWidth: 1,
                borderRadius: 6,
                hoverBackgroundColor: 'rgba(59, 130, 246, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.95)',
                    titleColor: '#f8fafc',
                    bodyColor: '#cbd5e1',
                    borderColor: 'rgba(59, 130, 246, 0.5)',
                    borderWidth: 1,
                    padding: 12
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(59, 130, 246, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#cbd5e1',
                        padding: 10
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#cbd5e1',
                        padding: 10
                    }
                }
            }
        }
    });
}

/**
 * Create model performance comparison chart
 */
function createModelPerformanceChart(elementId, data) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'Speed'],
            datasets: data.models.map((model, index) => ({
                label: model.name,
                data: [
                    model.accuracy * 100,
                    model.precision * 100,
                    model.recall * 100,
                    model.f1_score * 100,
                    model.speed
                ],
                borderColor: ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'][index % 4],
                backgroundColor: [
                    'rgba(59, 130, 246, 0.2)',
                    'rgba(139, 92, 246, 0.2)',
                    'rgba(16, 185, 129, 0.2)',
                    'rgba(245, 158, 11, 0.2)'
                ][index % 4],
                borderWidth: 2,
                pointBackgroundColor: ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'][index % 4],
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'][index % 4]
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#cbd5e1',
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.95)',
                    titleColor: '#f8fafc',
                    bodyColor: '#cbd5e1',
                    borderColor: 'rgba(59, 130, 246, 0.5)',
                    borderWidth: 1,
                    padding: 12
                }
            },
            scales: {
                r: {
                    angleLines: {
                        color: 'rgba(59, 130, 246, 0.2)'
                    },
                    grid: {
                        color: 'rgba(59, 130, 246, 0.2)'
                    },
                    pointLabels: {
                        color: '#cbd5e1',
                        font: {
                            size: 12
                        }
                    },
                    ticks: {
                        color: '#cbd5e1',
                        backdropColor: 'transparent'
                    }
                }
            }
        }
    });
}

/**
 * Create feature importance chart
 */
function createFeatureImportanceChart(elementId, data) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.feature),
            datasets: [{
                label: 'Importance',
                data: data.map(d => d.importance),
                backgroundColor: data.map(d => {
                    if (d.importance > 0.3) return 'rgba(239, 68, 68, 0.8)';
                    if (d.importance > 0.2) return 'rgba(245, 158, 11, 0.8)';
                    return 'rgba(59, 130, 246, 0.8)';
                }),
                borderWidth: 0,
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.95)',
                    titleColor: '#f8fafc',
                    bodyColor: '#cbd5e1',
                    borderColor: 'rgba(59, 130, 246, 0.5)',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            return 'Importance: ' + (context.parsed.x * 100).toFixed(1) + '%';
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 1,
                    grid: {
                        color: 'rgba(59, 130, 246, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#cbd5e1',
                        padding: 10,
                        callback: function(value) {
                            return (value * 100) + '%';
                        }
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#cbd5e1',
                        padding: 10
                    }
                }
            }
        }
    });
}

/**
 * Update existing chart with new data
 */
function updateChart(chart, newData) {
    if (!chart) return;
    
    chart.data.labels = newData.labels;
    chart.data.datasets.forEach((dataset, i) => {
        dataset.data = newData.datasets[i].data;
    });
    chart.update('active');
}

/**
 * Destroy chart instance
 */
function destroyChart(chart) {
    if (chart) {
        chart.destroy();
    }
}

// Export functions for use in other scripts
window.chartUtils = {
    createDetectionTrendChart,
    createThreatDistributionChart,
    createHourlyActivityChart,
    createModelPerformanceChart,
    createFeatureImportanceChart,
    updateChart,
    destroyChart
};

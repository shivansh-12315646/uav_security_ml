/* ═══════════════════════════════════════════════════════════════════
   Global Chart.js Configuration — Premium Defaults
   ═══════════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', function() {
    if (typeof Chart === 'undefined') return;

    // Set premium defaults for ALL charts
    Chart.defaults.font.family = "'Inter', -apple-system, sans-serif";
    Chart.defaults.font.weight = 600; // Increased weight for better readability
    Chart.defaults.font.size = 13; // Base size slightly larger
    Chart.defaults.animation.duration = 1000;
    Chart.defaults.animation.easing = 'easeOutExpo'; // Smoother animation
    Chart.defaults.responsive = true;
    Chart.defaults.maintainAspectRatio = true;
    
    // Elements styling for better readability
    Chart.defaults.elements.line.borderWidth = 3;
    Chart.defaults.elements.line.tension = 0.4; // Smooth curves
    Chart.defaults.elements.point.radius = 4;
    Chart.defaults.elements.point.hoverRadius = 6;
    Chart.defaults.elements.bar.borderRadius = 6;
    Chart.defaults.elements.arc.borderWidth = 0; // Remove border on pies for cleaner look

    // Apply initial theme colors
    const applyInitialColors = () => {
        if (typeof window.UAVTheme !== 'undefined') {
            const t = window.UAVTheme.getChartColors();
            Chart.defaults.color = t.chartText;
            Chart.defaults.borderColor = t.chartBorder;
        } else {
            const theme = document.body.getAttribute('data-bs-theme') || 'dark';
            if (theme === 'dark') {
                Chart.defaults.color = '#f8fafc';
                Chart.defaults.borderColor = 'rgba(99,102,241,0.2)';
            } else {
                Chart.defaults.color = '#1e293b';
                Chart.defaults.borderColor = 'rgba(0,0,0,0.1)';
            }
        }
    };
    applyInitialColors();

    // Accuracy comparison chart (only on pages with this canvas)
    const ctx = document.getElementById('accuracyChart');
    if (ctx) {
        // Get the dynamic palette
        const palette = window.UAVTheme ? window.UAVTheme.getPalette() : ['#6366f1', '#06b6d4', '#10b981', '#f59e0b'];
        
        // Create premium 3D-like gradients
        const gradients = palette.slice(0, 4).map(c => {
            const g = ctx.getContext('2d').createLinearGradient(0, 0, 0, 350);
            g.addColorStop(0, c);
            g.addColorStop(0.7, c + '88'); // More solid mid
            g.addColorStop(1, c + '11'); // Fade to transparent
            return g;
        });

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Rule-Based', 'LogReg', 'SVM', 'Random Forest'],
                datasets: [{
                    label: 'Accuracy (%)',
                    data: [78, 90, 93, 96],
                    backgroundColor: gradients,
                    borderColor: palette.slice(0, 4),
                    borderWidth: { top: 2, right: 0, bottom: 0, left: 0 },
                    borderRadius: 8,
                    borderSkipped: false,
                    hoverBackgroundColor: palette.slice(0, 4), // Solid color on hover
                }]
            },
            options: {
                responsive: true,
                plugins: { 
                    legend: { 
                        display: false // Hide legend for single dataset if obvious
                    },
                    tooltip: {
                        padding: 12,
                        titleFont: { size: 14, weight: 700 },
                        bodyFont: { size: 13, weight: 500 }
                    }
                },
                scales: {
                    y: { 
                        beginAtZero: true, 
                        max: 100, 
                        ticks: { font: { size: 13, weight: 600 } }, 
                        grid: { color: Chart.defaults.borderColor, drawBorder: false } 
                    },
                    x: { 
                        ticks: { font: { size: 13, weight: 700 } }, 
                        grid: { display: false } 
                    }
                }
            }
        });
    }
});

/* ═══════════════════════════════════════════════════════════════════
   Theme Toggle — Dark ⇄ Light with Chart.js color sync
   ═══════════════════════════════════════════════════════════════════ */
(function() {
    'use strict';

    const THEMES = {
        dark: {
            chartText: '#f8fafc', /* Much brighter for readability */
            chartGrid: 'rgba(99,102,241,0.15)',
            chartBorder: 'rgba(99,102,241,0.3)',
            tooltipBg: 'rgba(15,23,42,0.95)',
            tooltipTitle: '#ffffff',
            tooltipBody: '#e2e8f0',
            icon: 'fas fa-sun',
            /* Premium Dark Palette: Neon and highly saturated */
            palette: ['#818cf8', '#22d3ee', '#fbbf24', '#f472b6', '#34d399', '#a78bfa', '#fb923c', '#2dd4bf']
        },
        light: {
            chartText: '#1e293b', /* Much darker for readability */
            chartGrid: 'rgba(0,0,0,0.08)',
            chartBorder: 'rgba(0,0,0,0.15)',
            tooltipBg: 'rgba(255,255,255,0.95)',
            tooltipTitle: '#0f172a',
            tooltipBody: '#334155',
            icon: 'fas fa-moon',
            /* Premium Light Palette: Deep and distinct */
            palette: ['#4338ca', '#0891b2', '#d97706', '#be185d', '#059669', '#6d28d9', '#c2410c', '#0f766e']
        }
    };

    const getStored = () => localStorage.getItem('theme');
    const setStored = t => localStorage.setItem('theme', t);

    const getPreferred = () => {
        const s = getStored();
        if (s) return s;
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };

    function applyTheme(theme) {
        document.body.setAttribute('data-bs-theme', theme);

        // Update toggle icon
        const icon = document.querySelector('#themeToggle i');
        if (icon) icon.className = THEMES[theme].icon;

        // Update Chart.js defaults globally
        if (typeof Chart !== 'undefined') {
            const t = THEMES[theme];
            Chart.defaults.color = t.chartText;
            Chart.defaults.borderColor = t.chartBorder;
            Chart.defaults.plugins.legend.labels.color = t.chartText;

            // Update tooltips if configured globally
            if (Chart.defaults.plugins.tooltip) {
                Chart.defaults.plugins.tooltip.backgroundColor = t.tooltipBg;
                Chart.defaults.plugins.tooltip.titleColor = t.tooltipTitle;
                Chart.defaults.plugins.tooltip.bodyColor = t.tooltipBody;
            }

            // Re-render all active charts
            Object.values(Chart.instances || {}).forEach(chart => {
                if (chart.options?.scales?.x) {
                    chart.options.scales.x.ticks.color = t.chartText;
                    chart.options.scales.x.grid.color = t.chartGrid;
                }
                if (chart.options?.scales?.y) {
                    chart.options.scales.y.ticks.color = t.chartText;
                    chart.options.scales.y.grid.color = t.chartGrid;
                }
                if (chart.options?.scales?.r) {
                    chart.options.scales.r.ticks.color = t.chartText;
                    chart.options.scales.r.grid.color = t.chartGrid;
                    chart.options.scales.r.pointLabels.color = t.chartText;
                    chart.options.scales.r.ticks.backdropColor = 'transparent';
                }
                if (chart.options?.plugins?.tooltip) {
                    chart.options.plugins.tooltip.backgroundColor = t.tooltipBg;
                    chart.options.plugins.tooltip.titleColor = t.tooltipTitle;
                    chart.options.plugins.tooltip.bodyColor = t.tooltipBody;
                }
                if (chart.options?.plugins?.legend?.labels) {
                    chart.options.plugins.legend.labels.color = t.chartText;
                }
                chart.update('none');
            });
        }
    }

    // Apply on page load (before DOMContentLoaded for flash prevention)
    applyTheme(getPreferred());

    document.addEventListener('DOMContentLoaded', () => {
        const btn = document.getElementById('themeToggle');
        if (btn) {
            btn.addEventListener('click', () => {
                const cur = document.body.getAttribute('data-bs-theme');
                const next = cur === 'light' ? 'dark' : 'light';
                setStored(next);
                applyTheme(next);
            });
        }

        // Re-apply after Chart.js loads (for initial page)
        setTimeout(() => applyTheme(getPreferred()), 500);
    });

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        if (!getStored()) applyTheme(getPreferred());
    });

    // Export for use in other scripts
    window.UAVTheme = {
        getCurrent: () => document.body.getAttribute('data-bs-theme') || 'dark',
        getChartColors: () => THEMES[document.body.getAttribute('data-bs-theme') || 'dark'],
        getPalette: () => {
            const current = document.body.getAttribute('data-bs-theme') || 'dark';
            return THEMES[current].palette;
        },
    };
})();

/**
 * Dashboard JavaScript - Enterprise-grade interactivity
 * Handles animations, charts, and real-time updates
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS (Animate On Scroll)
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-out-cubic',
            once: true,
            offset: 50
        });
    }

    // Initialize Particles.js if available
    if (typeof particlesJS !== 'undefined' && document.getElementById('particles-js')) {
        particlesJS('particles-js', {
            particles: {
                number: { value: 60, density: { enable: true, value_area: 800 } },
                color: { value: '#818cf8' },
                shape: { type: 'circle' },
                opacity: { value: 0.4, random: true },
                size: { value: 3, random: true },
                line_linked: { enable: true, distance: 150, color: '#818cf8', opacity: 0.3, width: 1 },
                move: { enable: true, speed: 1.5, direction: 'none', random: true, straight: false, out_mode: 'out', bounce: false }
            },
            interactivity: {
                detect_on: 'canvas',
                events: { onhover: { enable: true, mode: 'grab' }, onclick: { enable: true, mode: 'push' }, resize: true },
                modes: { grab: { distance: 140, line_linked: { opacity: 0.6 } }, push: { particles_nb: 3 } }
            },
            retina_detect: true
        });
    }

    // Advanced stagger entrance for dashboard cards
    staggerCardsEntrance();

    // Animate metric cards on page load
    animateMetricCards();

    // Add active class to current nav link
    highlightActiveNavLink();

    // Initialize scroll to top button
    initScrollToTop();

    // Add hover effects to cards
    enhanceCardHoverEffects();

    // Initialize tooltips
    initializeTooltips();
});

/**
 * Advanced stagger entrance for cards
 */
function staggerCardsEntrance() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
            
            // Remove inline transition after animation completes so hover effects work
            setTimeout(() => {
                card.style.transition = '';
            }, 600);
        }, 100 + (index * 80)); // 80ms stagger delay
    });
}

/**
 * Animate metric cards with smooth easeOutExpo counting effect
 */
function animateMetricCards() {
    const metricNumbers = document.querySelectorAll('.metric-card h2, .metric-card h3');
    
    // easeOutExpo function
    const easeOutExpo = (x) => x === 1 ? 1 : 1 - Math.pow(2, -10 * x);

    metricNumbers.forEach(element => {
        const text = element.textContent;
        const number = parseFloat(text.replace(/[^0-9.]/g, ''));
        
        if (isNaN(number) || number === 0) return;
        
        const duration = 2000; // 2 seconds
        const fps = 60;
        const frames = (duration / 1000) * fps;
        let frame = 0;
        
        const suffix = text.replace(/[0-9.]/g, '');
        const isDecimal = text.includes('.');

        const timer = setInterval(() => {
            frame++;
            const progress = easeOutExpo(frame / frames);
            const current = number * progress;
            
            if (frame >= frames) {
                element.textContent = text; // Ensure exact final text
                clearInterval(timer);
            } else {
                if (isDecimal || suffix.includes('%')) {
                    element.textContent = current.toFixed(1) + suffix;
                } else {
                    element.textContent = Math.floor(current) + suffix;
                }
            }
        }, 1000 / fps);
    });
}

/**
 * Highlight active navigation link
 */
function highlightActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '/') {
            link.classList.add('active');
        } else if (href === '/' && currentPath === '/') {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

/**
 * Initialize scroll to top button
 */
function initScrollToTop() {
    // Create scroll to top button if it doesn't exist
    if (!document.querySelector('.scroll-to-top')) {
        const scrollBtn = document.createElement('div');
        scrollBtn.className = 'scroll-to-top';
        scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
        scrollBtn.title = 'Back to Top';
        document.body.appendChild(scrollBtn);
        
        scrollBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    const scrollBtn = document.querySelector('.scroll-to-top');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            scrollBtn.classList.add('visible');
        } else {
            scrollBtn.classList.remove('visible');
        }
    });
}

/**
 * Enhance card hover effects
 */
function enhanceCardHoverEffects() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 3000) {
    // Check if Toastify is available
    if (typeof Toastify !== 'undefined') {
        const bgColors = {
            'success': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            'danger': 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
            'warning': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
            'info': 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)'
        };
        
        Toastify({
            text: message,
            duration: duration,
            gravity: 'top',
            position: 'right',
            stopOnFocus: true,
            style: {
                background: bgColors[type] || bgColors['info'],
                borderRadius: '12px',
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)'
            }
        }).showToast();
    } else {
        // Fallback to alert
        alert(message);
    }
}

/**
 * Create circular progress bar
 */
function createCircularProgress(element, percentage) {
    element.style.setProperty('--progress', percentage + '%');
    
    const textElement = element.querySelector('.circular-progress-text');
    if (textElement) {
        let current = 0;
        const step = percentage / 30;
        const timer = setInterval(() => {
            current += step;
            if (current >= percentage) {
                current = percentage;
                clearInterval(timer);
            }
            textElement.textContent = Math.round(current) + '%';
        }, 30);
    }
}

/**
 * Animate confidence meter
 */
function animateConfidenceMeter(element, confidence) {
    const fill = element.querySelector('.confidence-meter-fill');
    if (fill) {
        setTimeout(() => {
            fill.style.width = (confidence * 100) + '%';
        }, 100);
    }
}

/**
 * Format threat level with appropriate styling
 */
function getThreatLevelBadge(level) {
    const badges = {
        'Critical': '<span class="badge bg-danger badge-glow pulse-danger">Critical</span>',
        'High': '<span class="badge bg-warning badge-glow pulse-warning">High</span>',
        'Medium': '<span class="badge bg-info">Medium</span>',
        'Low': '<span class="badge bg-secondary">Low</span>'
    };
    return badges[level] || badges['Low'];
}

/**
 * Auto-refresh dashboard data
 */
function startAutoRefresh(interval = 30000) {
    setInterval(() => {
        // Fetch updated metrics from API
        fetch('/api/dashboard/metrics')
            .then(response => response.json())
            .then(data => {
                updateDashboardMetrics(data);
            })
            .catch(error => {
                console.error('Error fetching dashboard metrics:', error);
            });
    }, interval);
}

/**
 * Update dashboard metrics
 */
function updateDashboardMetrics(data) {
    // Update metric cards
    if (data.total_detections !== undefined) {
        const element = document.querySelector('.metric-card.total-detections h2');
        if (element) {
            element.textContent = data.total_detections;
        }
    }
    
    if (data.active_alerts !== undefined) {
        const element = document.querySelector('.metric-card.active-alerts h2');
        if (element) {
            element.textContent = data.active_alerts;
        }
    }
    
    // Update notification badge
    if (data.active_alerts > 0) {
        updateNotificationBadge(data.active_alerts);
    }
}

/**
 * Update notification badge
 */
function updateNotificationBadge(count) {
    const badge = document.querySelector('.navbar .badge');
    if (badge) {
        badge.textContent = count;
        if (count > 0) {
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    }
}

/**
 * Loading spinner utility
 */
function showLoading(element) {
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    spinner.style.margin = '40px auto';
    element.innerHTML = '';
    element.appendChild(spinner);
}

/**
 * Show skeleton loader
 */
function showSkeleton(element, lines = 3) {
    element.innerHTML = '';
    for (let i = 0; i < lines; i++) {
        const skeleton = document.createElement('div');
        skeleton.className = 'skeleton skeleton-text';
        element.appendChild(skeleton);
    }
}

/**
 * Debounce function for performance
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for use in other scripts
window.dashboardUtils = {
    showToast,
    createCircularProgress,
    animateConfidenceMeter,
    getThreatLevelBadge,
    showLoading,
    showSkeleton,
    debounce
};

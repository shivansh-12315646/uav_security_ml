/**
 * Real-time Updates - WebSocket handling with Flask-SocketIO
 * Handles live monitoring and real-time data updates
 */

let socket = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

/**
 * Initialize Socket.IO connection
 */
function initializeSocket() {
    if (typeof io === 'undefined') {
        console.warn('Socket.IO not loaded. Real-time features disabled.');
        return;
    }

    socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port, {
        transports: ['websocket', 'polling'],
        upgrade: true,
        rememberUpgrade: true
    });

    // Connection established
    socket.on('connect', function() {
        console.log('✅ Socket.IO connected');
        reconnectAttempts = 0;
        updateConnectionStatus(true);
        
        // Join monitoring room if on monitoring page
        if (window.location.pathname.includes('monitoring')) {
            socket.emit('join_monitoring');
        }
    });

    // Connection lost
    socket.on('disconnect', function() {
        console.log('❌ Socket.IO disconnected');
        updateConnectionStatus(false);
        attemptReconnect();
    });

    // Connection error
    socket.on('connect_error', function(error) {
        console.error('Socket.IO connection error:', error);
        updateConnectionStatus(false);
    });

    // Listen for new detections
    socket.on('new_detection', function(data) {
        handleNewDetection(data);
    });

    // Listen for new alerts
    socket.on('new_alert', function(data) {
        handleNewAlert(data);
    });

    // Listen for system metrics updates
    socket.on('system_metrics', function(data) {
        handleSystemMetrics(data);
    });

    // Listen for detection updates
    socket.on('detection_update', function(data) {
        handleDetectionUpdate(data);
    });
}

/**
 * Attempt to reconnect to socket
 */
function attemptReconnect() {
    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
        console.log(`Attempting to reconnect in ${delay/1000}s... (Attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
        
        setTimeout(() => {
            if (socket && !socket.connected) {
                socket.connect();
            }
        }, delay);
    } else {
        console.error('Max reconnection attempts reached');
        if (window.dashboardUtils) {
            window.dashboardUtils.showToast('Connection lost. Please refresh the page.', 'danger', 0);
        }
    }
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(isConnected) {
    const indicator = document.getElementById('connection-status');
    if (indicator) {
        if (isConnected) {
            indicator.innerHTML = '<i class="fas fa-circle text-success"></i> Connected';
            indicator.className = 'badge bg-success';
        } else {
            indicator.innerHTML = '<i class="fas fa-circle text-danger"></i> Disconnected';
            indicator.className = 'badge bg-danger';
        }
    }
}

/**
 * Handle new detection event
 */
function handleNewDetection(data) {
    console.log('New detection:', data);
    
    // Update detection counter
    updateDetectionCounter();
    
    // Add to live feed if on dashboard
    if (window.location.pathname.includes('dashboard')) {
        addToLiveFeed(data);
    }
    
    // Show notification for threats
    if (data.prediction === 'Threat') {
        showThreatNotification(data);
    }
    
    // Update charts
    if (typeof updateDashboardCharts === 'function') {
        updateDashboardCharts();
    }
}

/**
 * Handle new alert event
 */
function handleNewAlert(data) {
    console.log('New alert:', data);
    
    // Update alert counter in navbar
    updateAlertBadge();
    
    // Show notification
    if (window.dashboardUtils) {
        const severity = data.severity || 'Medium';
        const type = severity === 'Critical' ? 'danger' : 'warning';
        window.dashboardUtils.showToast(`New ${severity} Alert!`, type);
    }
    
    // Play alert sound for critical alerts
    if (data.severity === 'Critical') {
        playAlertSound();
    }
    
    // Add to alerts list if on alerts page
    if (window.location.pathname.includes('alerts')) {
        prependAlertToList(data);
    }
}

/**
 * Handle system metrics update
 */
function handleSystemMetrics(data) {
    // Update CPU usage
    const cpuElement = document.getElementById('cpu-usage');
    if (cpuElement) {
        cpuElement.textContent = data.cpu + '%';
        updateMetricBar('cpu-bar', data.cpu);
    }
    
    // Update memory usage
    const memoryElement = document.getElementById('memory-usage');
    if (memoryElement) {
        memoryElement.textContent = data.memory + '%';
        updateMetricBar('memory-bar', data.memory);
    }
    
    // Update detection rate
    const rateElement = document.getElementById('detection-rate');
    if (rateElement) {
        rateElement.textContent = data.detection_rate + '/min';
    }
}

/**
 * Handle detection update event
 */
function handleDetectionUpdate(data) {
    // Update detection row if visible
    const row = document.querySelector(`tr[data-detection-id="${data.id}"]`);
    if (row) {
        // Update row data
        row.querySelector('.detection-status').textContent = data.status;
    }
}

/**
 * Add detection to live feed
 */
function addToLiveFeed(detection) {
    const feed = document.getElementById('live-detection-feed');
    if (!feed) return;
    
    const item = document.createElement('div');
    item.className = 'live-feed-item';
    item.style.animation = 'slideInRight 0.5s ease-out';
    
    const threatClass = detection.prediction === 'Threat' ? 'danger' : 'success';
    const icon = detection.prediction === 'Threat' ? 'exclamation-triangle' : 'check-circle';
    
    item.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${icon} text-${threatClass} me-2"></i>
            <div class="flex-grow-1">
                <strong>${detection.prediction}</strong>
                <small class="text-muted d-block">Confidence: ${(detection.confidence * 100).toFixed(1)}%</small>
            </div>
            <small class="text-muted">${new Date().toLocaleTimeString()}</small>
        </div>
    `;
    
    // Add to top of feed
    feed.insertBefore(item, feed.firstChild);
    
    // Keep only last 10 items
    while (feed.children.length > 10) {
        feed.removeChild(feed.lastChild);
    }
}

/**
 * Show threat notification
 */
function showThreatNotification(data) {
    if (window.dashboardUtils) {
        const message = `Threat Detected! Confidence: ${(data.confidence * 100).toFixed(1)}%`;
        window.dashboardUtils.showToast(message, 'danger', 5000);
    }
    
    // Update browser notification if permitted
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('UAV Security Alert', {
            body: `Threat detected with ${(data.confidence * 100).toFixed(1)}% confidence`,
            icon: '/static/img/alert-icon.png',
            badge: '/static/img/badge-icon.png',
            tag: 'threat-detection'
        });
    }
}

/**
 * Update detection counter
 */
function updateDetectionCounter() {
    const counter = document.querySelector('.metric-card.total-detections h2');
    if (counter) {
        const current = parseInt(counter.textContent) || 0;
        counter.textContent = current + 1;
    }
}

/**
 * Update alert badge in navbar
 */
function updateAlertBadge() {
    const badge = document.querySelector('.navbar .fa-bell + .badge');
    if (badge) {
        const current = parseInt(badge.textContent) || 0;
        badge.textContent = current + 1;
        badge.style.display = 'inline-block';
    }
}

/**
 * Update metric bar (progress bar)
 */
function updateMetricBar(barId, percentage) {
    const bar = document.getElementById(barId);
    if (bar) {
        bar.style.width = percentage + '%';
        bar.setAttribute('aria-valuenow', percentage);
        
        // Change color based on percentage
        bar.className = 'progress-bar';
        if (percentage > 80) {
            bar.classList.add('bg-danger');
        } else if (percentage > 60) {
            bar.classList.add('bg-warning');
        } else {
            bar.classList.add('bg-success');
        }
    }
}

/**
 * Play alert sound
 */
function playAlertSound() {
    const audio = new Audio('/static/sounds/alert.mp3');
    audio.volume = 0.5;
    audio.play().catch(error => {
        console.log('Could not play alert sound:', error);
    });
}

/**
 * Prepend alert to alerts list
 */
function prependAlertToList(alert) {
    const table = document.querySelector('.table tbody');
    if (!table) return;
    
    const row = document.createElement('tr');
    row.className = 'new-alert-row';
    row.style.animation = 'slideInRight 0.5s ease-out';
    
    const severityBadge = alert.severity === 'Critical' 
        ? '<span class="badge bg-danger">Critical</span>'
        : '<span class="badge bg-warning">High</span>';
    
    row.innerHTML = `
        <td>#${alert.id}</td>
        <td>${severityBadge}</td>
        <td><span class="badge bg-warning">Open</span></td>
        <td>${new Date().toLocaleString()}</td>
        <td><a href="#">#${alert.detection_id}</a></td>
        <td>
            <button class="btn btn-sm btn-warning">Acknowledge</button>
            <button class="btn btn-sm btn-success">Resolve</button>
        </td>
    `;
    
    table.insertBefore(row, table.firstChild);
}

/**
 * Request browser notification permission
 */
function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission().then(function(permission) {
            if (permission === 'granted') {
                console.log('Notification permission granted');
                if (window.dashboardUtils) {
                    window.dashboardUtils.showToast('Notifications enabled', 'success');
                }
            }
        });
    }
}

/**
 * Emit custom event to server
 */
function emitEvent(eventName, data) {
    if (socket && socket.connected) {
        socket.emit(eventName, data);
    } else {
        console.warn('Socket not connected. Cannot emit event:', eventName);
    }
}

// Initialize socket when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    
    // Request notification permission after a delay
    setTimeout(requestNotificationPermission, 5000);
});

// Export functions for use in other scripts
window.realtimeUtils = {
    initializeSocket,
    emitEvent,
    socket: () => socket
};

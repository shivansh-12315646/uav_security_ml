// Main JavaScript for UAV Security ML Application

$(document).ready(function() {
    // Sidebar toggle for mobile
    $('#sidebarToggle').on('click', function() {
        $('.sidebar').toggleClass('show');
    });
    
    // Close sidebar when clicking outside on mobile
    $(document).on('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!$(e.target).closest('.sidebar, #sidebarToggle').length) {
                $('.sidebar').removeClass('show');
            }
        }
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);
    
    // Add active class to current nav link
    const currentPath = window.location.pathname;
    $('.sidebar-nav .nav-link').each(function() {
        if ($(this).attr('href') === currentPath) {
            $(this).addClass('active');
        }
    });
    
    // Smooth scroll to top
    $('a[href="#top"]').on('click', function(e) {
        e.preventDefault();
        $('html, body').animate({ scrollTop: 0 }, 'smooth');
    });
    
    // Initialize tooltips if Bootstrap 5 tooltips are used
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers if Bootstrap 5 popovers are used
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Add loading state to buttons on form submit
    $('form').on('submit', function() {
        const submitBtn = $(this).find('button[type="submit"]');
        const originalText = submitBtn.html();
        submitBtn.prop('disabled', true);
        submitBtn.html('<span class="spinner-border spinner-border-sm me-2"></span>Processing...');
        
        // Re-enable after 3 seconds (fallback)
        setTimeout(function() {
            submitBtn.prop('disabled', false);
            submitBtn.html(originalText);
        }, 3000);
    });
});

// Format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Format percentage
function formatPercentage(num, decimals = 1) {
    return num.toFixed(decimals) + '%';
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastHTML = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    const toastContainer = $('#toastContainer');
    if (toastContainer.length === 0) {
        $('body').append('<div id="toastContainer" class="toast-container position-fixed bottom-0 end-0 p-3"></div>');
    }
    
    $('#toastContainer').append(toastHTML);
    const toastEl = $('#toastContainer .toast').last();
    const toast = new bootstrap.Toast(toastEl[0]);
    toast.show();
    
    // Remove toast element after it's hidden
    toastEl.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

// Confirm dialog helper
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// AJAX helper for API calls
function apiCall(url, method = 'GET', data = null) {
    return $.ajax({
        url: url,
        method: method,
        data: data ? JSON.stringify(data) : null,
        contentType: 'application/json',
        dataType: 'json'
    });
}

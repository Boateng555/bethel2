// LocalHero Admin JavaScript
document.addEventListener('DOMContentLoaded', function() {
    
    // Add "Send for Approval" button to change form
    function addSendApprovalButton() {
        const submitRow = document.querySelector('.submit-row');
        if (submitRow && !document.getElementById('send-approval-btn')) {
            const sendApprovalBtn = document.createElement('input');
            sendApprovalBtn.type = 'button';
            sendApprovalBtn.value = 'Send for Approval';
            sendApprovalBtn.id = 'send-approval-btn';
            sendApprovalBtn.className = 'btn btn-warning';
            sendApprovalBtn.style.marginRight = '10px';
            
            sendApprovalBtn.addEventListener('click', function() {
                sendForApproval();
            });
            
            submitRow.insertBefore(sendApprovalBtn, submitRow.firstChild);
        }
    }
    
    // Send for approval function
    function sendForApproval(heroId = null) {
        // Get hero ID from URL if not provided
        if (!heroId) {
            const urlParts = window.location.pathname.split('/');
            const heroIndex = urlParts.indexOf('localhero') + 2;
            if (urlParts[heroIndex] && urlParts[heroIndex] !== 'add') {
                heroId = urlParts[heroIndex];
            } else {
                showNotification('Error: Could not determine hero ID', 'error');
                return;
            }
        }
        
        // Show loading state
        const btn = document.getElementById('send-approval-btn') || event.target;
        const originalText = btn.value || btn.textContent;
        btn.value = btn.textContent = 'Sending...';
        btn.disabled = true;
        
        // Make AJAX request
        fetch(`/admin/core/localhero/${heroId}/send-approval/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                // Update the form if we're on the change form
                const statusField = document.getElementById('id_global_feature_status');
                if (statusField) {
                    statusField.value = 'pending';
                }
                const featuredField = document.getElementById('id_is_global_featured');
                if (featuredField) {
                    featuredField.checked = true;
                }
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            showNotification('Error sending request: ' + error.message, 'error');
        })
        .finally(() => {
            // Restore button state
            btn.value = btn.textContent = originalText;
            btn.disabled = false;
        });
    }
    
    // Show notification popup
    function showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.admin-notification');
        existingNotifications.forEach(notification => notification.remove());
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `admin-notification admin-notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 9999;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideIn 0.3s ease-out;
        `;
        
        // Set background color based on type
        switch(type) {
            case 'success':
                notification.style.backgroundColor = '#28a745';
                break;
            case 'error':
                notification.style.backgroundColor = '#dc3545';
                break;
            case 'warning':
                notification.style.backgroundColor = '#ffc107';
                notification.style.color = '#212529';
                break;
            default:
                notification.style.backgroundColor = '#17a2b8';
        }
        
        notification.textContent = message;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 5000);
        
        // Add click to dismiss
        notification.addEventListener('click', () => {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        });
    }
    
    // Get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        .admin-notification {
            cursor: pointer;
        }
        
        .admin-notification:hover {
            opacity: 0.9;
        }
    `;
    document.head.appendChild(style);
    
    // Initialize based on current page
    if (window.location.pathname.includes('/add/')) {
        // On add form, don't add the button yet
    } else if (window.location.pathname.includes('/change/')) {
        // On change form, add the button
        addSendApprovalButton();
    }
}); 
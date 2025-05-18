document.addEventListener('DOMContentLoaded', function() {
    // Initialize Select2 for all select elements with select2 class
    if (typeof $.fn.select2 !== 'undefined') {
        $('.select2').select2({
            theme: 'bootstrap-5',
            width: '100%'
        });
    }

    // Auto-expand textareas
    document.querySelectorAll('textarea.auto-expand').forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });

    // Handle file input display
    document.querySelectorAll('input[type="file"]').forEach(input => {
        input.addEventListener('change', function() {
            let fileList = '';
            for (let i = 0; i < this.files.length; i++) {
                fileList += `<li>${this.files[i].name} (${formatFileSize(this.files[i].size)})</li>`;
            }
            
            const fileDisplay = this.nextElementSibling;
            if (fileDisplay && fileDisplay.classList.contains('file-display')) {
                fileDisplay.innerHTML = fileList ? `<ul>${fileList}</ul>` : '';
            } else {
                const div = document.createElement('div');
                div.className = 'file-display mt-2';
                div.innerHTML = fileList ? `<ul>${fileList}</ul>` : '';
                this.parentNode.insertBefore(div, this.nextSibling);
            }
        });
    });

    // Handle message sending via AJAX
    const messageForm = document.querySelector('form[action*="send_message"]');
    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitButton = this.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Sending...';

            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Clear form
                    this.reset();
                    const fileDisplays = this.querySelectorAll('.file-display');
                    fileDisplays.forEach(display => display.remove());
                    
                    // Reload messages
                    location.reload();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to send message. Please try again.');
            })
            .finally(() => {
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            });
        });
    }

    // Auto-scroll messages container to bottom
    const messagesContainer = document.querySelector('.messages-container');
    if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Handle new message scroll
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length) {
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }
            });
        });

        observer.observe(messagesContainer, { childList: true, subtree: true });
    }

    // Handle announcement read marking
    document.querySelectorAll('.mark-read').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const announcementId = this.dataset.announcementId;
            const card = this.closest('.card');
            
            fetch(`/messaging/announcements/${announcementId}/read/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Update UI
                    card.classList.remove('border-primary');
                    this.closest('.card-footer').querySelector('.mark-read').remove();
                    card.querySelector('.badge.bg-primary')?.remove();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to mark announcement as read. Please try again.');
            });
        });
    });
});

// Utility function to format file sizes
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Handle real-time message updates (if WebSocket is available)
if (typeof WebSocket !== 'undefined' && window.messageWebSocketUrl) {
    const ws = new WebSocket(window.messageWebSocketUrl);
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        if (data.type === 'new_message' && data.thread_id === window.currentThreadId) {
            // Append new message to the container
            const messagesContainer = document.querySelector('.messages-container');
            if (messagesContainer) {
                const messageHtml = createMessageElement(data.message);
                messagesContainer.insertAdjacentHTML('beforeend', messageHtml);
            }
        } else if (data.type === 'new_announcement') {
            // Show notification for new announcement
            showNotification('New Announcement', data.title);
        }
    };
    
    ws.onclose = function() {
        console.log('WebSocket connection closed');
        // Attempt to reconnect after 5 seconds
        setTimeout(() => {
            window.location.reload();
        }, 5000);
    };
}

// Create message element HTML
function createMessageElement(message) {
    const isCurrentUser = message.sender.id === window.currentUserId;
    const messageClass = isCurrentUser ? 'message-sent' : 'message-received';
    
    let attachmentsHtml = '';
    if (message.attachments && message.attachments.length > 0) {
        attachmentsHtml = `
            <div class="message-attachments mt-2">
                <small class="text-muted">Attachments:</small>
                <ul class="list-unstyled ms-3 mb-0">
                    ${message.attachments.map(att => `
                        <li>
                            <i class="bi bi-paperclip"></i>
                            <a href="${att.url}" target="_blank">
                                ${att.filename}
                            </a>
                            <small class="text-muted">(${formatFileSize(att.file_size)})</small>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    }
    
    return `
        <div class="message ${messageClass} mb-3">
            <div class="message-header d-flex justify-content-between align-items-center mb-2">
                <div>
                    <strong>${message.sender.name}</strong>
                    ${isCurrentUser ? '(you)' : ''}
                </div>
                <small class="text-muted">${message.sent_at}</small>
            </div>
            <div class="message-body">
                ${message.body}
            </div>
            ${attachmentsHtml}
        </div>
    `;
}

// Show browser notification
function showNotification(title, body) {
    if (!("Notification" in window)) {
        return;
    }
    
    if (Notification.permission === "granted") {
        new Notification(title, { body: body });
    } else if (Notification.permission !== "denied") {
        Notification.requestPermission().then(permission => {
            if (permission === "granted") {
                new Notification(title, { body: body });
            }
        });
    }
} 
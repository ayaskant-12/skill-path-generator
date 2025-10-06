// Main JavaScript for Skill Path Generator

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    initializeProgressRings();
    initializeFlashMessages();
    initializeFormValidation();
    initializeInteractiveElements();
}

// Initialize progress rings with animation
function initializeProgressRings() {
    const progressRings = document.querySelectorAll('.progress-ring-circle');
    
    progressRings.forEach(ring => {
        const radius = ring.r.baseVal.value;
        const circumference = radius * 2 * Math.PI;
        
        ring.style.strokeDasharray = `${circumference} ${circumference}`;
        ring.style.strokeDashoffset = circumference;
        
        const offset = circumference - (parseInt(ring.parentElement.nextElementSibling?.textContent || '0') / 100 * circumference);
        setTimeout(() => {
            ring.style.strokeDashoffset = offset;
        }, 100);
    });
}

// Auto-hide flash messages after 5 seconds
function initializeFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'slideInRight 0.3s ease reverse';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
}

// Form validation enhancement
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    highlightFieldError(field);
                } else {
                    clearFieldError(field);
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showToast('Please fill in all required fields', 'error');
            }
        });
    });
}

function highlightFieldError(field) {
    field.style.borderColor = 'var(--danger-color)';
    field.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
}

function clearFieldError(field) {
    field.style.borderColor = '';
    field.style.boxShadow = '';
}

// Initialize interactive elements
function initializeInteractiveElements() {
    initializePathSharing();
    initializeSmoothScrolling();
    initializeGlassCardEffects();
}

// Path sharing functionality
function initializePathSharing() {
    const shareButtons = document.querySelectorAll('.share-path');
    
    shareButtons.forEach(button => {
        button.addEventListener('click', function() {
            const pathId = this.dataset.pathId;
            sharePath(pathId);
        });
    });
}

function sharePath(pathId) {
    const shareUrl = `${window.location.origin}/path/${pathId}`;
    
    if (navigator.share) {
        navigator.share({
            title: 'Check out my learning path!',
            url: shareUrl
        });
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(shareUrl).then(() => {
            showToast('Link copied to clipboard!', 'success');
        }).catch(() => {
            // Final fallback: show URL
            prompt('Copy this link to share:', shareUrl);
        });
    }
}

// Smooth scrolling for anchor links
function initializeSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Enhanced glass card effects
function initializeGlassCardEffects() {
    const cards = document.querySelectorAll('.glass-card');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const angleY = (x - centerX) / 10;
            const angleX = (centerY - y) / 10;
            
            this.style.transform = `perspective(1000px) rotateX(${angleX}deg) rotateY(${angleY}deg) scale3d(1.02, 1.02, 1.02)`;
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
        });
    });
}

// Toast notification system
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${getToastIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="toast-close">&times;</button>
    `;
    
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    toastContainer.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
        toast.style.opacity = '1';
    }, 10);
    
    // Auto remove after 5 seconds
    const autoRemove = setTimeout(() => {
        removeToast(toast);
    }, 5000);
    
    // Close button
    toast.querySelector('.toast-close').addEventListener('click', () => {
        clearTimeout(autoRemove);
        removeToast(toast);
    });
}

function getToastIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        gap: 10px;
        max-width: 400px;
    `;
    document.body.appendChild(container);
    return container;
}

function removeToast(toast) {
    toast.style.transform = 'translateX(100%)';
    toast.style.opacity = '0';
    setTimeout(() => {
        toast.remove();
    }, 300);
}

// Progress tracking utilities
function updateStepProgress(stepId, status) {
    // This would typically make an API call to update the progress
    console.log(`Updating step ${stepId} to ${status}`);
    
    // Update UI immediately for better UX
    const stepElement = document.querySelector(`[data-step-id="${stepId}"]`);
    if (stepElement) {
        const stepItem = stepElement.closest('.step-item');
        stepItem.classList.remove('todo', 'in-progress', 'completed');
        stepItem.classList.add(status === 'done' ? 'completed' : status === 'in_progress' ? 'in-progress' : 'todo');
    }
}

// Responsive navigation
function initializeMobileNavigation() {
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
        });
        
        // Close mobile nav when clicking outside
        document.addEventListener('click', (e) => {
            if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
                navLinks.style.display = 'none';
            }
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeMobileNavigation);

// Export functions for use in other modules
window.SkillPathApp = {
    showToast,
    updateStepProgress,
    sharePath
};

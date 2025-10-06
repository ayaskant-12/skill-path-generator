// Admin JavaScript with Enhanced Glassmorphism UI

document.addEventListener('DOMContentLoaded', function() {
    initializeAdminApp();
});

function initializeAdminApp() {
    initializeAdminCharts();
    initializeAdminModals();
    initializeAdminTables();
    initializeAdminFilters();
    initializeSidebarToggle();
    initializeRealTimeUpdates();
}

// Initialize sidebar toggle for mobile
function initializeSidebarToggle() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.admin-sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 && !sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
            sidebar.classList.add('collapsed');
        }
    });
}

// Initialize admin charts with glassmorphism style
function initializeAdminCharts() {
    // Animate all progress rings
    const progressRings = document.querySelectorAll('.progress-ring-circle');
    
    progressRings.forEach(ring => {
        const radius = ring.r.baseVal.value;
        const circumference = radius * 2 * Math.PI;
        
        ring.style.strokeDasharray = `${circumference} ${circumference}`;
        ring.style.strokeDashoffset = circumference;
        
        const progressText = ring.parentElement.querySelector('.progress-text');
        const progressValue = progressText ? parseFloat(progressText.textContent) : 0;
        const offset = circumference - (progressValue / 100 * circumference);
        
        setTimeout(() => {
            ring.style.strokeDashoffset = offset;
        }, 500);
    });
    
    // Animate completion bars
    const completionBars = document.querySelectorAll('.completion-item .progress-fill, .bar-fill');
    completionBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = width;
        }, 800);
    });
    
    // Animate stat cards
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Enhanced modal management
function initializeAdminModals() {
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(modal => {
        // Close modal on outside click
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal(this);
            }
        });
        
        // Close modal on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                modals.forEach(modal => closeModal(modal));
            }
        });
    });
}

function closeModal(modal) {
    modal.style.animation = 'modalSlideIn 0.3s ease reverse';
    setTimeout(() => {
        modal.style.display = 'none';
        modal.style.animation = '';
    }, 300);
}

// Enhanced table functionality with glassmorphism
function initializeAdminTables() {
    const tables = document.querySelectorAll('.resources-table');
    
    tables.forEach(table => {
        makeTableSortable(table);
        addTableSearch(table);
        addTableHoverEffects(table);
    });
}

function makeTableSortable(table) {
    const headers = table.querySelectorAll('th[class$="-column"]');
    
    headers.forEach((header, index) => {
        if (header.classList.contains('checkbox-column') || header.classList.contains('actions-column')) return;
        
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => {
            sortTable(table, index);
        });
        
        // Add sort indicator
        const sortIndicator = document.createElement('span');
        sortIndicator.className = 'sort-indicator';
        sortIndicator.innerHTML = '<i class="fas fa-sort"></i>';
        header.appendChild(sortIndicator);
    });
}

function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const header = table.querySelectorAll('th')[columnIndex];
    const isNumeric = !isNaN(parseFloat(rows[0].cells[columnIndex].textContent));
    
    // Clear other sort indicators
    table.querySelectorAll('.sort-indicator').forEach(indicator => {
        indicator.innerHTML = '<i class="fas fa-sort"></i>';
    });
    
    rows.sort((a, b) => {
        let aValue, bValue;
        
        if (columnIndex === 1) { // Title column
            aValue = a.querySelector('.resource-title strong').textContent.trim();
            bValue = b.querySelector('.resource-title strong').textContent.trim();
        } else {
            aValue = a.cells[columnIndex].textContent.trim();
            bValue = b.cells[columnIndex].textContent.trim();
        }
        
        if (isNumeric) {
            return parseFloat(aValue) - parseFloat(bValue);
        } else {
            return aValue.localeCompare(bValue);
        }
    });
    
    // Reverse if already sorted
    if (tbody.getAttribute('data-sorted') === columnIndex.toString()) {
        rows.reverse();
        tbody.removeAttribute('data-sorted');
        header.querySelector('.sort-indicator').innerHTML = '<i class="fas fa-sort-down"></i>';
    } else {
        tbody.setAttribute('data-sorted', columnIndex.toString());
        header.querySelector('.sort-indicator').innerHTML = '<i class="fas fa-sort-up"></i>';
    }
    
    // Reappend sorted rows with animation
    rows.forEach((row, index) => {
        row.style.opacity = '0';
        row.style.transform = 'translateX(-20px)';
        tbody.appendChild(row);
        
        setTimeout(() => {
            row.style.transition = 'all 0.3s ease';
            row.style.opacity = '1';
            row.style.transform = 'translateX(0)';
        }, index * 50);
    });
}

function addTableHoverEffects(table) {
    const rows = table.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.background = 'rgba(255, 255, 255, 0.05)';
            this.style.transform = 'translateX(5px)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.background = '';
            this.style.transform = '';
        });
    });
}

// Filter functionality with enhanced UI
function initializeAdminFilters() {
    const filterContainers = document.querySelectorAll('[data-filter]');
    
    filterContainers.forEach(container => {
        const filterSelect = container.querySelector('select');
        if (filterSelect) {
            filterSelect.addEventListener('change', (e) => {
                applyFilters();
                showAdminToast(`Filter applied: ${e.target.options[e.target.selectedIndex].text}`, 'info');
            });
        }
    });
}

function applyFilters() {
    // Enhanced filter logic with animations
    const searchTerm = document.getElementById('resourceSearch')?.value.toLowerCase() || '';
    const typeFilter = document.getElementById('typeFilter')?.value || '';
    const categoryFilter = document.getElementById('categoryFilter')?.value || '';
    
    const rows = document.querySelectorAll('.resource-row');
    let visibleCount = 0;
    
    rows.forEach((row, index) => {
        const title = row.querySelector('.resource-title strong').textContent.toLowerCase();
        const description = row.querySelector('.resource-desc')?.textContent.toLowerCase() || '';
        const type = row.dataset.type;
        const category = (row.dataset.category || '').toLowerCase();
        
        const matchesSearch = title.includes(searchTerm) || description.includes(searchTerm);
        const matchesType = !typeFilter || type === typeFilter;
        const matchesCategory = !categoryFilter || category.includes(categoryFilter.toLowerCase());
        
        if (matchesSearch && matchesType && matchesCategory) {
            visibleCount++;
            row.style.display = '';
            // Animate in
            row.style.animation = `fadeIn 0.3s ease ${index * 0.1}s both`;
        } else {
            // Animate out
            row.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                row.style.display = 'none';
                row.style.animation = '';
            }, 300);
        }
    });
    
    // Update pagination info
    const paginationInfo = document.querySelector('.pagination-info');
    if (paginationInfo) {
        paginationInfo.innerHTML = `Showing <strong>${visibleCount}</strong> of <strong>${rows.length}</strong> resources`;
    }
}

// Enhanced resource management functions
function openAddResourceModal() {
    const modal = document.getElementById('resourceModal');
    if (modal) {
        document.getElementById('modalTitle').textContent = 'Add New Resource';
        document.getElementById('resourceForm').reset();
        document.getElementById('resourceId').value = '';
        modal.style.display = 'flex';
    }
}

function closeResourceModal() {
    const modal = document.getElementById('resourceModal');
    if (modal) {
        closeModal(modal);
    }
}

function previewResource(resourceId) {
    const modal = document.getElementById('previewModal');
    const content = modal.querySelector('.preview-content');
    
    // Show loading with animation
    content.innerHTML = `
        <div class="preview-loading">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Loading resource details...</p>
        </div>
    `;
    
    modal.style.display = 'flex';
    
    // Simulate API call with enhanced UI
    setTimeout(() => {
        content.innerHTML = `
            <div class="resource-preview">
                <div class="preview-header">
                    <div class="preview-type">
                        <i class="fas fa-graduation-cap"></i>
                        <span>Online Course</span>
                    </div>
                    <div class="preview-meta">
                        <span class="difficulty-badge intermediate">Intermediate</span>
                        <span class="duration">8 hours</span>
                    </div>
                </div>
                <h3 class="preview-title">Advanced React Patterns and Best Practices</h3>
                <p class="preview-description">Learn advanced React patterns including compound components, render props, higher-order components, and hooks optimization. This course covers performance optimization, code splitting, and advanced state management techniques.</p>
                <div class="preview-url">
                    <i class="fas fa-link"></i>
                    <a href="https://example.com/advanced-react-patterns" target="_blank">https://example.com/advanced-react-patterns</a>
                </div>
                <div class="preview-tags">
                    <span class="tag">React</span>
                    <span class="tag">JavaScript</span>
                    <span class="tag">Patterns</span>
                    <span class="tag">Performance</span>
                    <span class="tag">Hooks</span>
                </div>
                <div class="preview-stats">
                    <div class="stat">
                        <span class="label">Added</span>
                        <span class="value">2 weeks ago</span>
                    </div>
                    <div class="stat">
                        <span class="label">Used in</span>
                        <span class="value">15 paths</span>
                    </div>
                    <div class="stat">
                        <span class="label">Rating</span>
                        <span class="value">4.8/5</span>
                    </div>
                </div>
            </div>
        `;
    }, 1500);
}

function closePreviewModal() {
    const modal = document.getElementById('previewModal');
    if (modal) {
        closeModal(modal);
    }
}

function editResource(resourceId) {
    // Enhanced edit with simulated data
    document.getElementById('modalTitle').textContent = 'Edit Resource';
    document.getElementById('resourceId').value = resourceId;
    
    // Simulate populated data with enhanced fields
    document.getElementById('resourceTitle').value = 'Advanced React Patterns and Best Practices';
    document.getElementById('resourceType').value = 'course';
    document.getElementById('resourceCategory').value = 'web development';
    document.getElementById('resourceUrl').value = 'https://example.com/advanced-react-patterns';
    document.getElementById('resourceDescription').value = 'Learn advanced React patterns including compound components, render props, higher-order components, and hooks optimization. This course covers performance optimization, code splitting, and advanced state management techniques.';
    document.getElementById('resourceDifficulty').value = 'intermediate';
    document.getElementById('resourceDuration').value = '3 weeks';
    document.getElementById('resourceTags').value = 'react, patterns, hooks, context, performance';
    
    document.getElementById('resourceModal').style.display = 'flex';
}

function deleteResource(resourceId) {
    showAdminConfirm(
        'Delete Resource',
        'Are you sure you want to delete this resource? This action cannot be undone and will affect any learning paths using this resource.',
        'danger',
        () => {
            // Simulate API call
            showAdminToast('Resource deleted successfully', 'success');
            // In real implementation, remove from UI or reload
        }
    );
}

function selectAllResources() {
    const checkboxes = document.querySelectorAll('.resource-checkbox');
    const selectAll = document.getElementById('selectAll');
    const isChecked = selectAll.checked;
    
    checkboxes.forEach((checkbox, index) => {
        setTimeout(() => {
            checkbox.checked = isChecked;
            // Add visual feedback
            const row = checkbox.closest('tr');
            if (isChecked) {
                row.style.background = 'rgba(99, 102, 241, 0.1)';
            } else {
                row.style.background = '';
            }
        }, index * 50);
    });
}

function deleteSelectedResources() {
    const selected = document.querySelectorAll('.resource-checkbox:checked');
    if (selected.length === 0) {
        showAdminToast('Please select at least one resource to delete', 'error');
        return;
    }
    
    showAdminConfirm(
        'Delete Multiple Resources',
        `You are about to delete ${selected.length} resources. This action cannot be undone.`,
        'danger',
        () => {
            showAdminToast(`${selected.length} resources deleted successfully`, 'success');
            // In real implementation, make API call and update UI
        }
    );
}

function clearFilters() {
    document.getElementById('resourceSearch').value = '';
    document.getElementById('typeFilter').value = '';
    document.getElementById('categoryFilter').value = '';
    applyFilters();
    showAdminToast('Filters cleared', 'info');
}

// Enhanced toast notification system for admin
function showAdminToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `admin-toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${getToastIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    const container = document.getElementById('admin-toast-container') || createAdminToastContainer();
    container.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
        toast.style.opacity = '1';
    }, 10);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.transform = 'translateX(100%)';
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }
    }, 5000);
}

function showAdminConfirm(title, message, type, onConfirm) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content glass-card">
            <div class="modal-header">
                <h3>${title}</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="confirm-body">
                <div class="confirm-icon ${type}">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <p>${message}</p>
            </div>
            <div class="modal-actions">
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                <button class="btn btn-${type}" id="confirmAction">Confirm</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.style.display = 'flex';
    
    document.getElementById('confirmAction').addEventListener('click', () => {
        modal.remove();
        onConfirm();
    });
    
    // Close on outside click
    modal.addEventListener('click', function(e) {
        if (e.target === this) {
            this.remove();
        }
    });
}

function createAdminToastContainer() {
    const container = document.createElement('div');
    container.id = 'admin-toast-container';
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

function getToastIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Real-time updates for admin dashboard
function initializeRealTimeUpdates() {
    // Simulate real-time updates with enhanced animations
    setInterval(() => {
        updateLiveStats();
        updateActivityFeed();
    }, 30000);
}

function updateLiveStats() {
    const stats = document.querySelectorAll('.stat-number');
    stats.forEach(stat => {
        const current = parseInt(stat.textContent.replace(/,/g, ''));
        const change = Math.floor(Math.random() * 10) - 2;
        const newValue = Math.max(0, current + change);
        
        animateValue(stat, current, newValue, 1000);
    });
}

function updateActivityFeed() {
    const activities = [
        'New user registration',
        'Learning path completed',
        'Resource added',
        'Progress milestone reached',
        'System backup completed'
    ];
    
    const randomActivity = activities[Math.floor(Math.random() * activities.length)];
    
    // In a real implementation, this would add to the activity timeline
    console.log('New activity:', randomActivity);
}

function animateValue(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const value = Math.floor(progress * (end - start) + start);
        element.textContent = value.toLocaleString();
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// Export functionality
function exportAnalyticsReport() {
    showAdminToast('Generating comprehensive analytics report...', 'info');
    // Simulate report generation
    setTimeout(() => {
        showAdminToast('Analytics report exported successfully!', 'success');
    }, 2000);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeOut {
            from { opacity: 1; transform: translateY(0); }
            to { opacity: 0; transform: translateY(10px); }
        }
        
        .admin-toast {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: var(--border-radius);
            padding: 1rem 1.5rem;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            transform: translateX(100%);
            opacity: 0;
            transition: all 0.3s ease;
            box-shadow: var(--glass-shadow);
        }
        
        .toast-success { border-left: 4px solid var(--success-color); }
        .toast-error { border-left: 4px solid var(--danger-color); }
        .toast-warning { border-left: 4px solid var(--warning-color); }
        .toast-info { border-left: 4px solid var(--primary-color); }
        
        .toast-content {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex: 1;
        }
        
        .toast-close {
            background: none;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            padding: 0.25rem;
            border-radius: var(--border-radius-sm);
        }
        
        .toast-close:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .confirm-body {
            padding: 2rem;
            text-align: center;
        }
        
        .confirm-icon {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            margin: 0 auto 1.5rem;
        }
        
        .confirm-icon.success { background: rgba(16, 185, 129, 0.1); color: var(--success-color); }
        .confirm-icon.error { background: rgba(239, 68, 68, 0.1); color: var(--danger-color); }
        .confirm-icon.warning { background: rgba(245, 158, 11, 0.1); color: var(--warning-color); }
        .confirm-icon.info { background: rgba(99, 102, 241, 0.1); color: var(--primary-color); }
        
        .sort-indicator {
            margin-left: 0.5rem;
            color: var(--text-secondary);
        }
        
        .admin-sidebar.collapsed {
            transform: translateX(-100%);
        }
        
        @media (max-width: 768px) {
            .admin-sidebar {
                position: fixed;
                height: 100vh;
                z-index: 1000;
                transform: translateX(-100%);
                transition: transform 0.3s ease;
            }
            
            .admin-sidebar:not(.collapsed) {
                transform: translateX(0);
            }
        }
    `;
    document.head.appendChild(style);
});

// Export admin functions
window.AdminApp = {
    openAddResourceModal,
    closeResourceModal,
    editResource,
    deleteResource,
    exportAnalyticsReport,
    showAdminToast,
    showAdminConfirm
};

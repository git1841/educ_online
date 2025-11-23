// Admin Panel JavaScript

// Toggle User Active Status
async function toggleUserActive(userId) {
    if (!confirm('Changer le statut de cet utilisateur?')) return;

    try {
        const response = await fetch(`/admin/toggle_user_active/${userId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showAlert('✅ ' + data.message, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert('❌ Erreur lors de la modification', 'danger');
        }
    } catch (error) {
        showAlert('❌ Erreur de connexion', 'danger');
    }
}

// Verify User
async function verifyUser(userId) {
    if (!confirm('Vérifier cet utilisateur?')) return;

    try {
        const response = await fetch(`/admin/verify_user/${userId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showAlert('✅ ' + data.message, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert('❌ Erreur lors de la vérification', 'danger');
        }
    } catch (error) {
        showAlert('❌ Erreur de connexion', 'danger');
    }
}

// Issue Warning
function issueWarning(userId, userName) {
    document.getElementById('warningUserId').value = userId;
    document.getElementById('warningUserName').textContent = userName;

    const modal = new bootstrap.Modal(document.getElementById('warningModal'));
    modal.show();
}

// Warning Form Handler
const warningForm = document.getElementById('warningForm');
if (warningForm) {
    warningForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(e.target);
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalHTML = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Envoi...';

        try {
            const response = await fetch('/admin/issue_warning', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success) {
                showAlert('✅ ' + data.message, 'success');
                const modal = bootstrap.Modal.getInstance(document.getElementById('warningModal'));
                modal.hide();
                e.target.reset();
            } else {
                showAlert('❌ ' + (data.detail || 'Erreur'), 'danger');
            }
        } catch (error) {
            showAlert('❌ Erreur de connexion', 'danger');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalHTML;
        }
    });
}

// Upload Content Form Handler
const uploadContentForm = document.getElementById('uploadContentForm');
if (uploadContentForm) {
    uploadContentForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(e.target);
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalHTML = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Upload...';

        try {
            const response = await fetch('/admin/upload_content', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success) {
                showAlert('✅ ' + data.message, 'success');
                const modal = bootstrap.Modal.getInstance(document.getElementById('uploadContentModal'));
                modal.hide();
                setTimeout(() => location.reload(), 1500);
            } else {
                showAlert('❌ ' + (data.detail || 'Erreur lors de l\'upload'), 'danger');
            }
        } catch (error) {
            showAlert('❌ Erreur de connexion', 'danger');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalHTML;
        }
    });
}

// Delete Content
async function deleteContent(contentId) {
    if (!confirm('Supprimer ce contenu? Cette action est irréversible.')) return;

    try {
        const response = await fetch(`/admin/delete_content/${contentId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showAlert('✅ ' + data.message, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert('❌ Erreur lors de la suppression', 'danger');
        }
    } catch (error) {
        showAlert('❌ Erreur de connexion', 'danger');
    }
}

// Toggle Content Access
async function toggleContentAccess(contentId) {
    if (!confirm('Changer le type d\'accès de ce contenu?')) return;

    try {
        const response = await fetch(`/admin/toggle_content_access/${contentId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showAlert('✅ ' + data.message, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert('❌ Erreur lors de la modification', 'danger');
        }
    } catch (error) {
        showAlert('❌ Erreur de connexion', 'danger');
    }
}

// Approve Group
async function approveGroup(requestId) {
    if (!confirm('Approuver cette demande de groupe?')) return;

    try {
        const response = await fetch(`/admin/approve_group/${requestId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showAlert('✅ ' + data.message, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert('❌ Erreur lors de l\'approbation', 'danger');
        }
    } catch (error) {
        showAlert('❌ Erreur de connexion', 'danger');
    }
}

// Reject Group
async function rejectGroup(requestId) {
    if (!confirm('Rejeter cette demande de groupe?')) return;

    try {
        const response = await fetch(`/admin/reject_group/${requestId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showAlert('✅ ' + data.message, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert('❌ Erreur lors du rejet', 'danger');
        }
    } catch (error) {
        showAlert('❌ Erreur de connexion', 'danger');
    }
}

// Create Publication Form Handler
const createPublicationForm = document.getElementById('createPublicationForm');
if (createPublicationForm) {
    createPublicationForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(e.target);
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalHTML = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Publication...';

        try {
            const response = await fetch('/admin/create_publication', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success) {
                showAlert('✅ ' + data.message, 'success');
                const modal = bootstrap.Modal.getInstance(document.getElementById('createPublicationModal'));
                modal.hide();
                setTimeout(() => location.reload(), 1500);
            } else {
                showAlert('❌ ' + (data.detail || 'Erreur'), 'danger');
            }
        } catch (error) {
            showAlert('❌ Erreur de connexion', 'danger');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalHTML;
        }
    });
}

// Delete Publication
async function deletePublication(pubId) {
    if (!confirm('Supprimer cette publication?')) return;

    try {
        const response = await fetch(`/admin/delete_publication/${pubId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showAlert('✅ ' + data.message, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert('❌ Erreur lors de la suppression', 'danger');
        }
    } catch (error) {
        showAlert('❌ Erreur de connexion', 'danger');
    }
}

// Search and Filter Functionality for Tables
function setupTableSearch(searchInputId, tableId) {
    const searchInput = document.getElementById(searchInputId);
    const table = document.getElementById(tableId);

    if (searchInput && table) {
        searchInput.addEventListener('input', debounce((e) => {
            const searchTerm = e.target.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        }, 300));
    }
}

// Export Table to CSV
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;

    let csv = [];
    const rows = table.querySelectorAll('tr');

    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = Array.from(cols).map(col => {
            return '"' + col.textContent.replace(/"/g, '""') + '"';
        });
        csv.push(rowData.join(','));
    });

    // Download CSV
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);

    showAlert('✅ Export réussi', 'success');
}

// Statistics Chart (if needed)
function createStatisticsChart(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    // Implementation with Chart.js would go here
    console.log('Chart data:', data);
}

// Auto-refresh statistics every 30 seconds
let statsRefreshInterval = null;

function startStatsRefresh() {
    statsRefreshInterval = setInterval(async () => {
        try {
            const response = await fetch('/admin/get_stats');
            const data = await response.json();

            if (data.success) {
                // Update statistics cards
                updateStatisticsDisplay(data.stats);
            }
        } catch (error) {
            console.error('Error refreshing stats:', error);
        }
    }, 30000);
}

function stopStatsRefresh() {
    if (statsRefreshInterval) {
        clearInterval(statsRefreshInterval);
        statsRefreshInterval = null;
    }
}

function updateStatisticsDisplay(stats) {
    // Update each statistic card
    const statsElements = {
        'total_users': stats.total_users,
        'pro_users': stats.pro_users,
        'total_contents': stats.total_contents,
        'pending_groups': stats.pending_groups
    };

    Object.entries(statsElements).forEach(([key, value]) => {
        const element = document.querySelector(`[data-stat="${key}"]`);
        if (element) {
            element.textContent = value;
        }
    });
}

// Bulk Actions
let selectedRows = new Set();

function toggleRowSelection(checkbox, rowId) {
    if (checkbox.checked) {
        selectedRows.add(rowId);
    } else {
        selectedRows.delete(rowId);
    }

    updateBulkActionsUI();
}

function toggleAllRows(checkbox) {
    const checkboxes = document.querySelectorAll('.row-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = checkbox.checked;
        toggleRowSelection(cb, cb.dataset.rowId);
    });
}

function updateBulkActionsUI() {
    const bulkActionsBar = document.getElementById('bulkActionsBar');
    const selectedCount = document.getElementById('selectedCount');

    if (bulkActionsBar && selectedCount) {
        if (selectedRows.size > 0) {
            bulkActionsBar.style.display = 'block';
            selectedCount.textContent = selectedRows.size;
        } else {
            bulkActionsBar.style.display = 'none';
        }
    }
}

// Initialize admin panel
document.addEventListener('DOMContentLoaded', () => {
    // Start stats refresh if on admin panel
    if (document.getElementById('admin_panel')) {
        startStatsRefresh();
    }

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        stopStatsRefresh();
    });
});

console.log('✅ Admin JavaScript chargé');




// AJOUTER CES FONCTIONS DANS admin.js: 


async function approveProUpgrade(requestId) {
    if (!confirm('Approuver cette demande d\'upgrade PRO?')) return;

    try {
        const response = await fetch(`/admin/approve_pro_upgrade/${requestId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showAlert('✅ ' + data.message, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert('❌ Erreur lors de l\'approbation', 'danger');
        }
    } catch (error) {
        showAlert('❌ Erreur de connexion', 'danger');
    }
}

async function rejectProUpgrade(requestId) {
    if (!confirm('Rejeter cette demande d\'upgrade PRO?')) return;

    try {
        const response = await fetch(`/admin/reject_pro_upgrade/${requestId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showAlert('✅ ' + data.message, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert('❌ Erreur lors du rejet', 'danger');
        }
    } catch (error) {
        showAlert('❌ Erreur de connexion', 'danger');
    }
}
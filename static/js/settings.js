// Settings page controller

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

function showAlert(message, type = 'error') {
    const container = document.getElementById('alert-container');
    container.innerHTML = `
        <div class="alert alert-${type}">
            <span>${type === 'error' ? '&#9888;' : '&#8505;'}</span>
            <span>${message}</span>
        </div>
    `;
}

async function loadProfile() {
    try {
        const res = await fetch('/api/auth/me');
        if (!res.ok) throw new Error('Failed to load profile');
        const user = await res.json();
        
        document.getElementById('settings-username').value = user.username || '';
        document.getElementById('settings-email').value = user.email || '';
    } catch (err) {
        showAlert(err.message, 'error');
    }
}

async function handleSaveSettings(e) {
    e.preventDefault();
    
    const usernameInput = document.getElementById('settings-username');
    const emailInput = document.getElementById('settings-email');
    const newPasswordInput = document.getElementById('settings-new-password');
    const currentPasswordInput = document.getElementById('settings-current-password');
    const submitBtn = document.getElementById('save-settings-btn');
    const alertContainer = document.getElementById('alert-container');

    alertContainer.innerHTML = ''; // Clear alerts
    submitBtn.disabled = true;
    submitBtn.textContent = 'Saving...';

    const payload = {
        username: usernameInput.value.trim(),
        email: emailInput.value.trim() || null,
        current_password: currentPasswordInput.value,
        new_password: newPasswordInput.value || null
    };

    try {
        const res = await fetch('/api/auth/profile', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.detail || 'Failed to update profile');
        }

        showToast('Settings saved successfully!');
        
        // Reset password fields
        newPasswordInput.value = '';
        currentPasswordInput.value = '';
        
        // Update user greeting in sidebar
        const userEl = document.getElementById('sidebar-username');
        if (userEl) {
            userEl.textContent = data.username;
        }
    } catch (err) {
        showAlert(err.message, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Save Settings';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadProfile();
});

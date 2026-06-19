// Global Authentication Helper

let currentUser = null;

function showBody() {
    const hideStyle = document.getElementById('auth-hide-body');
    if (hideStyle) {
        hideStyle.remove();
    }
    document.body.style.display = '';
}

async function checkAuth() {
    const isLoginPage = !!window.location.pathname.match(/^\/(login)(\.html)?$/);
    
    try {
        const res = await fetch('/api/auth/me');
        
        if (res.ok) {
            currentUser = await res.json();
            if (isLoginPage) {
                // If already logged in and on login page, go to dashboard
                window.location.href = '/dashboard';
            } else {
                // Display username in sidebar if element exists
                const userEl = document.getElementById('sidebar-username');
                if (userEl) {
                    userEl.textContent = currentUser.username;
                }
                
                // Show body now that we are authenticated
                showBody();
            }
        } else {
            if (!isLoginPage) {
                // If not logged in and on admin page, redirect to login
                window.location.href = '/login';
            } else {
                // If on login page, show body
                showBody();
            }
        }
    } catch (err) {
        console.error('Auth check failed:', err);
        if (!isLoginPage) {
            window.location.href = '/login';
        } else {
            showBody();
        }
    }
}

async function handleLogout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
    } catch (err) {
        console.error('Logout error:', err);
    }
    window.location.href = '/login';
}

// Add hide stylesheet to head immediately to avoid UI flashing while loading auth
if (!window.location.pathname.match(/^\/(login)(\.html)?$/) && !window.location.pathname.match(/^\/(form)(\.html)?/)) {
    const style = document.createElement('style');
    style.id = 'auth-hide-body';
    style.innerHTML = 'body { display: none !important; }';
    document.head.appendChild(style);
}

document.addEventListener('DOMContentLoaded', () => {
    // Run auth check
    checkAuth();
    
    // Add logout button event listener if it exists
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            handleLogout();
        });
    }
});

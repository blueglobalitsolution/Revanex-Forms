let deleteFormId = null;

function slugify(text) {
    return text
        .toString()
        .toLowerCase()
        .trim()
        .replace(/\s+/g, '-')           // Replace spaces with -
        .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
        .replace(/\-\-+/g, '-')         // Replace multiple - with single -
        .replace(/^-+/, '')             // Trim - from start of text
        .replace(/-+$/, '');            // Trim - from end of text
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

async function fetchForms() {
    const loading = document.getElementById('loading-state');
    const empty = document.getElementById('empty-state');
    const container = document.getElementById('forms-container');
    const list = document.getElementById('form-list');

    try {
        const res = await fetch('/api/forms');
        if (!res.ok) throw new Error('Failed to load forms');
        const forms = await res.json();

        loading.style.display = 'none';

        if (forms.length === 0) {
            empty.style.display = 'block';
            container.style.display = 'none';
            return;
        }

        container.style.display = 'block';
        list.innerHTML = forms.map(form => {
            const slug = slugify(form.title) || form.id;
            return `
                <div class="form-card">
                    <div class="form-card-info">
                        <h4>${escapeHtml(form.title)}</h4>
                        <p>${form.description ? escapeHtml(form.description.substring(0, 100)) : 'No description'}</p>
                        <div style="display:flex;gap:8px;margin-top:6px">
                            ${form.is_active ? '<span class="badge badge-success">Active</span>' : '<span class="badge badge-danger">Inactive</span>'}
                            ${form.razorpay_enabled ? '<span class="badge badge-info">Payments</span>' : ''}
                        </div>
                    </div>
                    <div class="form-card-meta">
                        <div class="stat">
                            <div class="stat-value">${form.submission_count}</div>
                            <div class="stat-label">Submissions</div>
                        </div>
                    </div>
                    <div class="form-card-actions">
                        <button class="btn btn-secondary btn-sm" onclick="shareForm('${slug}')">Share</button>
                        <a href="/submissions.html?form_id=${form.id}" class="btn btn-secondary btn-sm">View</a>
                        <a href="/create-form.html?edit=${form.id}" class="btn btn-secondary btn-sm">Edit</a>
                        <button class="btn btn-danger btn-sm" onclick="promptDelete(${form.id}, '${escapeHtml(form.title)}')">Delete</button>
                    </div>
                </div>
            `;
        }).join('');
    } catch (err) {
        loading.style.display = 'none';
        document.getElementById('alert-container').innerHTML = `
            <div class="alert alert-error"><span>&#9888;</span> ${err.message}</div>
        `;
    }
}

function shareForm(formSlugOrId) {
    const link = `${window.location.origin}/form.html?id=${formSlugOrId}`;
    const embed = `<iframe src="${window.location.origin}/form.html?id=${formSlugOrId}" width="100%" height="800" frameborder="0" style="border:1px solid #fbfbf2;border-radius:10px;max-width:720px;margin:0 auto;display:block"></iframe>`;

    document.getElementById('share-link').value = link;
    document.getElementById('embed-code').value = embed;
    document.getElementById('share-modal').classList.add('active');
}

function closeShareModal() {
    document.getElementById('share-modal').classList.remove('active');
}

function copyShareLink() {
    const input = document.getElementById('share-link');
    input.select();
    navigator.clipboard.writeText(input.value).then(() => {
        showToast('Link copied!');
    }).catch(() => {
        input.select();
        document.execCommand('copy');
        showToast('Link copied!');
    });
}

function copyEmbedCode() {
    const input = document.getElementById('embed-code');
    input.select();
    navigator.clipboard.writeText(input.value).then(() => {
        showToast('Embed code copied!');
    }).catch(() => {
        input.select();
        document.execCommand('copy');
        showToast('Embed code copied!');
    });
}

function promptDelete(formId, title) {
    deleteFormId = formId;
    document.getElementById('delete-form-name').textContent = `"${title}"`;
    document.getElementById('delete-modal').classList.add('active');
}

function closeDeleteModal() {
    deleteFormId = null;
    document.getElementById('delete-modal').classList.remove('active');
}

async function confirmDelete() {
    if (!deleteFormId) return;
    const btn = document.getElementById('confirm-delete-btn');
    btn.disabled = true;
    btn.textContent = 'Deleting...';

    try {
        const res = await fetch(`/api/forms/${deleteFormId}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Failed to delete form');
        showToast('Form deleted successfully');
        closeDeleteModal();
        fetchForms();
    } catch (err) {
        showToast(err.message, 'error');
        btn.disabled = false;
        btn.textContent = 'Delete';
    }
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

document.addEventListener('DOMContentLoaded', fetchForms);

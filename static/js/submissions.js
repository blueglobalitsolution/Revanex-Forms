let formId = null;
let formData = null;

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function getParam(name) {
    return new URLSearchParams(window.location.search).get(name);
}

async function loadData() {
    formId = parseInt(getParam('form_id'));
    if (!formId) {
        document.getElementById('alert-container').innerHTML = `
            <div class="alert alert-error"><span>&#9888;</span> No form ID specified</div>
        `;
        document.getElementById('loading-state').style.display = 'none';
        return;
    }

    try {
        const [formRes, subsRes] = await Promise.all([
            fetch(`/api/forms/${formId}`),
            fetch(`/api/forms/${formId}/submissions`)
        ]);

        if (!formRes.ok) throw new Error('Form not found');
        formData = await formRes.json();

        document.getElementById('form-title').textContent = `Submissions: ${formData.title}`;

        if (!subsRes.ok) throw new Error('Failed to load submissions');
        const submissions = await subsRes.json();

        document.getElementById('loading-state').style.display = 'none';

        if (submissions.length === 0) {
            document.getElementById('empty-state').style.display = 'block';
            document.getElementById('submission-count').textContent = 'No submissions yet';
            return;
        }

        document.getElementById('submissions-container').style.display = 'block';
        document.getElementById('submission-count').textContent = `${submissions.length} submission${submissions.length !== 1 ? 's' : ''}`;

        renderTable(submissions);
    } catch (err) {
        document.getElementById('loading-state').style.display = 'none';
        document.getElementById('alert-container').innerHTML = `
            <div class="alert alert-error"><span>&#9888;</span> ${err.message}</div>
        `;
    }
}

function renderTable(submissions) {
    const tbody = document.getElementById('submissions-table-body');
    const thead = document.querySelector('#table-header');

    const allKeys = new Set();
    submissions.forEach(sub => {
        if (sub.data) Object.keys(sub.data).forEach(k => allKeys.add(k));
    });
    const keys = Array.from(allKeys);

    let headerHtml = '<th>#</th>';
    keys.forEach(k => { headerHtml += `<th>${escapeHtml(k)}</th>`; });
    headerHtml += '<th>Submitted</th><th>Payment</th><th>Actions</th>';
    thead.innerHTML = headerHtml;

    tbody.innerHTML = submissions.map(sub => {
        const date = sub.created_at ? new Date(sub.created_at).toLocaleString() : '-';
        const paymentStatus = sub.payment_status === 'captured'
            ? '<span class="badge badge-success">Paid</span>'
            : sub.payment_status === 'failed'
                ? '<span class="badge badge-danger">Failed</span>'
                : '<span class="badge badge-info">None</span>';

        return `
            <tr>
                <td>${sub.id}</td>
                ${keys.map(k => `<td>${escapeHtml(sub.data?.[k] || '')}</td>`).join('')}
                <td style="white-space:nowrap;font-size:13px">${date}</td>
                <td>${paymentStatus}</td>
                <td>
                    <div class="actions">
                        <button class="btn btn-secondary btn-sm" onclick="showDetail(${sub.id})">View</button>
                        <button class="btn btn-danger btn-sm" onclick="deleteSubmission(${sub.id})">Delete</button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');

    window._submissions = submissions;
    window._keys = keys;
}

function showDetail(submissionId) {
    const subs = window._submissions || [];
    const sub = subs.find(s => s.id === submissionId);
    if (!sub) return;

    const keys = window._keys || Object.keys(sub.data || {});
    let html = `
        <div style="margin-bottom:16px">
            <span style="font-size:12px;color:var(--gray-400)">Submission #${sub.id}</span>
            <h3 style="margin-top:4px;font-size:18px">${sub.created_at ? new Date(sub.created_at).toLocaleString() : ''}</h3>
        </div>
        <table>
            <thead><tr><th>Field</th><th>Value</th></tr></thead>
            <tbody>
    `;

    keys.forEach(k => {
        const val = sub.data?.[k] || '';
        html += `<tr><td style="font-weight:600">${escapeHtml(k)}</td><td>${escapeHtml(String(val))}</td></tr>`;
    });

    if (sub.payment_id) {
        html += `<tr><td style="font-weight:600">Payment ID</td><td>${escapeHtml(sub.payment_id)}</td></tr>`;
        html += `<tr><td style="font-weight:600">Payment Status</td><td>${escapeHtml(sub.payment_status)}</td></tr>`;
        if (sub.payment_amount) {
            html += `<tr><td style="font-weight:600">Amount</td><td>₹${sub.payment_amount}</td></tr>`;
        }
    }

    html += `</tbody></table>`;

    document.getElementById('detail-body').innerHTML = html;
    document.getElementById('detail-modal').classList.add('active');
}

function closeDetailModal() {
    document.getElementById('detail-modal').classList.remove('active');
}

async function deleteSubmission(submissionId) {
    if (!confirm('Delete this submission?')) return;
    try {
        const res = await fetch(`/api/forms/${formId}/submissions/${submissionId}`, {
            method: 'DELETE'
        });
        if (!res.ok) throw new Error('Failed to delete');
        showToast('Submission deleted');
        loadData();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function exportCSV() {
    if (!formId) return;
    window.location.href = `/api/forms/${formId}/submissions/export`;
}

document.addEventListener('DOMContentLoaded', loadData);

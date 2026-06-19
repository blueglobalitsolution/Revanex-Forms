let fields = [];
let editingFieldId = null;
let editFormId = null;

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

function generateFieldId() {
    return 'field_' + Date.now() + '_' + Math.random().toString(36).substr(2, 5);
}

function addField(type) {
    const field = {
        id: generateFieldId(),
        type: type,
        label: getDefaultLabel(type),
        placeholder: '',
        required: false,
        options: [],
        order: fields.length
    };
    fields.push(field);
    renderCanvas();
    editField(field.id);
}

function getDefaultLabel(type) {
    const labels = {
        text: 'Text Field',
        email: 'Email Address',
        textarea: 'Long Text',
        number: 'Number',
        tel: 'Phone Number',
        select: 'Select Option',
        checkbox: 'Checkbox',
        radio: 'Radio',
        date: 'Date',
        url: 'Website URL',
        time: 'Time',
        rating: 'Star Rating',
        file: 'File Upload',
        hidden: 'Hidden Field'
    };
    return labels[type] || 'Field';
}

function renderCanvas() {
    const canvas = document.getElementById('builder-canvas');
    const empty = document.getElementById('canvas-empty');

    if (fields.length === 0) {
        canvas.innerHTML = `
            <div class="canvas-empty" id="canvas-empty">
                <div class="icon">+</div>
                <h4>Add your first field</h4>
                <p>Click a field type from the left panel to get started</p>
            </div>
        `;
        return;
    }

    const sorted = [...fields].sort((a, b) => a.order - b.order);
    canvas.innerHTML = sorted.map((f, idx) => `
        <div class="builder-field ${editingFieldId === f.id ? 'active' : ''}" data-field-id="${f.id}" draggable="true">
            <span class="drag-handle" onclick="editField('${f.id}')">&#9776;</span>
            <div class="field-content" onclick="editField('${f.id}')">
                <div class="field-header">
                    <span class="field-label">${escapeHtml(f.label)}</span>
                    <span class="field-type-badge">${f.type}</span>
                    ${f.required ? '<span class="badge badge-danger">Required</span>' : ''}
                </div>
                <div style="font-size:12px;color:var(--gray-400)">
                    ${f.type === 'select' || f.type === 'radio' || f.type === 'checkbox'
                        ? `${f.options.length} option${f.options.length !== 1 ? 's' : ''}`
                        : f.placeholder || 'No placeholder'}
                </div>
            </div>
            <div class="field-actions">
                <button class="btn btn-secondary btn-sm btn-icon" onclick="editField('${f.id}')" title="Edit">&#9998;</button>
                <button class="btn btn-danger btn-sm btn-icon" onclick="removeField('${f.id}')" title="Remove">&times;</button>
            </div>
        </div>
    `).join('');

    setupDragDrop();
}

function setupDragDrop() {
    const items = document.querySelectorAll('.builder-field');
    items.forEach(item => {
        item.addEventListener('dragstart', handleDragStart);
        item.addEventListener('dragover', handleDragOver);
        item.addEventListener('drop', handleDrop);
        item.addEventListener('dragend', handleDragEnd);
    });
}

function handleDragStart(e) {
    e.dataTransfer.setData('text/plain', e.currentTarget.dataset.fieldId);
    e.currentTarget.style.opacity = '0.5';
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.style.borderTop = '2px solid var(--primary)';
}

function handleDrop(e) {
    e.preventDefault();
    const fromId = e.dataTransfer.getData('text/plain');
    const toId = e.currentTarget.dataset.fieldId;
    if (fromId === toId) return;

    const fromIdx = fields.findIndex(f => f.id === fromId);
    const toIdx = fields.findIndex(f => f.id === toId);
    const [moved] = fields.splice(fromIdx, 1);
    fields.splice(toIdx, 0, moved);
    fields.forEach((f, i) => f.order = i);
    renderCanvas();
}

function handleDragEnd(e) {
    e.currentTarget.style.opacity = '1';
    document.querySelectorAll('.builder-field').forEach(el => {
        el.style.borderTop = '';
    });
}

function removeField(id) {
    fields = fields.filter(f => f.id !== id);
    fields.forEach((f, i) => f.order = i);
    if (editingFieldId === id) {
        editingFieldId = null;
        document.getElementById('field-editor').classList.remove('active');
    }
    renderCanvas();
}

function editField(id) {
    editingFieldId = id;
    const field = fields.find(f => f.id === id);
    if (!field) return;

    document.getElementById('edit-field-id').value = id;
    document.getElementById('edit-field-label').value = field.label;
    document.getElementById('edit-field-placeholder').value = field.placeholder;
    document.getElementById('edit-field-required').checked = field.required;

    if (field.type === 'hidden') {
        document.getElementById('edit-field-placeholder-label').textContent = 'Default Value';
        document.getElementById('edit-field-placeholder').placeholder = 'Value to pass secretly';
    } else {
        document.getElementById('edit-field-placeholder-label').textContent = 'Placeholder';
        document.getElementById('edit-field-placeholder').placeholder = 'Placeholder text';
    }

    const optionsGroup = document.getElementById('edit-field-options-group');
    if (field.type === 'select' || field.type === 'checkbox' || field.type === 'radio') {
        optionsGroup.style.display = 'block';
        document.getElementById('edit-field-options').value = field.options.join('\n');
    } else {
        optionsGroup.style.display = 'none';
    }

    document.getElementById('field-editor').classList.add('active');
    renderCanvas();
}

function saveFieldEdit() {
    const id = document.getElementById('edit-field-id').value;
    const field = fields.find(f => f.id === id);
    if (!field) return;

    field.label = document.getElementById('edit-field-label').value.trim() || field.label;
    field.placeholder = document.getElementById('edit-field-placeholder').value;
    field.required = document.getElementById('edit-field-required').checked;

    if (field.type === 'select' || field.type === 'checkbox' || field.type === 'radio') {
        const raw = document.getElementById('edit-field-options').value;
        field.options = raw.split('\n').map(s => s.trim()).filter(s => s.length > 0);
    }

    editingFieldId = null;
    document.getElementById('field-editor').classList.remove('active');
    renderCanvas();
}

function toggleRazorpaySettings() {
    const enabled = document.getElementById('razorpay-toggle').checked;
    document.getElementById('razorpay-settings').style.display = enabled ? 'block' : 'none';
}

async function saveForm() {
    const title = document.getElementById('form-title').value.trim();
    if (!title) {
        showToast('Please enter a form title', 'error');
        return;
    }

    const btn = document.getElementById('save-form-btn');
    btn.disabled = true;
    btn.textContent = 'Saving...';

    const payload = {
        title: title,
        description: document.getElementById('form-description').value.trim(),
        fields: fields.map(f => ({
            id: f.id,
            type: f.type,
            label: f.label,
            placeholder: f.placeholder,
            required: f.required,
            options: f.options,
            order: f.order
        })),
        razorpay_enabled: document.getElementById('razorpay-toggle').checked,
        razorpay_key_id: document.getElementById('razorpay-key-id').value.trim() || '',
        razorpay_key_secret: document.getElementById('razorpay-key-secret').value.trim() || '',
        notification_email: document.getElementById('notification-email').value.trim() || '',
        submit_button_text: document.getElementById('submit-text').value.trim() || 'Submit',
        redirect_url: document.getElementById('redirect-url').value.trim() || ''
    };

    try {
        let res;
        if (editFormId) {
            res = await fetch(`/api/forms/${editFormId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        } else {
            res = await fetch('/api/forms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        }

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Failed to save form');
        }

        showToast(editFormId ? 'Form updated!' : 'Form created!');
        setTimeout(() => {
            window.location.href = '/dashboard';
        }, 800);
    } catch (err) {
        showToast(err.message, 'error');
        btn.disabled = false;
        btn.textContent = 'Save Form';
    }
}

async function loadForm(formId) {
    try {
        const res = await fetch(`/api/forms/${formId}`);
        if (!res.ok) throw new Error('Form not found');
        const form = await res.json();

        editFormId = form.id;
        document.getElementById('page-title').textContent = 'Edit Form';
        document.getElementById('form-title').value = form.title;
        document.getElementById('form-description').value = form.description || '';
        document.getElementById('notification-email').value = form.notification_email || '';
        document.getElementById('submit-text').value = form.submit_button_text || 'Submit';
        document.getElementById('redirect-url').value = form.redirect_url || '';

        document.getElementById('razorpay-toggle').checked = form.razorpay_enabled;
        document.getElementById('razorpay-key-id').value = form.razorpay_key_id || '';
        document.getElementById('razorpay-key-secret').value = form.razorpay_key_secret || '';
        toggleRazorpaySettings();

        fields = (form.fields || []).map((f, i) => ({
            id: f.id || generateFieldId(),
            type: f.type,
            label: f.label,
            placeholder: f.placeholder || '',
            required: f.required || false,
            options: f.options || [],
            order: f.order !== undefined ? f.order : i
        }));

        renderCanvas();
    } catch (err) {
        document.getElementById('alert-container').innerHTML = `
            <div class="alert alert-error"><span>&#9888;</span> ${err.message}</div>
        `;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const editId = params.get('edit');
    if (editId) loadForm(parseInt(editId));
});

let formConfig = null;
let currentOrderId = null;

function getParam(name) {
    return new URLSearchParams(window.location.search).get(name);
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

async function loadForm() {
    const formId = getParam('id');
    if (!formId) {
        showError('No form ID specified. Please check your link.');
        return;
    }

    try {
        const res = await fetch(`/api/forms/${formId}`);
        if (!res.ok) throw new Error('Form not found or no longer available');
        formConfig = await res.json();

        if (!formConfig.is_active) {
            showError('This form is no longer accepting submissions.');
            return;
        }

        document.getElementById('form-title').textContent = formConfig.title;
        document.getElementById('form-description').textContent = formConfig.description || '';
        document.getElementById('submit-btn').textContent = formConfig.submit_button_text || 'Submit';

        document.getElementById('form-loading').style.display = 'none';
        document.getElementById('form-content').style.display = 'block';

        if (formConfig.razorpay_enabled) {
            document.getElementById('payment-section').style.display = 'block';
        }

        renderFields(formConfig.fields || []);
    } catch (err) {
        showError(err.message);
    }
}

function renderFields(fields) {
    const container = document.getElementById('form-fields');
    const sorted = [...fields].sort((a, b) => a.order - b.order);

    container.innerHTML = sorted.map(f => {
        const requiredAttr = f.required ? 'required' : '';
        const requiredMark = f.required ? '<span class="required">*</span>' : '';
        const fieldId = `field-${f.id}`;

        let inputHtml = '';
        const common = `id="${fieldId}" class="form-input" ${requiredAttr}`;

        switch (f.type) {
            case 'text':
            case 'url':
                inputHtml = `<input type="${f.type}" ${common} placeholder="${escapeHtml(f.placeholder)}">`;
                break;
            case 'email':
                inputHtml = `<input type="email" ${common} placeholder="${escapeHtml(f.placeholder)}" oninput="checkPriceField()">`;
                break;
            case 'number':
                inputHtml = `<input type="number" ${common} placeholder="${escapeHtml(f.placeholder)}" step="0.01" oninput="checkPriceField()">`;
                break;
            case 'tel':
                inputHtml = `<input type="tel" ${common} placeholder="${escapeHtml(f.placeholder)}">`;
                break;
            case 'date':
                inputHtml = `<input type="date" ${common}>`;
                break;
            case 'textarea':
                inputHtml = `<textarea ${common} placeholder="${escapeHtml(f.placeholder)}" rows="4"></textarea>`;
                break;
            case 'select':
                const opts = (f.options || []).map(o =>
                    `<option value="${escapeHtml(o)}">${escapeHtml(o)}</option>`
                ).join('');
                inputHtml = `<select ${common}><option value="">${escapeHtml(f.placeholder || 'Select...')}</option>${opts}</select>`;
                break;
            case 'checkbox':
                inputHtml = `<div class="checkbox-group">${(f.options || []).map(o => `
                    <label class="checkbox-item">
                        <input type="checkbox" name="${fieldId}" value="${escapeHtml(o)}">
                        <span>${escapeHtml(o)}</span>
                    </label>
                `).join('')}</div>`;
                break;
            case 'radio':
                inputHtml = `<div class="radio-group">${(f.options || []).map(o => `
                    <label class="radio-item">
                        <input type="radio" name="${fieldId}" value="${escapeHtml(o)}" ${requiredAttr}>
                        <span>${escapeHtml(o)}</span>
                    </label>
                `).join('')}</div>`;
                break;
            default:
                inputHtml = `<input type="text" ${common}>`;
        }

        return `
            <div class="form-group" data-field-id="${f.id}" data-field-type="${f.type}">
                <label class="form-label" for="${fieldId}">${escapeHtml(f.label)} ${requiredMark}</label>
                ${inputHtml}
                <div class="form-error" id="error-${f.id}">This field is required</div>
            </div>
        `;
    }).join('');
}

function checkPriceField() {
    if (!formConfig || !formConfig.razorpay_enabled) return;

    const priceField = (formConfig.fields || []).find(f => f.id === 'price' || f.label.toLowerCase() === 'price');
    if (!priceField) return;

    const input = document.getElementById(`field-${priceField.id}`);
    if (!input) return;

    const val = parseFloat(input.value);
    if (!isNaN(val) && val > 0) {
        document.getElementById('payment-amount-display').textContent = val;
        document.getElementById('payment-summary').style.display = 'block';
    } else {
        document.getElementById('payment-summary').style.display = 'none';
    }
}

function collectFormData() {
    const data = {};
    let respondentEmail = null;
    let isValid = true;

    (formConfig.fields || []).forEach(f => {
        const fieldId = `field-${f.id}`;
        const errorEl = document.getElementById(`error-${f.id}`);
        let value = '';

        switch (f.type) {
            case 'checkbox': {
                const checked = document.querySelectorAll(`input[name="${fieldId}"]:checked`);
                value = Array.from(checked).map(cb => cb.value).join(', ');
                break;
            }
            case 'radio': {
                const selected = document.querySelector(`input[name="${fieldId}"]:checked`);
                value = selected ? selected.value : '';
                break;
            }
            default: {
                const el = document.getElementById(fieldId);
                if (el) value = el.value.trim();
            }
        }

        data[f.label] = value;

        if (f.type === 'email' && value) {
            respondentEmail = value;
        }

        if (f.required) {
            if (!value) {
                isValid = false;
                if (errorEl) {
                    errorEl.textContent = 'This field is required';
                    errorEl.classList.add('visible');
                }
                const input = document.getElementById(fieldId);
                if (input) input.classList.add('error');
            } else {
                if (errorEl) errorEl.classList.remove('visible');
                const input = document.getElementById(fieldId);
                if (input) input.classList.remove('error');
            }
        }
    });

    return isValid ? { data, respondentEmail } : null;
}

async function handleSubmit(e) {
    e.preventDefault();
    const btn = document.getElementById('submit-btn');
    const errorContainer = document.getElementById('form-error');
    const errorMessage = document.getElementById('error-message');

    errorContainer.style.display = 'none';

    const collected = collectFormData();
    if (!collected) {
        btn.disabled = false;
        btn.textContent = formConfig?.submit_button_text || 'Submit';
        return;
    }

    btn.disabled = true;
    btn.textContent = 'Submitting...';

    if (formConfig.razorpay_enabled) {
        const priceField = (formConfig.fields || []).find(
            f => f.id === 'price' || f.label.toLowerCase() === 'price'
        );
        const priceValue = priceField
            ? parseFloat(document.getElementById(`field-${priceField.id}`)?.value || '0')
            : 0;

        if (priceValue > 0) {
            const paid = await processPayment(priceValue, collected.respondentEmail);
            if (!paid) {
                btn.disabled = false;
                btn.textContent = formConfig?.submit_button_text || 'Submit';
                return;
            }
            collected.payment_id = paid.payment_id;
            collected.payment_amount = priceValue;
        }
    }

    try {
        const payload = {
            data: collected.data,
            respondent_email: collected.respondentEmail || null,
            payment_id: collected.payment_id || null,
            payment_amount: collected.payment_amount || null
        };

        const res = await fetch(`/api/forms/${getParam('id')}/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Submission failed');
        }

        document.getElementById('form-content').style.display = 'none';
        document.getElementById('form-success').style.display = 'block';

        if (formConfig.redirect_url) {
            setTimeout(() => {
                window.location.href = formConfig.redirect_url;
            }, 3000);
        }
    } catch (err) {
        errorMessage.textContent = err.message;
        errorContainer.style.display = 'block';
        btn.disabled = false;
        btn.textContent = formConfig?.submit_button_text || 'Submit';
    }
}

async function processPayment(amount, respondentEmail) {
    const formId = getParam('id');
    const btn = document.getElementById('submit-btn');

    try {
        const orderRes = await fetch(`/api/forms/${formId}/payment/order`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                amount: Math.round(amount * 100),
                currency: 'INR'
            })
        });

        if (!orderRes.ok) {
            const err = await orderRes.json();
            throw new Error(err.detail || 'Payment initiation failed');
        }

        const orderData = await orderRes.json();
        currentOrderId = orderData.order_id;

        const result = await new Promise((resolve, reject) => {
            const options = {
                key: orderData.key_id,
                amount: orderData.amount,
                currency: orderData.currency,
                name: formConfig.title,
                description: `Payment for ${formConfig.title}`,
                order_id: orderData.order_id,
                handler: function(response) {
                    resolve(response);
                },
                modal: {
                    ondismiss: function() {
                        reject(new Error('Payment cancelled'));
                    }
                },
                prefill: {
                    contact: '',
                    email: respondentEmail || ''
                },
                theme: {
                    color: '#864d26'
                }
            };

            const rzp = new Razorpay(options);
            rzp.on('payment.failed', function(response) {
                reject(new Error(response.error.description || 'Payment failed'));
            });
            rzp.open();
        });

        const verifyRes = await fetch(`/api/forms/${formId}/payment/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                razorpay_order_id: result.razorpay_order_id,
                razorpay_payment_id: result.razorpay_payment_id,
                razorpay_signature: result.razorpay_signature
            })
        });

        const verifyData = await verifyRes.json();
        if (verifyData.status !== 'success') {
            throw new Error('Payment verification failed');
        }

        return { payment_id: result.razorpay_payment_id };
    } catch (err) {
        const errorContainer = document.getElementById('form-error');
        const errorMessage = document.getElementById('error-message');
        errorMessage.textContent = err.message;
        errorContainer.style.display = 'block';
        btn.disabled = false;
        btn.textContent = formConfig?.submit_button_text || 'Submit';
        return null;
    }
}

function showError(message) {
    document.getElementById('form-loading').style.display = 'none';
    document.getElementById('form-error').style.display = 'block';
    document.getElementById('error-message').textContent = message;
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('main-form');
    form.addEventListener('submit', handleSubmit);
    loadForm();
});

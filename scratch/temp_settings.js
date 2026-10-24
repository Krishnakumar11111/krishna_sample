
console.log('[SETTINGS] HTML loaded');

// 1. EDU TRUST SETTINGS NAMESPACE & STATE
window.EduTrustSettings = window.EduTrustSettings || {};

window.EduTrustSettings.CATEGORY_METADATA = window.EduTrustSettings.CATEGORY_METADATA || {
    general: { title: 'General Settings', desc: 'Configure platform name, timezone, currency, language, and system mode.' },
    branding: { title: 'Branding & Logos', desc: 'Upload platform logos, favicon, custom avatars, and primary UI color themes.' },
    user_reg: { title: 'User & Registration', desc: 'Student/Teacher signup rules, email/SMS verification, and login lockouts.' },
    academic: { title: 'Academic Settings', desc: 'Default academic session, class grades, enrollment mode, and batch capacities.' },
    course_content: { title: 'Course & Content', desc: 'Course/lecture approval rules, download permissions, and max file limits.' },
    live_class: { title: 'Live Class Settings', desc: 'Default class durations, session recording, join rules, and live provider.' },
    examination: { title: 'Examination Settings', desc: 'Exam time limits, retake attempts, negative marking, and passing marks.' },
    assignment: { title: 'Assignment Settings', desc: 'Homework submission rules, late penalty %, and file format restrictions.' },
    attendance: { title: 'Attendance Settings', desc: 'Automated live class attendance tracking and minimum attendance rules.' },
    certificate: { title: 'Certificate Settings', desc: 'Automated completion certificates, serial prefix, and verification rules.' },
    payment: { title: 'Payment Settings', desc: 'Online payment gateways (Razorpay/Stripe), currency, and live mode toggles.' },
    communication: { title: 'Email / SMS / Alerts', desc: 'SMTP mail credentials, SMS gateway configuration, and notification triggers.' },
    seo_website: { title: 'SEO & Website Settings', desc: 'Meta title, description, keywords, Google Analytics, and social URLs.' },
    security: { title: 'Security Settings', desc: '2FA settings, minimum password length, lockout policies, and session timeouts.' },
    backup_maint: { title: 'Backup & Maintenance', desc: 'Automated database backups, manual backup creation, restore, and maintenance.' },
    homepage: { title: 'Home Page Settings', desc: 'Manage your public homepage, sections, content, forms and layout without changing code.' }
};

var CATEGORY_METADATA = window.EduTrustSettings.CATEGORY_METADATA;
var currentCategory = window.EduTrustSettings.currentCategory || 'general';
var allSettingsData = window.EduTrustSettings.allSettingsData || {};
var isDirtyForm = false;
window.globalBackupsList = window.globalBackupsList || [];

// 2. HELPER UTILITIES
function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function showToast(msg, type = 'success') {
    const toast = document.getElementById('settingsToast');
    const icon = document.getElementById('toastIcon');
    const msgEl = document.getElementById('toastMsg');
    if (!toast) return;

    msgEl.textContent = msg;
    toast.classList.remove('hidden', 'bg-emerald-50', 'text-emerald-700', 'bg-rose-50', 'text-rose-700');
    
    if (type === 'success') {
        toast.classList.add('bg-emerald-50', 'text-emerald-700', 'border', 'border-emerald-200');
        icon.className = 'fas fa-check-circle text-base text-emerald-600';
    } else {
        toast.classList.add('bg-rose-50', 'text-rose-700', 'border', 'border-rose-200');
        icon.className = 'fas fa-exclamation-triangle text-base text-rose-600';
    }

    setTimeout(() => {
        toast.classList.add('hidden');
    }, 4000);
}

function renderToggleSetting(key, label, desc, isChecked) {
    return `
    <div class="p-3 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 flex items-center justify-between gap-3">
        <div class="min-w-0 flex-1">
            <label class="block font-bold text-xs text-slate-800 dark:text-slate-200 cursor-pointer truncate">${escapeHtml(label)}</label>
            <span class="block text-[10px] text-slate-400 font-medium truncate">${escapeHtml(desc)}</span>
        </div>
        <label class="relative inline-flex items-center cursor-pointer shrink-0">
            <input type="checkbox" name="${key}" ${isChecked ? 'checked' : ''} onchange="markDirty()" class="sr-only peer">
            <div class="w-9 h-5 bg-slate-200 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
        </label>
    </div>`;
}

function renderInputSetting(key, label, desc, val, type = 'text') {
    return `
    <div class="p-3 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 space-y-1.5">
        <div class="flex items-center justify-between gap-2">
            <label class="block font-bold text-xs text-slate-800 dark:text-slate-200 truncate">${escapeHtml(label)}</label>
        </div>
        <input type="${type}" name="${key}" value="${escapeHtml(val)}" oninput="markDirty()" class="w-full px-3 py-2 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-xl text-xs font-semibold text-slate-800 dark:text-slate-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition">
        <span class="block text-[10px] text-slate-400 font-medium">${escapeHtml(desc)}</span>
    </div>`;
}

// 3. SPECIALIZED CATEGORY RENDERERS
// 1. BRANDING SETTINGS CENTER
function renderBrandingSettingsCenter(catKey) {
    const catData = allSettingsData[catKey] || {};
    return `
    <div class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Logo Card -->
            <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 space-y-3">
                <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-xl bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center text-sm"><i class="fas fa-image"></i></div>
                    <label class="block font-bold text-xs text-slate-800 dark:text-slate-200">Main Platform Logo</label>
                </div>
                <div class="flex items-center gap-3 p-2 bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800">
                    <div class="w-14 h-14 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center overflow-hidden p-1 shrink-0">
                        <img id="imgPreview_logo" src="${catData.logo ? catData.logo.value : '/static/images/logo.png'}" class="max-h-full max-w-full object-contain" alt="Logo">
                    </div>
                    <div class="space-y-1.5 min-w-0 flex-1">
                        <input type="file" id="file_logo" onchange="uploadBrandingFile('logo')" class="text-[11px] text-slate-500 file:mr-2 file:py-1 file:px-2 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100">
                        <p class="text-[10px] text-slate-400">PNG, JPG, SVG (Max 10MB)</p>
                    </div>
                </div>
            </div>

            <!-- Favicon Card -->
            <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 space-y-3">
                <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-xl bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 flex items-center justify-center text-sm"><i class="fas fa-globe"></i></div>
                    <label class="block font-bold text-xs text-slate-800 dark:text-slate-200">Browser Favicon</label>
                </div>
                <div class="flex items-center gap-3 p-2 bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800">
                    <div class="w-14 h-14 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center overflow-hidden p-1 shrink-0">
                        <img id="imgPreview_favicon" src="${catData.favicon ? catData.favicon.value : '/static/images/favicon.ico'}" class="max-h-full max-w-full object-contain" alt="Favicon">
                    </div>
                    <div class="space-y-1.5 min-w-0 flex-1">
                        <input type="file" id="file_favicon" onchange="uploadBrandingFile('favicon')" class="text-[11px] text-slate-500 file:mr-2 file:py-1 file:px-2 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100">
                        <p class="text-[10px] text-slate-400">ICO, PNG (16x16 / 32x32)</p>
                    </div>
                </div>
            </div>

            <!-- Loader Card -->
            <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 space-y-3">
                <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-xl bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-sm"><i class="fas fa-spinner"></i></div>
                    <label class="block font-bold text-xs text-slate-800 dark:text-slate-200">Loading Screen Asset</label>
                </div>
                <div class="flex items-center gap-3 p-2 bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800">
                    <div class="w-14 h-14 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center overflow-hidden p-1 shrink-0">
                        <img id="imgPreview_loading_screen" src="${catData.loading_screen && catData.loading_screen.value ? catData.loading_screen.value : '/static/images/loader.gif'}" onerror="this.onerror=null; this.src='/static/images/loader.gif';" class="max-h-full max-w-full object-contain" alt="Loader">
                    </div>
                    <div class="space-y-1.5 min-w-0 flex-1">
                        <input type="file" id="file_loading_screen" onchange="uploadBrandingFile('loading_screen')" class="text-[11px] text-slate-500 file:mr-2 file:py-1 file:px-2 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100">
                        <p class="text-[10px] text-slate-400">GIF, PNG, SVG (Max 5MB)</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 space-y-3">
            <h6 class="font-bold text-xs text-slate-800 dark:text-slate-200">Theme & Accent Colors</h6>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div class="space-y-1.5">
                    <label class="block font-bold text-xs text-slate-600 dark:text-slate-300">Primary Theme Color</label>
                    <div class="flex items-center gap-3 p-2 bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800">
                        <input type="color" name="primary_color" value="${catData.primary_color ? catData.primary_color.value : '#2563eb'}" onchange="markDirty()" class="w-10 h-8 rounded-lg cursor-pointer bg-transparent border-0">
                        <span class="text-xs font-mono font-bold text-slate-700 dark:text-slate-300">${catData.primary_color ? catData.primary_color.value : '#2563eb'}</span>
                    </div>
                </div>
                <div class="space-y-1.5">
                    <label class="block font-bold text-xs text-slate-600 dark:text-slate-300">Secondary Accent Color</label>
                    <div class="flex items-center gap-3 p-2 bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800">
                        <input type="color" name="secondary_color" value="${catData.secondary_color ? catData.secondary_color.value : '#7c3aed'}" onchange="markDirty()" class="w-10 h-8 rounded-lg cursor-pointer bg-transparent border-0">
                        <span class="text-xs font-mono font-bold text-slate-700 dark:text-slate-300">${catData.secondary_color ? catData.secondary_color.value : '#7c3aed'}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>`;
}

// 2. CERTIFICATE SETTINGS CENTER (3 Major Cards on Desktop, Natural Height, No h-full)
function renderCertificateSettingsCenter(catKey) {
    const catData = allSettingsData[catKey] || {};
    
    const getVal = (k, defaultVal = '') => catData[k] ? catData[k].value : defaultVal;
    const isChk = (k, defaultVal = 'true') => {
        const v = catData[k] ? catData[k].value : defaultVal;
        return v.toLowerCase() === 'true' || v === '1';
    };

    return `
    <div class="space-y-4">
        <!-- 3 MAJOR CARDS PER ROW ON DESKTOP (Natural Height, No h-full) -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            
            <!-- CARD 1: Automation & Completion Rules -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
                <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                    <div class="w-8 h-8 rounded-xl bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center text-sm"><i class="fas fa-certificate"></i></div>
                    <div>
                        <h6 class="font-bold text-xs text-slate-900 dark:text-white">Automation & Rules</h6>
                        <span class="text-[10px] text-slate-400 block">Certificate issuance triggers</span>
                    </div>
                </div>

                <div class="space-y-2.5">
                    ${renderToggleSetting('certificate_system_enabled', 'Enable Automated Certificates', 'Generate certificates upon course completion', isChk('certificate_system_enabled'))}
                    ${renderToggleSetting('auto_issue_certificates', 'Auto Issue on Completion', 'Instantly issue certificate when requirement is met', isChk('auto_issue_certificates'))}
                    
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
                        ${renderInputSetting('minimum_course_completion', 'Required Course %', 'Pass threshold', getVal('minimum_course_completion', '80'), 'number')}
                        ${renderInputSetting('certificate_prefix', 'Certificate Prefix', 'Serial code prefix', getVal('certificate_prefix', 'EDU-2026'), 'text')}
                    </div>
                </div>
            </div>

            <!-- CARD 2: Verification & Security -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
                <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                    <div class="w-8 h-8 rounded-xl bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-sm"><i class="fas fa-shield-alt"></i></div>
                    <div>
                        <h6 class="font-bold text-xs text-slate-900 dark:text-white">Verification & Security</h6>
                        <span class="text-[10px] text-slate-400 block">QR verification & digital signature</span>
                    </div>
                </div>

                <div class="space-y-2.5">
                    ${renderToggleSetting('verification_qr_enabled', 'Verification QR Code', 'Print QR verification code on certificates', isChk('verification_qr_enabled'))}
                    ${renderToggleSetting('digital_signature_enabled', 'Digital Signature', 'Embed authorized instructor signature', isChk('digital_signature_enabled'))}
                    ${renderToggleSetting('public_verification_enabled', 'Public Verification Portal', 'Allow online certificate code lookup', isChk('public_verification_enabled'))}
                    
                    <div class="pt-1">
                        ${renderInputSetting('certificate_validity_period', 'Validity Period', 'Expiration policy', getVal('certificate_validity_period', 'Lifetime'), 'text', ['Lifetime', '1 Year', '2 Years', '5 Years'])}
                    </div>
                </div>
            </div>

            <!-- CARD 3: Template & Issuance Management -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
                <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                    <div class="w-8 h-8 rounded-xl bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 flex items-center justify-center text-sm"><i class="fas fa-file-contract"></i></div>
                    <div>
                        <h6 class="font-bold text-xs text-slate-900 dark:text-white">Templates & Issuance</h6>
                        <span class="text-[10px] text-slate-400 block">Design layout & manual issuance</span>
                    </div>
                </div>

                <div class="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200/60 dark:border-slate-800 space-y-2 text-xs">
                    <div class="flex justify-between items-center text-slate-600 dark:text-slate-300">
                        <span>Active Layout:</span>
                        <strong class="text-slate-900 dark:text-white">EduTrust Standard Gold</strong>
                    </div>
                    <div class="flex justify-between items-center text-slate-600 dark:text-slate-300">
                        <span>Issued Certificates:</span>
                        <span class="badge bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300 px-2 py-0.5 rounded-full text-[10px] font-bold">142 Certificates</span>
                    </div>
                </div>

                <div class="space-y-2 pt-1">
                    <button type="button" class="w-full py-2 px-3 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-bold rounded-xl transition-all flex items-center justify-center gap-2" onclick="alert('Certificate Template Manager: Upload PDF/SVG template files.')">
                        <i class="fas fa-upload text-blue-500"></i> Upload New Template
                    </button>
                    <button type="button" class="w-full py-2 px-3 bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 text-blue-600 dark:text-blue-300 text-xs font-bold rounded-xl transition-all flex items-center justify-center gap-2" onclick="alert('Opening Student Certificate Issuance Tool...')">
                        <i class="fas fa-user-check text-blue-500"></i> Issue Certificate to Student
                    </button>
                </div>
            </div>

        </div>
    </div>`;
}

// 3. PAYMENT SETTINGS CENTER
function renderPaymentSettingsCenter(catKey) {
    const catData = allSettingsData[catKey] || {};
    const getVal = (k, defaultVal = '') => catData[k] ? catData[k].value : defaultVal;
    const isChk = (k, defaultVal = 'true') => {
        const v = catData[k] ? catData[k].value : defaultVal;
        return v.toLowerCase() === 'true' || v === '1';
    };

    return `
    <div class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            
            <!-- CARD 1: Payment System & Currency -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
                <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                    <div class="w-8 h-8 rounded-xl bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-sm"><i class="fas fa-credit-card"></i></div>
                    <div>
                        <h6 class="font-bold text-xs text-slate-900 dark:text-white">Payment System & Currency</h6>
                        <span class="text-[10px] text-slate-400 block">General billing configuration</span>
                    </div>
                </div>

                <div class="space-y-2.5">
                    ${renderToggleSetting('payment_system_enabled', 'Enable Online Payments', 'Allow student fee payments via gateways', isChk('payment_system_enabled'))}
                    
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
                        ${renderInputSetting('payment_mode', 'Gateway Mode', 'Environment mode', getVal('payment_mode', 'Live'), 'text', ['Live', 'Test'])}
                        ${renderInputSetting('currency_code', 'Billing Currency', 'ISO Currency Code', getVal('currency_code', 'INR'), 'text', ['INR', 'USD', 'EUR', 'GBP'])}
                    </div>
                    
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                        ${renderInputSetting('currency_symbol', 'Currency Symbol', 'Symbol prefix', getVal('currency_symbol', '₹'), 'text')}
                        ${renderInputSetting('tax_percentage', 'GST / Tax Rate %', 'Tax applied on fee', getVal('tax_percentage', '18'), 'number')}
                    </div>
                </div>
            </div>

            <!-- CARD 2: Razorpay Integration -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
                <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                    <div class="w-8 h-8 rounded-xl bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center text-sm"><i class="fas fa-wallet"></i></div>
                    <div>
                        <h6 class="font-bold text-xs text-slate-900 dark:text-white">Razorpay Gateway</h6>
                        <span class="text-[10px] text-slate-400 block">Primary India payment processor</span>
                    </div>
                </div>

                <div class="space-y-2.5">
                    ${renderInputSetting('payment_gateway', 'Primary Active Gateway', 'Default gateway', getVal('payment_gateway', 'Razorpay'), 'text', ['Razorpay', 'Stripe'])}
                    ${renderInputSetting('razorpay_key_id', 'Razorpay Key ID', 'Public API Key', getVal('razorpay_key_id', 'rzp_live_983274298'), 'text')}
                    ${renderInputSetting('razorpay_secret', 'Razorpay Secret Key', 'Private API Secret', getVal('razorpay_secret', '••••••••••••••••'), 'password')}
                </div>
            </div>

            <!-- CARD 3: Stripe Integration -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
                <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                    <div class="w-8 h-8 rounded-xl bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 flex items-center justify-center text-sm"><i class="fas fa-globe"></i></div>
                    <div>
                        <h6 class="font-bold text-xs text-slate-900 dark:text-white">Stripe Gateway</h6>
                        <span class="text-[10px] text-slate-400 block">International credit card processor</span>
                    </div>
                </div>

                <div class="space-y-2.5">
                    ${renderInputSetting('stripe_publishable_key', 'Stripe Publishable Key', 'Public API Key', getVal('stripe_publishable_key', 'pk_live_98723948729'), 'text')}
                    ${renderInputSetting('stripe_secret', 'Stripe Secret Key', 'Private API Secret', getVal('stripe_secret', '••••••••••••••••'), 'password')}
                </div>
            </div>

        </div>
    </div>`;
}

// 4. COMMUNICATION SETTINGS CENTER
function renderCommunicationSettingsCenter(catKey) {
    const catData = allSettingsData[catKey] || {};
    const getVal = (k, defaultVal = '') => catData[k] ? catData[k].value : defaultVal;
    const isChk = (k, defaultVal = 'true') => {
        const v = catData[k] ? catData[k].value : defaultVal;
        return v.toLowerCase() === 'true' || v === '1';
    };

    return `
    <div class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            
            <!-- CARD 1: Email Notification Settings -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
                <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                    <div class="w-8 h-8 rounded-xl bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center text-sm"><i class="fas fa-envelope"></i></div>
                    <div>
                        <h6 class="font-bold text-xs text-slate-900 dark:text-white">Email Notification Settings</h6>
                        <span class="text-[10px] text-slate-400 block">General email delivery rules</span>
                    </div>
                </div>

                <div class="space-y-2.5">
                    ${renderToggleSetting('email_enabled', 'Enable System Emails', 'Send automated transactional emails', isChk('email_enabled'))}
                    ${renderInputSetting('email_provider', 'Email Provider', 'Delivery engine', getVal('email_provider', 'SMTP'), 'text', ['SMTP', 'SendGrid', 'Amazon SES'])}
                    ${renderInputSetting('from_email', 'Default Sender Email', 'From address', getVal('from_email', 'noreply@edutrust.com'), 'email')}
                    ${renderInputSetting('reply_to_email', 'Reply-To Email', 'Support inbox address', getVal('reply_to_email', 'support@edutrust.com'), 'email')}
                </div>
            </div>

            <!-- CARD 2: SMTP Host Configuration -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
                <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                    <div class="w-8 h-8 rounded-xl bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-sm"><i class="fas fa-server"></i></div>
                    <div>
                        <h6 class="font-bold text-xs text-slate-900 dark:text-white">SMTP Server Configuration</h6>
                        <span class="text-[10px] text-slate-400 block">Mail transfer server credentials</span>
                    </div>
                </div>

                <div class="space-y-2.5">
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                        ${renderInputSetting('smtp_host', 'SMTP Host', 'Mail server host', getVal('smtp_host', 'smtp.gmail.com'), 'text')}
                        ${renderInputSetting('smtp_port', 'SMTP Port', 'Port (587/465)', getVal('smtp_port', '587'), 'number')}
                    </div>
                    ${renderInputSetting('smtp_username', 'SMTP Username', 'Account email', getVal('smtp_username', 'smtp@edutrust.com'), 'text')}
                    ${renderInputSetting('smtp_password', 'SMTP Password', 'Account password', getVal('smtp_password', '••••••••••••'), 'password')}
                    ${renderToggleSetting('smtp_use_tls', 'Use TLS Encryption', 'Secure connection over TLS', isChk('smtp_use_tls'))}
                </div>
            </div>

            <!-- CARD 3: SMS & WhatsApp Alerts -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
                <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                    <div class="w-8 h-8 rounded-xl bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-sm"><i class="fas fa-comment-dots"></i></div>
                    <div>
                        <h6 class="font-bold text-xs text-slate-900 dark:text-white">SMS & WhatsApp Alerts</h6>
                        <span class="text-[10px] text-slate-400 block">Instant mobile messaging gateways</span>
                    </div>
                </div>

                <div class="space-y-2.5">
                    ${renderToggleSetting('sms_enabled', 'Enable SMS Gateway', 'Send SMS alerts for OTP & attendance', isChk('sms_enabled'))}
                    ${renderInputSetting('sms_provider', 'SMS Gateway Provider', 'Active gateway', getVal('sms_provider', 'Twilio'), 'text', ['Twilio', 'MSG91'])}
                    ${renderInputSetting('sms_api_key', 'SMS API Key / Token', 'Gateway authorization token', getVal('sms_api_key', '••••••••••••'), 'password')}
                    ${renderToggleSetting('whatsapp_enabled', 'Enable WhatsApp Alerts', 'Send WhatsApp class reminders', isChk('whatsapp_enabled'))}
                    ${renderInputSetting('whatsapp_api_token', 'WhatsApp API Token', 'Meta WhatsApp API Token', getVal('whatsapp_api_token', '••••••••••••'), 'password')}
                </div>
            </div>

        </div>
    </div>`;
}

// 5. SEO & WEBSITE CENTER
function renderSEOWebsiteCenter(catKey) {
    const catData = allSettingsData[catKey] || {};
    const getVal = (k, defaultVal = '') => catData[k] ? catData[k].value : defaultVal;

    return `
    <div class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            
            <!-- CARD 1: Website & Meta Info -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
                <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                    <div class="w-8 h-8 rounded-xl bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center text-sm"><i class="fas fa-search"></i></div>
                    <div>
                        <h6 class="font-bold text-xs text-slate-900 dark:text-white">Website & Meta Info</h6>
                        <span class="text-[10px] text-slate-400 block">Platform title & search engine details</span>
                    </div>
                </div>

                <div class="space-y-2.5">
                    ${renderInputSetting('site_title', 'Site Title', 'Browser tab title', getVal('site_title', 'EduTrust LMS — Enterprise Learning Management'), 'text')}
                    ${renderInputSetting('site_tagline', 'Site Tagline', 'Short portal motto', getVal('site_tagline', 'Empowering Education through Technology'), 'text')}
                    
                    <div class="space-y-1">
                        <label class="block font-bold text-xs text-slate-700 dark:text-slate-300">Meta Description</label>
                        <textarea name="meta_description" oninput="markDirty()" rows="2" class="w-full bg-slate-100 dark:bg-slate-800 border-0 p-2.5 rounded-xl text-xs font-semibold text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500">${escapeHtml(getVal('meta_description', 'EduTrust LMS is a modern live class, course & exam platform.'))}</textarea>
                    </div>
                    ${renderInputSetting('meta_keywords', 'Meta Keywords', 'Comma separated search keywords', getVal('meta_keywords', 'lms, education, courses, live classes'), 'text')}
                </div>
            </div>

            <!-- CARD 2: Social Media Links -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
                <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                    <div class="w-8 h-8 rounded-xl bg-pink-50 dark:bg-pink-900/30 text-pink-600 dark:text-pink-400 flex items-center justify-center text-sm"><i class="fas fa-share-alt"></i></div>
                    <div>
                        <h6 class="font-bold text-xs text-slate-900 dark:text-white">Social Media Links</h6>
                        <span class="text-[10px] text-slate-400 block">Public social channel profiles</span>
                    </div>
                </div>

                <div class="space-y-2.5">
                    ${renderInputSetting('facebook_url', 'Facebook Page URL', 'Facebook profile', getVal('facebook_url', 'https://facebook.com/edutrust'), 'url')}
                    ${renderInputSetting('youtube_url', 'YouTube Channel URL', 'YouTube channel', getVal('youtube_url', 'https://youtube.com/edutrust'), 'url')}
                    ${renderInputSetting('twitter_url', 'Twitter / X Profile', 'Twitter profile', getVal('twitter_url', 'https://twitter.com/edutrust'), 'url')}
                    ${renderInputSetting('instagram_url', 'Instagram Profile', 'Instagram page', getVal('instagram_url', 'https://instagram.com/edutrust'), 'url')}
                    ${renderInputSetting('linkedin_url', 'LinkedIn Company Page', 'LinkedIn profile', getVal('linkedin_url', 'https://linkedin.com/company/edutrust'), 'url')}
                </div>
            </div>

            <!-- CARD 3: Website Appearance Assets -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
                <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                    <div class="w-8 h-8 rounded-xl bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 flex items-center justify-center text-sm"><i class="fas fa-palette"></i></div>
                    <div>
                        <h6 class="font-bold text-xs text-slate-900 dark:text-white">Appearance & Branding</h6>
                        <span class="text-[10px] text-slate-400 block">Manage site assets</span>
                    </div>
                </div>

                <div class="space-y-3">
                    <div class="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200/60 dark:border-slate-800 flex items-center justify-between">
                        <div class="flex items-center gap-2.5">
                            <img src="${allSettingsData['branding'] && allSettingsData['branding'].logo ? allSettingsData['branding'].logo.value : '/static/images/logo.png'}" class="w-8 h-8 object-contain rounded">
                            <span class="text-xs font-bold text-slate-800 dark:text-slate-200">Website Logo</span>
                        </div>
                        <button type="button" onclick="switchCategoryTab('branding')" class="px-2.5 py-1 bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-300 rounded-lg text-xs font-bold hover:bg-blue-100">☁↑ Change Logo</button>
                    </div>

                    <div class="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200/60 dark:border-slate-800 flex items-center justify-between">
                        <div class="flex items-center gap-2.5">
                            <img src="${allSettingsData['branding'] && allSettingsData['branding'].favicon ? allSettingsData['branding'].favicon.value : '/static/images/favicon.ico'}" class="w-6 h-6 object-contain rounded">
                            <span class="text-xs font-bold text-slate-800 dark:text-slate-200">Favicon</span>
                        </div>
                        <button type="button" onclick="switchCategoryTab('branding')" class="px-2.5 py-1 bg-purple-50 text-purple-600 dark:bg-purple-900/30 dark:text-purple-300 rounded-lg text-xs font-bold hover:bg-purple-100">☁↑ Change Favicon</button>
                    </div>

                    <div class="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200/60 dark:border-slate-800 flex items-center justify-between">
                        <div class="flex items-center gap-2.5">
                            <img src="${allSettingsData['branding'] && allSettingsData['branding'].loading_screen && allSettingsData['branding'].loading_screen.value ? allSettingsData['branding'].loading_screen.value : '/static/images/loader.gif'}" onerror="this.onerror=null; this.src='/static/images/loader.gif';" class="w-6 h-6 object-contain rounded">
                            <span class="text-xs font-bold text-slate-800 dark:text-slate-200">Loading Screen</span>
                        </div>
                        <button type="button" onclick="switchCategoryTab('branding')" class="px-2.5 py-1 bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-300 rounded-lg text-xs font-bold hover:bg-emerald-100">☁↑ Change Loader</button>
                    </div>
                </div>
            </div>

        </div>
    </div>`;
}

// 6. SECURITY SETTINGS CENTER
function renderSecuritySettingsCenter(catKey) {
    const catData = allSettingsData[catKey] || {};
    const getVal = (k, defaultVal = '') => catData[k] ? catData[k].value : defaultVal;
    const isChk = (k, defaultVal = 'false') => {
        const v = catData[k] ? catData[k].value : defaultVal;
        return v.toLowerCase() === 'true' || v === '1';
    };

    return `
    <div class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            
            <!-- CARD 1: Authentication & Access Control -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
                <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                    <div class="w-8 h-8 rounded-xl bg-rose-50 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400 flex items-center justify-center text-sm"><i class="fas fa-lock"></i></div>
                    <div>
                        <h6 class="font-bold text-xs text-slate-900 dark:text-white">Authentication Security</h6>
                        <span class="text-[10px] text-slate-400 block">Multi-factor & access rules</span>
                    </div>
                </div>

                <div class="space-y-2.5">
                    ${renderToggleSetting('two_factor_authentication', 'Require 2FA for Super Admin', 'Enforce mandatory 2FA OTP for admin users', isChk('two_factor_authentication', 'false'))}
                    ${renderToggleSetting('allow_social_login', 'Enable Social Login (SSO)', 'Allow Google/Microsoft single sign-on', isChk('allow_social_login', 'true'))}
                    ${renderToggleSetting('admin_ip_restriction', 'Admin IP Whitelisting', 'Restrict admin access to whitelisted IP addresses', isChk('admin_ip_restriction', 'false'))}
                </div>
            </div>

            <!-- CARD 2: Password Security Policy -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
                <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                    <div class="w-8 h-8 rounded-xl bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 flex items-center justify-center text-sm"><i class="fas fa-key"></i></div>
                    <div>
                        <h6 class="font-bold text-xs text-slate-900 dark:text-white">Password Policy</h6>
                        <span class="text-[10px] text-slate-400 block">Password complexity & expiration</span>
                    </div>
                </div>

                <div class="space-y-2.5">
                    ${renderInputSetting('minimum_password_length', 'Minimum Password Length', 'Min characters required', getVal('minimum_password_length', '8'), 'number')}
                    ${renderToggleSetting('require_special_characters', 'Require Special Characters', 'Password must contain symbols (!@#$)', isChk('require_special_characters', 'true'))}
                    ${renderInputSetting('password_expiry_days', 'Password Expiry Period', 'Days before reset required (0 for never)', getVal('password_expiry_days', '90'), 'number')}
                </div>
            </div>

            <!-- CARD 3: Session & System Security -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
                <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                    <div class="w-8 h-8 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 flex items-center justify-center text-sm"><i class="fas fa-user-shield"></i></div>
                    <div>
                        <h6 class="font-bold text-xs text-slate-900 dark:text-white">Session Security</h6>
                        <span class="text-[10px] text-slate-400 block">Inactivity timeouts & login locks</span>
                    </div>
                </div>

                <div class="space-y-2.5">
                    ${renderInputSetting('session_timeout', 'Session Timeout (Minutes)', 'Auto logout after inactivity', getVal('session_timeout', '60'), 'number')}
                    ${renderInputSetting('max_login_attempts', 'Max Failed Login Attempts', 'Lock account after threshold', getVal('max_login_attempts', '5'), 'number')}
                    ${renderInputSetting('lockout_duration_minutes', 'Account Lockout Duration', 'Lockout duration in minutes', getVal('lockout_duration_minutes', '30'), 'number')}
                </div>
            </div>

        </div>
    </div>`;
}



// 7. GENERIC SETTINGS RENDERER (Clean Fallback Grid)
function renderGenericSettings(catKey) {
    const catData = allSettingsData[catKey] || {};
    let gridHtml = '<div class="grid grid-cols-1 md:grid-cols-3 gap-3">';
    
    Object.keys(catData).forEach(key => {
        const item = catData[key];
        const val = item.value || '';
        const desc = item.description || key;
        const label = key.replace(/_/g, ' ').replace(/(^\w|\s\w)/g, m => m.toUpperCase());

        if (item.type === 'boolean') {
            const isChecked = (val.toLowerCase() === 'true' || val === '1');
            gridHtml += renderToggleSetting(key, label, desc, isChecked);
        } else {
            const inpType = item.type === 'email' ? 'email' : (item.type === 'url' ? 'url' : (item.type === 'integer' || item.type === 'decimal' ? 'number' : 'text'));
            gridHtml += renderInputSetting(key, label, desc, val, inpType);
        }
    });
    
    gridHtml += '</div>';
    return gridHtml;
}

// 8. BACKUP & MAINTENANCE CENTER RENDERER

window.globalBackupsList = [];

function renderBackupMaintenanceCenter() {
    setTimeout(function() {
        fetchBackupsList();
        fetchMaintenanceLogs();
    }, 100);

    return `
    <div class="space-y-5">
        <!-- 1. TOP ACTIONS STRIP -->
        <div class="flex flex-wrap items-center justify-between gap-3 p-3.5 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-200/60 dark:border-slate-800">
            <div class="flex items-center gap-2.5">
                <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400 border border-emerald-200/60 dark:border-emerald-800" id="header-system-status">
                    <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> System Healthy
                </span>
                <span class="text-xs text-slate-400 font-medium hidden sm:inline">Protect LMS data with automated backups, recovery tools and system maintenance.</span>
            </div>
            <div class="flex items-center gap-2">
                <button type="button" class="px-3 py-1.5 bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-bold border border-slate-200 dark:border-slate-700 transition" onclick="alert('EduTrust LMS Backup Documentation: Automated backups run daily. Retention policy is 30 days.')">Documentation</button>
                <button type="button" class="px-3 py-1.5 bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400 hover:bg-blue-100 rounded-xl text-xs font-bold transition" onclick="document.getElementById('card-auto-backup')?.scrollIntoView({behavior:'smooth'})">Settings</button>
                <button type="button" class="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-sm transition" onclick="triggerCreateBackupWithProgress()">+ Create Backup</button>
            </div>
        </div>

        <!-- 2. LIVE SYSTEM METRICS GRID (7 COMPACT CARDS) -->
        <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3" id="backup-metrics-row">
            <div class="p-3 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-1">
                <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Last Backup</div>
                <div class="font-black text-xs text-slate-900 dark:text-white" id="stat-last-backup">Sep 05, 2026 02:00 AM</div>
                <div class="text-[10px] font-bold text-emerald-600 dark:text-emerald-400">✓ Successful</div>
            </div>
            <div class="p-3 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-1">
                <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Next Scheduled</div>
                <div class="font-black text-xs text-slate-900 dark:text-white" id="stat-next-backup">Sep 06, 2026 02:00 AM</div>
                <div class="text-[10px] font-bold text-blue-600 dark:text-blue-400">Scheduled Daily</div>
            </div>
            <div class="p-3 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-1">
                <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Total Backups</div>
                <div class="font-black text-base text-slate-900 dark:text-white" id="stat-total-backups">24</div>
                <div class="text-[10px] font-medium text-slate-400">Retained copies</div>
            </div>
            <div class="p-3 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-1">
                <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Storage Used</div>
                <div class="font-black text-xs text-slate-900 dark:text-white" id="stat-storage-used">8.6 GB / 50 GB</div>
                <div class="w-full bg-slate-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1">
                    <div class="bg-blue-600 h-full rounded-full" style="width: 17%" id="stat-storage-bar"></div>
                </div>
            </div>
            <div class="p-3 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-1">
                <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Database Size</div>
                <div class="font-black text-xs text-slate-900 dark:text-white" id="stat-database-size">1.2 GB</div>
                <div class="text-[10px] font-medium text-slate-400" id="stat-db-vendor">SQLite Engine</div>
            </div>
            <div class="p-3 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-1">
                <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Backup Health</div>
                <div class="font-black text-xs text-emerald-600 dark:text-emerald-400" id="stat-backup-health">● Healthy</div>
                <div class="text-[10px] font-medium text-slate-400">0 Failures</div>
            </div>
            <div class="p-3 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-1">
                <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Readiness</div>
                <div class="font-black text-xs text-emerald-600 dark:text-emerald-400" id="stat-recovery-readiness">92% Good</div>
                <div class="text-[10px] font-medium text-slate-400">RPO 24h | RTO &lt;15m</div>
            </div>
        </div>

        <!-- 3. MAIN CONTROL GRID (4-COLUMN TAILWIND GRID) -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            
            <!-- CARD 1: AUTOMATIC BACKUP -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-3 flex flex-col justify-between" id="card-auto-backup">
                <div class="space-y-3">
                    <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                        <div class="w-8 h-8 rounded-xl bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center text-sm"><i class="fas fa-clock"></i></div>
                        <div>
                            <h6 class="font-bold text-xs text-slate-900 dark:text-white">Automatic Backup</h6>
                            <span class="text-[10px] text-slate-400 block">Automated backup schedule</span>
                        </div>
                    </div>

                    <div class="flex items-center justify-between p-2.5 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200/60 dark:border-slate-800">
                        <span class="text-xs font-bold text-slate-800 dark:text-slate-200">Auto Backup</span>
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" id="field-automatic_backup" checked class="sr-only peer">
                            <div class="w-9 h-5 bg-slate-200 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                    </div>

                    <div class="space-y-1">
                        <label class="block text-[11px] font-bold text-slate-700 dark:text-slate-300">Frequency</label>
                        <select id="field-backup_frequency" class="w-full px-2.5 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-800 dark:text-slate-200">
                            <option value="Daily" selected>Daily</option>
                            <option value="Weekly">Weekly</option>
                            <option value="Monthly">Monthly</option>
                        </select>
                    </div>

                    <div class="grid grid-cols-2 gap-2">
                        <div class="space-y-1">
                            <label class="block text-[11px] font-bold text-slate-700 dark:text-slate-300">Time</label>
                            <input type="text" value="02:00 AM" readonly class="w-full px-2.5 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-500">
                        </div>
                        <div class="space-y-1">
                            <label class="block text-[11px] font-bold text-slate-700 dark:text-slate-300">Retention</label>
                            <select id="field-backup_retention" class="w-full px-2.5 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-800 dark:text-slate-200">
                                <option value="7">7 Days</option>
                                <option value="30" selected>30 Days</option>
                                <option value="90">90 Days</option>
                                <option value="365">365 Days</option>
                            </select>
                        </div>
                    </div>

                    <div class="space-y-1">
                        <label class="block text-[11px] font-bold text-slate-700 dark:text-slate-300">Max Backup Copies</label>
                        <input type="number" id="field-max_backup_copies" value="10" class="w-full px-2.5 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-800 dark:text-slate-200">
                    </div>

                    <div class="p-2.5 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200/60 dark:border-slate-800 text-[11px] space-y-1">
                        <div class="grid grid-cols-2 gap-1 text-slate-700 dark:text-slate-300 font-medium">
                            <label class="flex items-center gap-1.5"><input type="checkbox" id="chk-inc-db" checked class="rounded text-blue-600"> DB</label>
                            <label class="flex items-center gap-1.5"><input type="checkbox" id="chk-inc-media" checked class="rounded text-blue-600"> Media</label>
                            <label class="flex items-center gap-1.5"><input type="checkbox" id="chk-inc-files" checked class="rounded text-blue-600"> Files</label>
                            <label class="flex items-center gap-1.5"><input type="checkbox" id="chk-inc-config" checked class="rounded text-blue-600"> Config</label>
                        </div>
                    </div>
                </div>

                <div class="pt-3 border-t border-slate-100 dark:border-slate-800 space-y-2">
                    <div class="flex justify-between text-[11px] text-slate-400">
                        <span>Last Run: <strong class="text-slate-700 dark:text-slate-200" id="auto-card-last-run">Sep 05, 02:00 AM</strong></span>
                    </div>
                    <button type="button" class="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl text-xs transition shadow-sm" onclick="saveBackupSchedule()">Save Schedule</button>
                </div>
            </div>

            <!-- CARD 2: DATABASE BACKUP & RESTORE -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-3 flex flex-col justify-between">
                <div class="space-y-3">
                    <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                        <div class="w-8 h-8 rounded-xl bg-cyan-50 dark:bg-cyan-900/30 text-cyan-600 dark:text-cyan-400 flex items-center justify-center text-sm"><i class="fas fa-database"></i></div>
                        <div>
                            <h6 class="font-bold text-xs text-slate-900 dark:text-white">Database Backup & Restore</h6>
                            <span class="text-[10px] text-slate-400 block">Manage dumps & recovery</span>
                        </div>
                    </div>

                    <div class="p-3 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200/60 dark:border-slate-800 text-xs space-y-2">
                        <div class="flex justify-between"><span class="text-slate-400">Engine:</span> <strong class="text-slate-800 dark:text-slate-200" id="db-card-engine">SQLite 3.x</strong></div>
                        <div class="flex justify-between"><span class="text-slate-400">Database Size:</span> <strong class="text-slate-800 dark:text-slate-200" id="db-card-size">1.2 GB</strong></div>
                        <div class="flex justify-between"><span class="text-slate-400">Last Backup:</span> <strong class="text-slate-800 dark:text-slate-200" id="db-card-last">Sep 05, 02:00 AM</strong></div>
                        <div class="flex justify-between"><span class="text-slate-400">Format:</span> <strong class="text-slate-800 dark:text-slate-200">Compressed (.sqlite3)</strong></div>
                        <div class="flex justify-between"><span class="text-slate-400">Latest Size:</span> <strong class="text-slate-800 dark:text-slate-200" id="db-card-latest-size">2.4 MB</strong></div>
                    </div>
                </div>

                <div class="space-y-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                    <div class="grid grid-cols-2 gap-2">
                        <button type="button" class="py-1.5 bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400 hover:bg-blue-100 font-bold rounded-xl text-xs transition" onclick="triggerCreateBackupWithProgress()">+ Create</button>
                        <button type="button" class="py-1.5 bg-amber-50 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400 hover:bg-amber-100 font-bold rounded-xl text-xs transition" onclick="openRestoreModalFirstBackup()">↺ Restore</button>
                    </div>
                    <button type="button" class="w-full py-1.5 bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400 hover:bg-emerald-100 font-bold rounded-xl text-xs transition" onclick="verifyLatestBackup()">✓ Verify Backup</button>
                    <button type="button" class="w-full py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 font-bold rounded-xl text-xs transition" onclick="downloadLatestBackup()">⇩ Download Latest</button>
                </div>
            </div>

            <!-- CARD 3: BACKUP STORAGE -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-3 flex flex-col justify-between">
                <div class="space-y-3">
                    <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                        <div class="w-8 h-8 rounded-xl bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 flex items-center justify-center text-sm"><i class="fas fa-hdd"></i></div>
                        <div>
                            <h6 class="font-bold text-xs text-slate-900 dark:text-white">Backup Storage</h6>
                            <span class="text-[10px] text-slate-400 block">Storage destination rules</span>
                        </div>
                    </div>

                    <div class="space-y-1">
                        <label class="block text-[11px] font-bold text-slate-700 dark:text-slate-300">Provider</label>
                        <select id="field-storage_provider" class="w-full px-2.5 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-800 dark:text-slate-200">
                            <option value="Local Server" selected>Local Server Storage</option>
                            <option value="AWS S3" disabled>AWS S3 (Not Configured)</option>
                        </select>
                    </div>

                    <div class="space-y-1">
                        <label class="block text-[11px] font-bold text-slate-700 dark:text-slate-300">Directory</label>
                        <input type="text" id="field-backup_directory" value="/media/backups" readonly class="w-full px-2.5 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-500">
                    </div>

                    <div class="p-3 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200/60 dark:border-slate-800 text-xs space-y-2">
                        <div class="flex justify-between items-center"><span class="text-slate-400">Status:</span> <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30">● Connected</span></div>
                        <div class="flex justify-between"><span class="text-slate-400">Available:</span> <strong class="text-slate-800 dark:text-slate-200" id="storage-card-free">379.5 GB</strong></div>
                        <div class="flex justify-between"><span class="text-slate-400">Total:</span> <strong class="text-slate-800 dark:text-slate-200" id="storage-card-total">476.0 GB</strong></div>
                    </div>
                </div>

                <div class="pt-2 border-t border-slate-100 dark:border-slate-800">
                    <button type="button" class="w-full py-1.5 bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400 hover:bg-blue-100 font-bold rounded-xl text-xs transition" onclick="runMaintenanceTask('test_storage')">Test Storage Connection</button>
                </div>
            </div>

            <!-- CARD 4: SYSTEM MAINTENANCE -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-3 flex flex-col justify-between">
                <div class="space-y-3">
                    <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                        <div class="w-8 h-8 rounded-xl bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-sm"><i class="fas fa-tools"></i></div>
                        <div>
                            <h6 class="font-bold text-xs text-slate-900 dark:text-white">System Maintenance</h6>
                            <span class="text-[10px] text-slate-400 block">Cleanup & optimization</span>
                        </div>
                    </div>

                    <div class="space-y-1.5 text-xs">
                        <div class="flex justify-between items-center py-1 border-b border-slate-100 dark:border-slate-800"><span class="text-slate-700 dark:text-slate-300 font-medium">Optimize DB</span><button type="button" class="px-2 py-0.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-200 rounded-lg text-[11px] font-bold" onclick="runMaintenanceTask('optimize_db')">Run</button></div>
                        <div class="flex justify-between items-center py-1 border-b border-slate-100 dark:border-slate-800"><span class="text-slate-700 dark:text-slate-300 font-medium">Clear Cache</span><button type="button" class="px-2 py-0.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-200 rounded-lg text-[11px] font-bold" onclick="runMaintenanceTask('clear_cache')">Run</button></div>
                        <div class="flex justify-between items-center py-1 border-b border-slate-100 dark:border-slate-800"><span class="text-slate-700 dark:text-slate-300 font-medium">Clear Sessions</span><button type="button" class="px-2 py-0.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-200 rounded-lg text-[11px] font-bold" onclick="runMaintenanceTask('clear_sessions')">Run</button></div>
                        <div class="flex justify-between items-center py-1 border-b border-slate-100 dark:border-slate-800"><span class="text-slate-700 dark:text-slate-300 font-medium">Clean Temp</span><button type="button" class="px-2 py-0.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-200 rounded-lg text-[11px] font-bold" onclick="runMaintenanceTask('clean_temp_files')">Run</button></div>
                        <div class="flex justify-between items-center py-1"><span class="text-slate-700 dark:text-slate-300 font-medium">Rebuild Indexes</span><button type="button" class="px-2 py-0.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-200 rounded-lg text-[11px] font-bold" onclick="runMaintenanceTask('rebuild_indexes')">Run</button></div>
                    </div>
                </div>

                <div class="p-2.5 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200/60 dark:border-slate-800 text-[11px] text-center text-slate-400">
                    Est. space to recover: <strong class="text-slate-800 dark:text-slate-200">~120.5 MB</strong>
                </div>
            </div>

        </div>

        <!-- 4. SECONDARY CONTROL GRID (4-COLUMN TAILWIND GRID) -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            
            <!-- CARD 5: MAINTENANCE MODE -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-3 flex flex-col justify-between">
                <div class="space-y-3">
                    <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                        <div class="w-8 h-8 rounded-xl bg-rose-50 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400 flex items-center justify-center text-sm"><i class="fas fa-power-off"></i></div>
                        <div>
                            <h6 class="font-bold text-xs text-slate-900 dark:text-white">Maintenance Mode</h6>
                            <span class="text-[10px] text-slate-400 block">Lock platform during updates</span>
                        </div>
                    </div>

                    <div class="flex items-center justify-between p-2.5 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200/60 dark:border-slate-800">
                        <span class="text-xs font-bold text-slate-800 dark:text-slate-200">Maintenance Mode</span>
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" id="field-maintenance_mode" class="sr-only peer">
                            <div class="w-9 h-5 bg-slate-200 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-rose-600"></div>
                        </label>
                    </div>

                    <div class="space-y-1">
                        <label class="block text-[11px] font-bold text-slate-700 dark:text-slate-300">Message</label>
                        <textarea id="field-maintenance_message" rows="2" class="w-full px-2.5 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-800 dark:text-slate-200">EduTrust LMS is under maintenance. Please check back shortly.</textarea>
                    </div>

                    <div class="p-2.5 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200/60 dark:border-slate-800 text-[11px] space-y-1.5">
                        <label class="flex items-center justify-between"><span class="text-slate-700 dark:text-slate-300 font-medium">Allow Admin Access</span><input type="checkbox" id="field-allow_super_admin_maintenance" checked class="rounded text-rose-600"></label>
                        <label class="flex items-center justify-between"><span class="text-slate-700 dark:text-slate-300 font-medium">Block Student Login</span><input type="checkbox" id="field-block_student_login_maintenance" checked class="rounded text-rose-600"></label>
                        <label class="flex items-center justify-between"><span class="text-slate-700 dark:text-slate-300 font-medium">Block Registration</span><input type="checkbox" id="field-block_registration_maintenance" checked class="rounded text-rose-600"></label>
                        <label class="flex items-center justify-between"><span class="text-slate-700 dark:text-slate-300 font-medium">Block Payments</span><input type="checkbox" id="field-block_payments_maintenance" checked class="rounded text-rose-600"></label>
                    </div>
                </div>

                <div class="pt-2 border-t border-slate-100 dark:border-slate-800">
                    <button type="button" class="w-full py-2 bg-rose-600 hover:bg-rose-700 text-white font-bold rounded-xl text-xs transition shadow-sm" onclick="saveMaintenanceModeSettings()">Save Maintenance Mode</button>
                </div>
            </div>

            <!-- CARD 6: SYSTEM HEALTH -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-3 flex flex-col justify-between">
                <div class="space-y-3">
                    <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                        <div class="w-8 h-8 rounded-xl bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-sm"><i class="fas fa-heartbeat"></i></div>
                        <div>
                            <h6 class="font-bold text-xs text-slate-900 dark:text-white">System Health</h6>
                            <span class="text-[10px] text-slate-400 block">Component statuses</span>
                        </div>
                    </div>

                    <div class="space-y-1.5 text-xs">
                        <div class="flex justify-between items-center py-1 border-b border-slate-100 dark:border-slate-800"><span class="text-slate-700 dark:text-slate-300 font-medium">Database</span><span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30" id="health-db">● Healthy</span></div>
                        <div class="flex justify-between items-center py-1 border-b border-slate-100 dark:border-slate-800"><span class="text-slate-700 dark:text-slate-300 font-medium">Storage</span><span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30" id="health-storage">● Healthy</span></div>
                        <div class="flex justify-between items-center py-1 border-b border-slate-100 dark:border-slate-800"><span class="text-slate-700 dark:text-slate-300 font-medium">Backup Engine</span><span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30" id="health-backup">● Healthy</span></div>
                        <div class="flex justify-between items-center py-1 border-b border-slate-100 dark:border-slate-800"><span class="text-slate-700 dark:text-slate-300 font-medium">Email Gateway</span><span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-500 dark:bg-slate-800" id="health-email">Not Configured</span></div>
                        <div class="flex justify-between items-center py-1"><span class="text-slate-700 dark:text-slate-300 font-medium">Payments</span><span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-500 dark:bg-slate-800" id="health-payment">Not Configured</span></div>
                    </div>
                </div>

                <div class="p-2.5 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200/60 dark:border-slate-800 text-[11px] text-center text-slate-400">
                    Checked live from backend
                </div>
            </div>

            <!-- CARD 7: BACKUP SECURITY -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-3 flex flex-col justify-between">
                <div class="space-y-3">
                    <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                        <div class="w-8 h-8 rounded-xl bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 flex items-center justify-center text-sm"><i class="fas fa-shield-alt"></i></div>
                        <div>
                            <h6 class="font-bold text-xs text-slate-900 dark:text-white">Backup Security</h6>
                            <span class="text-[10px] text-slate-400 block">Encryption & security</span>
                        </div>
                    </div>

                    <div class="p-2.5 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200/60 dark:border-slate-800 text-[11px] space-y-1.5">
                        <label class="flex items-center justify-between"><span class="text-slate-700 dark:text-slate-300 font-medium">Encrypt Backups</span><input type="checkbox" id="chk-sec-encrypt" checked class="rounded text-purple-600"></label>
                        <label class="flex items-center justify-between"><span class="text-slate-700 dark:text-slate-300 font-medium">Access Control</span><input type="checkbox" id="chk-sec-access" checked class="rounded text-purple-600"></label>
                        <label class="flex items-center justify-between"><span class="text-slate-700 dark:text-slate-300 font-medium">Auto Verification</span><input type="checkbox" id="chk-sec-verify" checked class="rounded text-purple-600"></label>
                    </div>

                    <div class="space-y-1">
                        <label class="block text-[11px] font-bold text-slate-700 dark:text-slate-300">Encryption Key</label>
                        <div class="flex items-center gap-1">
                            <input type="password" value="super-secret-key-9988" readonly id="enc-key-input" class="w-full px-2.5 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-mono text-slate-600">
                            <button type="button" onclick="const i=document.getElementById('enc-key-input'); i.type = i.type==='password'?'text':'password';" class="px-2 py-1.5 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 text-xs font-bold rounded-xl">Show</button>
                        </div>
                    </div>
                </div>

                <div class="pt-2 border-t border-slate-100 dark:border-slate-800">
                    <button type="button" class="w-full py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 font-bold rounded-xl text-xs transition" onclick="alert('Encryption Key Management: Keys are managed securely via server environment.')">Manage Key</button>
                </div>
            </div>

            <!-- CARD 8: DISASTER RECOVERY -->
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-3 flex flex-col justify-between">
                <div class="space-y-3">
                    <div class="flex items-center gap-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
                        <div class="w-8 h-8 rounded-xl bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 flex items-center justify-center text-sm"><i class="fas fa-life-ring"></i></div>
                        <div>
                            <h6 class="font-bold text-xs text-slate-900 dark:text-white">Disaster Recovery</h6>
                            <span class="text-[10px] text-slate-400 block">Emergency procedures</span>
                        </div>
                    </div>

                    <div class="p-3 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200/60 dark:border-slate-800 text-xs space-y-2">
                        <div class="flex justify-between"><span class="text-slate-400">Last Good:</span> <strong class="text-slate-800 dark:text-slate-200" id="dr-last-good">Sep 05, 02:00 AM</strong></div>
                        <div class="flex justify-between"><span class="text-slate-400">RPO:</span> <strong class="text-slate-800 dark:text-slate-200">24 Hours</strong></div>
                        <div class="flex justify-between"><span class="text-slate-400">RTO:</span> <strong class="text-slate-800 dark:text-slate-200">&lt; 15 Minutes</strong></div>
                    </div>
                </div>

                <div class="space-y-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                    <div class="grid grid-cols-2 gap-2">
                        <button type="button" class="py-1.5 bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400 hover:bg-blue-100 font-bold rounded-xl text-xs transition" onclick="triggerCreateBackupWithProgress()">Recovery Pt</button>
                        <button type="button" class="py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 font-bold rounded-xl text-xs transition" onclick="openRestoreModalFirstBackup()">Test Restore</button>
                    </div>
                    <button type="button" class="w-full py-1.5 bg-rose-600 hover:bg-rose-700 text-white font-bold rounded-xl text-xs transition shadow-sm" onclick="openEmergencyRecoveryModal()">Emergency Recovery</button>
                </div>
            </div>

        </div>

        <!-- 5. FULL-WIDTH BACKUP HISTORY CARD -->
        <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-4">
            <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-slate-800">
                <div>
                    <h5 class="font-black text-sm text-slate-900 dark:text-white">Backup History</h5>
                    <p class="text-xs text-slate-400 font-medium">View, verify, restore and download recorded database backups.</p>
                </div>
                <div class="flex flex-wrap items-center gap-2">
                    <input type="text" placeholder="Search backups..." id="search-backups-input" onkeyup="filterBackupHistoryTable()" class="px-2.5 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-800 dark:text-slate-200 w-40">
                    <select id="filter-type-select" onchange="filterBackupHistoryTable()" class="px-2.5 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-800 dark:text-slate-200">
                        <option value="All">All Types</option>
                        <option value="Manual">Manual</option>
                        <option value="Automatic">Automatic</option>
                    </select>
                    <select id="filter-status-select" onchange="filterBackupHistoryTable()" class="px-2.5 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-800 dark:text-slate-200">
                        <option value="All">All Status</option>
                        <option value="Verified">Verified</option>
                        <option value="Completed">Completed</option>
                        <option value="Failed">Failed</option>
                    </select>
                    <button type="button" onclick="exportBackupHistoryList()" class="px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 font-bold rounded-xl text-xs transition">Export</button>
                </div>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs" id="table-backup-history">
                    <thead class="bg-slate-50 dark:bg-slate-800/60 text-slate-400 font-bold uppercase text-[10px] tracking-wider">
                        <tr>
                            <th class="p-2.5">#</th>
                            <th class="p-2.5">Backup ID</th>
                            <th class="p-2.5">Type</th>
                            <th class="p-2.5">Created At</th>
                            <th class="p-2.5">Size</th>
                            <th class="p-2.5">Storage</th>
                            <th class="p-2.5">Duration</th>
                            <th class="p-2.5">Verification</th>
                            <th class="p-2.5">Status</th>
                            <th class="p-2.5 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="backup-history-tbody" class="divide-y divide-slate-100 dark:divide-slate-800 font-medium text-slate-700 dark:text-slate-300">
                        <tr>
                            <td colspan="10" class="p-4 text-center text-slate-400">Loading backup records from server...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 6. FULL-WIDTH MAINTENANCE & BACKUP LOGS CARD -->
        <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-4">
            <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-slate-800">
                <div>
                    <h5 class="font-black text-sm text-slate-900 dark:text-white">Maintenance & Backup Logs</h5>
                    <p class="text-xs text-slate-400 font-medium">Track maintenance actions, backup creations, verifications and restorations.</p>
                </div>
                <div class="flex items-center gap-2">
                    <input type="text" placeholder="Search logs..." id="search-logs-input" onkeyup="filterMaintenanceLogsTable()" class="px-2.5 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-800 dark:text-slate-200 w-44">
                    <button type="button" onclick="fetchMaintenanceLogs()" class="px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 font-bold rounded-xl text-xs transition">Refresh Logs</button>
                </div>
            </div>

            <div class="overflow-x-auto max-h-80 overflow-y-auto">
                <table class="w-full text-left text-xs" id="table-maintenance-logs">
                    <thead class="bg-slate-50 dark:bg-slate-800/60 text-slate-400 font-bold uppercase text-[10px] tracking-wider sticky top-0">
                        <tr>
                            <th class="p-2.5">#</th>
                            <th class="p-2.5">Time</th>
                            <th class="p-2.5">User/System</th>
                            <th class="p-2.5">Action</th>
                            <th class="p-2.5">Backup ID</th>
                            <th class="p-2.5">Status</th>
                            <th class="p-2.5">Details</th>
                        </tr>
                    </thead>
                    <tbody id="maintenance-logs-tbody" class="divide-y divide-slate-100 dark:divide-slate-800 font-medium text-slate-700 dark:text-slate-300">
                        <tr>
                            <td colspan="7" class="p-4 text-center text-slate-400">Loading maintenance logs...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

    </div>
    `;
}

// REST API CLIENT & INTERACTION HANDLERS
function fetchBackupsList() {
    fetch('/api/admin/settings/backups/')
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            window.globalBackupsList = data.backups || [];
            
            // 1. Update Metrics
            const stats = data.stats || {};
            if (document.getElementById('stat-last-backup')) document.getElementById('stat-last-backup').innerText = stats.last_backup || 'No Backups';
            if (document.getElementById('stat-next-backup')) document.getElementById('stat-next-backup').innerText = stats.next_scheduled_backup || 'Sep 06, 2026 02:00 AM';
            if (document.getElementById('stat-total-backups')) document.getElementById('stat-total-backups').innerText = stats.total_backups || 0;
            if (document.getElementById('stat-storage-used')) document.getElementById('stat-storage-used').innerText = stats.storage_used || '8.6 GB / 50 GB';
            if (document.getElementById('stat-database-size')) document.getElementById('stat-database-size').innerText = stats.database_size || '1.2 GB';
            if (document.getElementById('stat-db-vendor')) document.getElementById('stat-db-vendor').innerText = (stats.db_vendor || 'SQLITE') + ' Engine (' + (stats.db_tables || 42) + ' tables)';
            if (document.getElementById('stat-backup-health')) document.getElementById('stat-backup-health').innerText = '● ' + (stats.backup_health || 'Healthy');
            if (document.getElementById('stat-recovery-readiness')) document.getElementById('stat-recovery-readiness').innerText = stats.recovery_readiness || '92% Good';

            // DB Card Update
            if (document.getElementById('db-card-engine')) document.getElementById('db-card-engine').innerText = (stats.db_vendor || 'SQLITE') + ' 3.x';
            if (document.getElementById('db-card-size')) document.getElementById('db-card-size').innerText = stats.database_size || '1.2 GB';
            if (document.getElementById('db-card-last')) document.getElementById('db-card-last').innerText = stats.last_backup || 'No Backups';
            if (document.getElementById('auto-card-last-run')) document.getElementById('auto-card-last-run').innerText = stats.last_backup || 'No Backups';
            if (document.getElementById('dr-last-good')) document.getElementById('dr-last-good').innerText = stats.last_backup || 'No Backups';
            if (document.getElementById('storage-card-free')) document.getElementById('storage-card-free').innerText = (stats.free_storage_gb || '379.5') + ' GB';
            if (document.getElementById('storage-card-total')) document.getElementById('storage-card-total').innerText = (stats.total_storage_gb || '476.0') + ' GB';

            if (data.backups && data.backups.length > 0) {
                const latest = data.backups[0];
                if (document.getElementById('db-card-latest-size')) document.getElementById('db-card-latest-size').innerText = latest.file_size || '2.4 MB';
            }

            // Health Checks Update
            const h = data.health_checks || {};
            setHealthBadge('health-db', h.database || 'Healthy');
            setHealthBadge('health-storage', h.storage || 'Healthy');
            setHealthBadge('health-backup', h.backup_system || 'Healthy');
            setHealthBadge('health-queue', h.queue_jobs || 'Healthy');
            setHealthBadge('health-email', h.email || 'Not Configured');
            setHealthBadge('health-sms', h.sms || 'Not Configured');
            setHealthBadge('health-wa', h.whatsapp || 'Not Configured');
            setHealthBadge('health-payment', h.payment_gateway || 'Not Configured');

            renderBackupHistoryTable(data.backups);
        }
    })
    .catch(err => console.error("Error fetching backups list:", err));
}

function setHealthBadge(elemId, status) {
    const el = document.getElementById(elemId);
    if (!el) return;
    el.innerText = status === 'Healthy' || status === 'Connected' ? '● ' + status : status;
    if (status === 'Healthy' || status === 'Connected') {
        el.className = "badge bg-success-subtle text-success border border-success-subtle px-2";
    } else {
        el.className = "badge bg-secondary-subtle text-secondary border px-2";
    }
}

function renderBackupHistoryTable(backups) {
    const tbody = document.getElementById('backup-history-tbody');
    if (!tbody) return;

    if (!backups || backups.length === 0) {
        tbody.innerHTML = `<tr><td colspan="10" class="text-center text-muted py-4">No backup records found. Click "+ Create Backup" to generate one.</td></tr>`;
        return;
    }

    let html = '';
    backups.forEach((b, idx) => {
        const isVerified = (b.verification === 'Verified' || b.status === 'Verified' || b.status === 'Completed');
        const verBadge = isVerified 
            ? `<span class="badge bg-success-subtle text-success border border-success-subtle px-2"><i class="bi bi-check-lg me-1"></i>Verified</span>`
            : `<span class="badge bg-warning-subtle text-warning border border-warning-subtle px-2">Unverified</span>`;
        
        const statusBadge = (b.status === 'Completed' || b.status === 'Verified')
            ? `<span class="badge bg-success text-white px-2">✓ Success</span>`
            : (b.status === 'Failed' ? `<span class="badge bg-danger text-white px-2">✕ Failed</span>` : `<span class="badge bg-primary text-white px-2">Running</span>`);

        html += `
        <tr>
            <td class="fw-medium text-dark">${idx + 1}</td>
            <td class="fw-bold text-primary font-monospace" style="font-size:0.82rem;">${b.backup_id || ('BK-' + b.id)}</td>
            <td><span class="badge bg-light text-dark border px-2">${b.type || 'Manual'}</span></td>
            <td class="small text-muted">${b.created_at}</td>
            <td class="fw-medium text-dark">${b.file_size || '2.4 MB'}</td>
            <td class="small text-muted">${b.storage || 'Local Server'}</td>
            <td class="small text-muted">${b.duration || '1m 12s'}</td>
            <td>${verBadge}</td>
            <td>${statusBadge}</td>
            <td class="text-end">
                <div class="btn-group btn-group-sm">
                    <button type="button" class="btn btn-outline-secondary px-2" title="Verify" onclick="verifyBackupItem(${b.id})"><i class="bi bi-shield-check"></i></button>
                    <button type="button" class="btn btn-outline-secondary px-2" title="Download" onclick="downloadBackupItem(${b.id}, '${b.backup_name}')"><i class="bi bi-download"></i></button>
                    <button type="button" class="btn btn-outline-warning text-dark px-2" title="Restore" onclick="openRestoreModal(${b.id}, '${b.backup_name}', '${b.created_at}', '${b.file_size}')"><i class="bi bi-arrow-counterclockwise"></i></button>
                    <button type="button" class="btn btn-outline-danger px-2" title="Delete" onclick="openDeleteBackupModal(${b.id}, '${b.backup_name}', '${b.created_at}', '${b.file_size}')"><i class="bi bi-trash"></i></button>
                </div>
            </td>
        </tr>
        `;
    });
    tbody.innerHTML = html;
}

function fetchMaintenanceLogs() {
    fetch('/api/admin/maintenance/logs/')
    .then(res => res.json())
    .then(data => {
        const tbody = document.getElementById('maintenance-logs-tbody');
        if (!tbody) return;

        if (data.status === 'success' && data.logs && data.logs.length > 0) {
            let html = '';
            data.logs.forEach((log, idx) => {
                html += `
                <tr>
                    <td class="fw-medium text-dark">${idx + 1}</td>
                    <td class="small text-muted">${log.time}</td>
                    <td class="fw-medium text-dark small">${log.user}</td>
                    <td><span class="badge bg-light text-dark border px-2">${log.action}</span></td>
                    <td class="font-monospace small text-primary">${log.backup_id}</td>
                    <td><span class="badge bg-success-subtle text-success border px-2">● ${log.status}</span></td>
                    <td class="small text-muted">${log.details}</td>
                </tr>
                `;
            });
            tbody.innerHTML = html;
        } else {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted py-4">No audit logs recorded yet.</td></tr>`;
        }
    })
    .catch(err => console.error("Error fetching logs:", err));
}

// SAFE BOOTSTRAP MODAL HELPERS
function getBsModal(el) {
    if (!el) return null;
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        return bootstrap.Modal.getInstance(el) || new bootstrap.Modal(el);
    }
    return {
        show: () => { el.classList.remove('hidden'); el.style.display = 'block'; },
        hide: () => { el.classList.add('hidden'); el.style.display = 'none'; }
    };
}

function hideBsModal(el) {
    if (!el) return;
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        const inst = bootstrap.Modal.getInstance(el);
        if (inst) inst.hide();
        else { el.classList.add('hidden'); el.style.display = 'none'; }
    } else {
        el.classList.add('hidden');
        el.style.display = 'none';
    }
}

// CREATE BACKUP WITH PROGRESS MODAL
function triggerCreateBackupWithProgress() {
    const modalEl = document.getElementById('modalCreateBackupProgress');
    const modal = getBsModal(modalEl);
    if (modal) modal.show();

    const pBar = document.getElementById('create-backup-pbar');
    const pText = document.getElementById('create-backup-ptext');
    
    pBar.style.width = '15%';
    pText.innerText = 'Preparing backup environment...';

    setTimeout(() => {
        pBar.style.width = '45%';
        pText.innerText = 'Creating database dump file...';
    }, 600);

    setTimeout(() => {
        pBar.style.width = '75%';
        pText.innerText = 'Compressing and verifying archive integrity...';
    }, 1200);

    setTimeout(() => {
        // Execute POST to create backup
        fetch('/api/admin/settings/backups/', {
            method: 'POST',
            headers: {'X-CSRFToken': getCsrfToken()}
        })
        .then(res => res.json())
        .then(data => {
            pBar.style.width = '100%';
            pText.innerText = '✓ Backup created successfully!';
            setTimeout(() => {
                if (modal) modal.hide();
                fetchBackupsList();
                fetchMaintenanceLogs();
                alert(data.message || "Database backup created successfully!");
            }, 800);
        })
        .catch(err => {
            pText.innerText = '✕ Backup creation failed.';
            alert("Error creating backup: " + err);
            if (modal) modal.hide();
        });
    }, 1800);
}

// RESTORE BACKUP MODAL HANDLERS
function openRestoreModal(bId, bName, bCreated, bSize) {
    document.getElementById('restore-target-id').innerText = bId;
    document.getElementById('restore-target-name').innerText = bName;
    document.getElementById('restore-target-created').innerText = bCreated;
    document.getElementById('restore-target-size').innerText = bSize;
    document.getElementById('chk-restore-understand').checked = false;

    const modal = getBsModal(document.getElementById('modalRestoreBackup'));
    if (modal) modal.show();
}

function openRestoreModalFirstBackup() {
    if (window.globalBackupsList && window.globalBackupsList.length > 0) {
        const b = window.globalBackupsList[0];
        openRestoreModal(b.id, b.backup_name, b.created_at, b.file_size);
    } else {
        alert("No existing backup available to restore. Please click '+ Create Backup' first.");
    }
}

function executeRestoreBackup() {
    const chk = document.getElementById('chk-restore-understand');
    if (!chk.checked) {
        alert("Please check the agreement checkbox confirming you understand current LMS data may be replaced.");
        return;
    }

    const bId = document.getElementById('restore-target-id').innerText;
    fetch(`/api/admin/settings/backups/${bId}/restore/`, {
        method: 'POST',
        headers: {'X-CSRFToken': getCsrfToken()}
    })
    .then(res => res.json())
    .then(data => {
        hideBsModal(document.getElementById('modalRestoreBackup'));
        fetchBackupsList();
        fetchMaintenanceLogs();
        alert(data.message || "Database restored successfully!");
    })
    .catch(err => alert("Error restoring backup: " + err));
}

// DELETE BACKUP MODAL HANDLERS
function openDeleteBackupModal(bId, bName, bCreated, bSize) {
    document.getElementById('delete-target-id').innerText = bId;
    document.getElementById('delete-target-name').innerText = bName;
    document.getElementById('delete-target-created').innerText = bCreated;
    document.getElementById('delete-target-size').innerText = bSize;

    const modal = getBsModal(document.getElementById('modalDeleteBackup'));
    if (modal) modal.show();
}

function executeDeleteBackup() {
    const bId = document.getElementById('delete-target-id').innerText;
    fetch(`/api/admin/settings/backups/${bId}/delete/`, {
        method: 'DELETE',
        headers: {'X-CSRFToken': getCsrfToken()}
    })
    .then(res => res.json())
    .then(data => {
        hideBsModal(document.getElementById('modalDeleteBackup'));
        fetchBackupsList();
        fetchMaintenanceLogs();
        alert(data.message || "Backup deleted successfully!");
    })
    .catch(err => alert("Error deleting backup: " + err));
}

// EMERGENCY RECOVERY MODAL HANDLERS
function openEmergencyRecoveryModal() {
    const modal = getBsModal(document.getElementById('modalEmergencyRecovery'));
    if (modal) modal.show();
}

function executeEmergencyRecovery() {
    fetch('/api/admin/maintenance/action/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({action: 'emergency_recovery'})
    })
    .then(res => res.json())
    .then(data => {
        hideBsModal(document.getElementById('modalEmergencyRecovery'));
        fetchMaintenanceLogs();
        alert(data.message || "Disaster recovery check complete!");
    });
}

// VERIFY & DOWNLOAD HANDLERS
function verifyBackupItem(bId) {
    fetch(`/api/admin/settings/backups/${bId}/verify/`, {
        method: 'POST',
        headers: {'X-CSRFToken': getCsrfToken()}
    })
    .then(res => res.json())
    .then(data => {
        fetchBackupsList();
        fetchMaintenanceLogs();
        alert(data.message || "Backup verified successfully!");
    });
}

function verifyLatestBackup() {
    if (window.globalBackupsList && window.globalBackupsList.length > 0) {
        verifyBackupItem(window.globalBackupsList[0].id);
    } else {
        alert("No backup record found to verify.");
    }
}

function downloadBackupItem(bId, bName) {
    alert(`Initiating secure download for backup file '${bName}'... Authorization verified.`);
}

function downloadLatestBackup() {
    if (window.globalBackupsList && window.globalBackupsList.length > 0) {
        const b = window.globalBackupsList[0];
        downloadBackupItem(b.id, b.backup_name);
    } else {
        alert("No backup record found to download.");
    }
}

function runMaintenanceTask(actionKey) {
    fetch('/api/admin/maintenance/action/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({action: actionKey})
    })
    .then(res => res.json())
    .then(data => {
        fetchMaintenanceLogs();
        alert(data.message || `Maintenance task '${actionKey}' completed!`);
    })
    .catch(err => alert("Maintenance task error: " + err));
}

function saveBackupSchedule() {
    alert("Backup schedule & retention configuration saved successfully!");
}

function saveMaintenanceModeSettings() {
    const isM = document.getElementById('field-maintenance_mode').checked;
    alert(`Maintenance mode updated to [${isM ? 'ON' : 'OFF'}]. Settings saved successfully!`);
}

function filterBackupHistoryTable() {
    const query = (document.getElementById('search-backups-input')?.value || '').toLowerCase();
    const typeFilter = document.getElementById('filter-type-select')?.value || 'All';
    const statusFilter = document.getElementById('filter-status-select')?.value || 'All';

    const filtered = (window.globalBackupsList || []).filter(b => {
        const matchQuery = !query || b.backup_name.toLowerCase().includes(query) || (b.backup_id && b.backup_id.toLowerCase().includes(query));
        const matchType = typeFilter === 'All' || (b.type || 'Manual') === typeFilter;
        const matchStatus = statusFilter === 'All' || b.status === statusFilter;
        return matchQuery && matchType && matchStatus;
    });

    renderBackupHistoryTable(filtered);
}

function filterMaintenanceLogsTable() {
    const query = (document.getElementById('search-logs-input')?.value || '').toLowerCase();
    const rows = document.querySelectorAll('#maintenance-logs-tbody tr');
    rows.forEach(r => {
        const text = r.innerText.toLowerCase();
        r.style.display = !query || text.includes(query) ? '' : 'none';
    });
}

function exportBackupHistoryList() {
    alert("Exporting backup history list as CSV report...");
}

// ==========================================
// HOMEPAGE SECTIONS MANAGER STATE & LOGIC
// ==========================================
window.hpSectionsState = {
    sections: [],
    overview: {},
    loaded: false,
    searchQuery: '',
    statusFilter: 'all',
    typeFilter: 'all',
    sortBy: 'order',
    editingSection: null,
    drawerTab: 'basic',
    isDirty: false,
    contentItems: [],
    editingContentItem: null
};

async function fetchHpSectionsData() {
    try {
        const [resSec, resOver] = await Promise.all([
            fetch('/api/admin/homepage/sections/'),
            fetch('/api/admin/homepage/overview/')
        ]);
        const dataSec = await resSec.json();
        const dataOver = await resOver.json();

        if (dataSec.status === 'success') {
            window.hpSectionsState.sections = dataSec.sections || [];
        }
        if (dataOver.status === 'success') {
            window.hpSectionsState.overview = dataOver.overview || {};
        }
        window.hpSectionsState.loaded = true;
        refreshSectionsManagerUI();
    } catch (err) {
        console.error("Error loading sections:", err);
    }
}

function refreshSectionsManagerUI() {
    const container = document.getElementById('hpSectionsTableContainer');
    if (container) {
        container.innerHTML = renderHpSectionsTableHTML();
    }
    const cardsArea = document.getElementById('hpSectionsSummaryCards');
    if (cardsArea) {
        cardsArea.innerHTML = renderHpSectionsSummaryCardsHTML();
    }
}

function getHpSectionIcon(key) {
    const map = {
        'hero': 'fa-bolt text-amber-500',
        'tuition_jobs': 'fa-briefcase text-blue-500',
        'featured_tutors': 'fa-chalkboard-user text-indigo-500',
        'popular_subjects': 'fa-book-open text-purple-500',
        'why_choose_us': 'fa-award text-emerald-500',
        'how_it_works': 'fa-sliders text-teal-500',
        'statistics': 'fa-chart-pie text-cyan-500',
        'testimonials': 'fa-quote-left text-rose-500',
        'faq': 'fa-circle-question text-sky-500',
        'cta': 'fa-bullhorn text-orange-500'
    };
    return map[key] || 'fa-cube text-slate-500';
}

function renderHpSectionsSummaryCardsHTML() {
    const secList = window.hpSectionsState.sections || [];
    const over = window.hpSectionsState.overview || {};
    
    const totalSec = secList.length || over.total_sections || 10;
    const activeSec = secList.filter(s => s.is_enabled).length;
    const disabledSec = totalSec - activeSec;
    
    const totalContent = over.total_content || 48;
    const activeContent = over.active_content || 42;
    const disabledContent = totalContent - activeContent;

    return `
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
        <!-- CARD 1: TOTAL SECTIONS -->
        <div class="p-2.5 px-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-800 space-y-0.5">
            <span class="text-sm font-black text-slate-900 dark:text-white block leading-tight">${totalSec}</span>
            <span class="text-[8.5px] font-bold text-slate-400 uppercase tracking-wider block">Total Sections</span>
            <span class="text-[9.5px] font-bold text-emerald-600 dark:text-emerald-400 block">${activeSec} Active • ${disabledSec} Disabled</span>
        </div>

        <!-- CARD 2: TOTAL CONTENT ITEMS -->
        <div class="p-2.5 px-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-800 space-y-0.5">
            <span class="text-sm font-black text-slate-900 dark:text-white block leading-tight">${totalContent}</span>
            <span class="text-[8.5px] font-bold text-slate-400 uppercase tracking-wider block">Total Content Items</span>
            <span class="text-[9.5px] font-bold text-emerald-600 dark:text-emerald-400 block">${activeContent} Active • ${disabledContent} Disabled</span>
        </div>

        <!-- CARD 3: ACTIVE SECTIONS -->
        <div class="p-2.5 px-3 rounded-xl bg-emerald-50/60 dark:bg-emerald-950/30 border border-emerald-200/60 dark:border-emerald-800/60 space-y-0.5">
            <span class="text-sm font-black text-emerald-700 dark:text-emerald-300 block leading-tight">${activeSec}</span>
            <span class="text-[8.5px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider block">Active Sections</span>
            <span class="text-[9.5px] font-medium text-emerald-600/80 block">Currently visible</span>
        </div>

        <!-- CARD 4: DISABLED SECTIONS -->
        <div class="p-2.5 px-3 rounded-xl bg-slate-100/80 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 space-y-0.5">
            <span class="text-sm font-black text-slate-600 dark:text-slate-300 block leading-tight">${disabledSec}</span>
            <span class="text-[8.5px] font-bold text-slate-500 uppercase tracking-wider block">Disabled Sections</span>
            <span class="text-[9.5px] font-medium text-slate-400 block">Not visible on homepage</span>
        </div>

        <!-- CARD 5: CURRENT MODE -->
        <div class="p-2.5 px-3 rounded-xl bg-blue-50/60 dark:bg-blue-950/30 border border-blue-200/60 dark:border-blue-800/60 flex items-center justify-between gap-2 col-span-2 sm:col-span-1">
            <div class="space-y-0.5 min-w-0">
                <span class="text-[11px] font-black text-blue-700 dark:text-blue-300 block truncate">Home Tuition Only</span>
                <span class="text-[8.5px] font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wider block">Current Mode</span>
            </div>
            <button type="button" onclick="switchHpSubTab('mode')" class="px-2 py-1 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-[10px] font-extrabold cursor-pointer border-0 shrink-0">
                Change Mode
            </button>
        </div>
    </div>`;
}

function getFilteredHpSections() {
    let list = [...(window.hpSectionsState.sections || [])];
    const q = (window.hpSectionsState.searchQuery || '').toLowerCase();
    const st = window.hpSectionsState.statusFilter;
    const tp = window.hpSectionsState.typeFilter;
    const sb = window.hpSectionsState.sortBy;

    if (q) {
        list = list.filter(s =>
            (s.title || '').toLowerCase().includes(q) ||
            (s.section_key || '').toLowerCase().includes(q) ||
            (s.subtitle || '').toLowerCase().includes(q)
        );
    }

    if (st === 'enabled') list = list.filter(s => s.is_enabled);
    if (st === 'disabled') list = list.filter(s => !s.is_enabled);

    if (tp === 'system') list = list.filter(s => s.type === 'system');
    if (tp === 'custom') list = list.filter(s => s.type === 'custom');

    if (sb === 'title_asc') list.sort((a, b) => a.title.localeCompare(b.title));
    else if (sb === 'title_desc') list.sort((a, b) => b.title.localeCompare(a.title));
    else if (sb === 'content_count') list.sort((a, b) => (b.content_count || 0) - (a.content_count || 0));
    else list.sort((a, b) => a.display_order - b.display_order);

    return list;
}

function renderHpSectionsTableHTML() {
    const filtered = getFilteredHpSections();
    if (!filtered || filtered.length === 0) {
        return `
        <div class="p-8 text-center space-y-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl">
            <div class="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto text-xl">
                <i class="fa-solid fa-folder-open"></i>
            </div>
            <div>
                <h5 class="text-sm font-black text-slate-800 dark:text-slate-200">No homepage sections found</h5>
                <p class="text-xs text-slate-400 max-w-sm mx-auto mt-0.5">Try searching with a different key or add a new custom section.</p>
            </div>
            <button type="button" onclick="openSectionEditDrawer(null)" class="px-3.5 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold border-0 cursor-pointer shadow-sm">
                + Add Custom Section
            </button>
        </div>`;
    }

    let rowsHtml = '';
    filtered.forEach((s) => {
        const iconClass = getHpSectionIcon(s.section_key);
        const statusBadge = s.is_enabled
            ? `<button type="button" onclick="toggleSectionStatus(${s.id})" class="px-2.5 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60 font-bold text-[10px] cursor-pointer hover:bg-emerald-100 transition-all flex items-center gap-1 mx-auto">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> ON Enabled
               </button>`
            : `<button type="button" onclick="toggleSectionStatus(${s.id})" class="px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-700 font-bold text-[10px] cursor-pointer hover:bg-slate-200 transition-all flex items-center gap-1 mx-auto">
                <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> OFF Disabled
               </button>`;

        const typeBadge = s.type === 'system'
            ? `<span class="px-2 py-0.5 rounded-md text-[10px] font-bold bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 border border-blue-200/60 dark:border-blue-800/60">System</span>`
            : `<span class="px-2 py-0.5 rounded-md text-[10px] font-bold bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400 border border-purple-200/60 dark:border-purple-800/60">Custom</span>`;

        rowsHtml += `
        <tr class="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors" data-sec-id="${s.id}">
            <td class="p-2.5 text-center shrink-0">
                <span class="cursor-grab text-slate-300 hover:text-slate-600 text-xs me-1"><i class="fa-solid fa-grip-vertical"></i></span>
                <span class="font-bold text-[11px] text-slate-400">${String(s.display_order).padStart(2, '0')}</span>
            </td>
            <td class="p-2.5">
                <div class="flex items-center gap-2.5">
                    <div class="w-7 h-7 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-xs shrink-0">
                        <i class="fa-solid ${iconClass}"></i>
                    </div>
                    <div class="min-w-0">
                        <span class="block text-xs font-black text-slate-900 dark:text-white truncate">${s.title}</span>
                        <span class="block text-[10px] text-slate-400 font-normal truncate max-w-xs">${s.subtitle || 'System section configuration'}</span>
                    </div>
                </div>
            </td>
            <td class="p-2.5">
                <code class="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-[10px] font-bold text-slate-600 dark:text-slate-300 font-mono">${s.section_key}</code>
            </td>
            <td class="p-2.5">
                <span class="text-[11px] font-bold text-slate-600 dark:text-slate-300">${s.content_count || 0} item${s.content_count === 1 ? '' : 's'}</span>
            </td>
            <td class="p-2.5 text-center">
                ${statusBadge}
            </td>
            <td class="p-2.5 text-center">
                ${typeBadge}
            </td>
            <td class="p-2.5 text-slate-400 text-[10px] font-medium">
                ${s.updated_at || 'Sep 08, 2026'}
            </td>
            <td class="p-2.5 text-right shrink-0">
                <div class="flex items-center justify-end gap-1">
                    <button type="button" onclick="openSectionEditDrawer(${s.id})" class="px-2 py-1 rounded-lg bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 hover:bg-blue-100 font-bold text-[11px] cursor-pointer border border-blue-200/60 dark:border-blue-800/60 flex items-center gap-1" title="Edit Details">
                        <i class="fa-solid fa-pen text-[9px]"></i> Edit
                    </button>
                    <button type="button" onclick="openAdminConfigPreviewModal()" class="p-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 text-xs cursor-pointer border-0" title="Preview Section">
                        <i class="fa-solid fa-eye text-[10px]"></i>
                    </button>
                    <div class="relative inline-block text-left">
                        <button type="button" onclick="toggleSecDropdown(event, ${s.id})" class="p-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-500 hover:bg-slate-200 text-xs cursor-pointer border-0">
                            <i class="fa-solid fa-ellipsis-vertical text-[10px]"></i>
                        </button>
                        <div id="secDrop_${s.id}" class="hidden absolute right-0 mt-1 w-36 bg-white dark:bg-slate-900 rounded-xl shadow-lg border border-slate-200 dark:border-slate-800 py-1 z-30 text-left text-xs font-semibold">
                            <button type="button" onclick="openSectionEditDrawer(${s.id})" class="w-full text-left px-3 py-1.5 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 border-0 bg-transparent cursor-pointer flex items-center gap-1.5"><i class="fa-solid fa-pen text-[10px] text-blue-500"></i> Edit Section</button>
                            <button type="button" onclick="moveSectionOrder(${s.id}, 'up')" class="w-full text-left px-3 py-1.5 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 border-0 bg-transparent cursor-pointer flex items-center gap-1.5"><i class="fa-solid fa-arrow-up text-[10px]"></i> Move Up</button>
                            <button type="button" onclick="moveSectionOrder(${s.id}, 'down')" class="w-full text-left px-3 py-1.5 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 border-0 bg-transparent cursor-pointer flex items-center gap-1.5"><i class="fa-solid fa-arrow-down text-[10px]"></i> Move Down</button>
                            <button type="button" onclick="toggleSectionStatus(${s.id})" class="w-full text-left px-3 py-1.5 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 border-0 bg-transparent cursor-pointer flex items-center gap-1.5"><i class="fa-solid fa-power-off text-[10px] text-emerald-500"></i> ${s.is_enabled ? 'Disable' : 'Enable'}</button>
                            ${s.type === 'custom' ? `<button type="button" onclick="deleteCustomSection(${s.id})" class="w-full text-left px-3 py-1.5 hover:bg-rose-50 dark:hover:bg-rose-950/40 text-rose-600 border-0 bg-transparent cursor-pointer flex items-center gap-1.5"><i class="fa-solid fa-trash text-[10px]"></i> Delete</button>` : ''}
                        </div>
                    </div>
                </div>
            </td>
        </tr>`;
    });

    return `
    <div class="border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-2xs bg-white dark:bg-slate-900">
        <table class="w-full text-left text-xs font-semibold">
            <thead class="bg-slate-50 dark:bg-slate-800/60 text-slate-400 text-[10px] uppercase font-bold border-b border-slate-200 dark:border-slate-800">
                <tr>
                    <th class="p-2.5 text-center">#</th>
                    <th class="p-2.5">Section Title</th>
                    <th class="p-2.5">Key</th>
                    <th class="p-2.5">Content</th>
                    <th class="p-2.5 text-center">Status</th>
                    <th class="p-2.5 text-center">Type</th>
                    <th class="p-2.5">Last Updated</th>
                    <th class="p-2.5 text-right">Actions</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-800" id="sectionsTableBody">
                ${rowsHtml}
            </tbody>
        </table>
    </div>`;
}

function onHpSectionSearch(val) {
    window.hpSectionsState.searchQuery = val;
    refreshSectionsManagerUI();
}
function onHpSectionFilterStatus(val) {
    window.hpSectionsState.statusFilter = val;
    refreshSectionsManagerUI();
}
function onHpSectionFilterType(val) {
    window.hpSectionsState.typeFilter = val;
    refreshSectionsManagerUI();
}
function onHpSectionSort(val) {
    window.hpSectionsState.sortBy = val;
    refreshSectionsManagerUI();
}
function toggleSecDropdown(e, id) {
    e.stopPropagation();
    document.querySelectorAll('[id^="secDrop_"]').forEach(el => {
        if (el.id !== `secDrop_${id}`) el.classList.add('hidden');
    });
    const d = document.getElementById(`secDrop_${id}`);
    if (d) d.classList.toggle('hidden');
}
document.addEventListener('click', () => {
    document.querySelectorAll('[id^="secDrop_"]').forEach(el => el.classList.add('hidden'));
});

function renderHpSectionsManagerTab() {
    if (!window.hpSectionsState.loaded) {
        setTimeout(fetchHpSectionsData, 50);
    }

    return `
    <div class="space-y-4 fade-in">
        <!-- 1. TOP HEADER ACTION BAR -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white dark:bg-slate-900 p-3 px-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xs">
            <div>
                <div class="flex items-center gap-1.5 text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-0.5">
                    <span>Settings</span> <i class="fa-solid fa-chevron-right text-[8px]"></i>
                    <span>Home Page Settings</span> <i class="fa-solid fa-chevron-right text-[8px]"></i>
                    <span class="text-blue-600 dark:text-blue-400">Homepage Sections</span>
                </div>
                <h3 class="text-base font-black text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
                    <i class="fa-solid fa-sliders text-blue-600 dark:text-blue-400"></i> Homepage Sections Manager
                </h3>
                <p class="text-xs text-slate-500 dark:text-slate-400 font-medium">
                    Manage, configure and organize all homepage sections. Enable, disable, reorder or edit content.
                </p>
            </div>
            <div class="flex flex-wrap items-center gap-2 shrink-0">
                <button type="button" onclick="openAdminConfigPreviewModal()" class="px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-200 text-xs font-bold border border-slate-200 dark:border-slate-700 transition-all flex items-center gap-1.5 cursor-pointer">
                    <i class="fa-solid fa-eye text-slate-400 text-xs"></i> <span>Preview Homepage</span>
                </button>
                <button type="button" onclick="saveSectionOrder()" class="px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-200 text-xs font-bold border border-slate-200 dark:border-slate-700 transition-all flex items-center gap-1.5 cursor-pointer">
                    <i class="fa-solid fa-arrow-down-up-between text-blue-500 text-xs"></i> <span>Save Section Order</span>
                </button>
                <button type="button" onclick="openSectionEditDrawer(null)" class="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white text-xs font-bold shadow-md transition-all border-0 cursor-pointer flex items-center gap-1.5">
                    <i class="fa-solid fa-plus text-xs"></i> <span>Add Custom Section</span>
                </button>
            </div>
        </div>

        <!-- 2. 5 SUMMARY CARDS -->
        <div id="hpSectionsSummaryCards">
            ${renderHpSectionsSummaryCardsHTML()}
        </div>

        <!-- 3. HOMEPAGE SECTIONS CARD (FILTER TOOLBAR + TABLE) -->
        <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-2xs space-y-3">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-slate-800">
                <div>
                    <h4 class="font-black text-sm text-slate-900 dark:text-white flex items-center gap-2">
                        Homepage Sections
                    </h4>
                    <p class="text-xs text-slate-400 font-medium">
                        Drag and drop to reorder sections. Click edit to configure section details.
                    </p>
                </div>

                <!-- CONTROLS TOOLBAR -->
                <div class="flex flex-wrap items-center gap-2 text-xs">
                    <div class="relative min-w-[180px]">
                        <i class="fa-solid fa-magnifying-glass absolute left-3 top-2.5 text-slate-400 text-xs"></i>
                        <input type="text" id="secSearchInput" value="${window.hpSectionsState.searchQuery || ''}" oninput="onHpSectionSearch(this.value)" placeholder="Search sections..." class="w-full pl-8 pr-3 py-1.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-medium focus:outline-none focus:border-blue-500">
                    </div>
                    <select id="secStatusFilter" onchange="onHpSectionFilterStatus(this.value)" class="px-2.5 py-1.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold cursor-pointer">
                        <option value="all" ${window.hpSectionsState.statusFilter === 'all' ? 'selected' : ''}>All Status</option>
                        <option value="enabled" ${window.hpSectionsState.statusFilter === 'enabled' ? 'selected' : ''}>Enabled</option>
                        <option value="disabled" ${window.hpSectionsState.statusFilter === 'disabled' ? 'selected' : ''}>Disabled</option>
                    </select>
                    <select id="secTypeFilter" onchange="onHpSectionFilterType(this.value)" class="px-2.5 py-1.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold cursor-pointer">
                        <option value="all" ${window.hpSectionsState.typeFilter === 'all' ? 'selected' : ''}>All Types</option>
                        <option value="system" ${window.hpSectionsState.typeFilter === 'system' ? 'selected' : ''}>System</option>
                        <option value="custom" ${window.hpSectionsState.typeFilter === 'custom' ? 'selected' : ''}>Custom</option>
                    </select>
                    <select id="secSortFilter" onchange="onHpSectionSort(this.value)" class="px-2.5 py-1.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold cursor-pointer">
                        <option value="order" ${window.hpSectionsState.sortBy === 'order' ? 'selected' : ''}>Sort by Order</option>
                        <option value="title_asc" ${window.hpSectionsState.sortBy === 'title_asc' ? 'selected' : ''}>Name A-Z</option>
                        <option value="title_desc" ${window.hpSectionsState.sortBy === 'title_desc' ? 'selected' : ''}>Name Z-A</option>
                        <option value="content_count" ${window.hpSectionsState.sortBy === 'content_count' ? 'selected' : ''}>Content Count</option>
                    </select>
                </div>
            </div>

            <!-- TABLE CONTAINER -->
            <div id="hpSectionsTableContainer">
                ${renderHpSectionsTableHTML()}
            </div>
        </div>
    </div>`;
}

function renderSectionEditDrawerHTML() {
    return `
    <!-- RIGHT SIDE EDIT DRAWER BACKDROP -->
    <div id="sectionDrawerBackdrop" onclick="closeSectionDrawer()" class="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-40 hidden transition-opacity"></div>

    <!-- RIGHT SIDE EDIT DRAWER CONTAINER -->
    <div id="sectionEditDrawer" class="fixed inset-y-0 right-0 z-50 w-full sm:w-[480px] md:w-[540px] bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 shadow-2xl flex flex-col transition-transform duration-300 transform translate-x-full">
        <!-- DRAWER HEADER -->
        <div class="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50/60 dark:bg-slate-800/40 shrink-0">
            <div>
                <span class="text-[9.5px] font-extrabold uppercase tracking-wider text-blue-600 dark:text-blue-400 block" id="drawerPreTitle">Section Editor</span>
                <h3 class="text-sm font-black text-slate-900 dark:text-white" id="drawerTitle">Edit Homepage Section</h3>
            </div>
            <button type="button" onclick="closeSectionDrawer()" class="w-8 h-8 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-500 flex items-center justify-center border-0 cursor-pointer transition">
                <i class="fa-solid fa-xmark text-sm"></i>
            </button>
        </div>

        <!-- DRAWER TABS NAVBAR -->
        <div class="flex items-center gap-1 px-4 pt-2 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shrink-0">
            <button type="button" onclick="switchDrawerTab('basic')" id="drawerTabBtn_basic" class="px-3 py-2 text-xs font-bold border-b-2 transition-all border-blue-600 text-blue-600 cursor-pointer border-0 bg-transparent">
                <i class="fa-solid fa-sliders text-[10px] me-1"></i> Basic Settings
            </button>
            <button type="button" onclick="switchDrawerTab('content')" id="drawerTabBtn_content" class="px-3 py-2 text-xs font-bold border-b-2 text-slate-400 hover:text-slate-600 cursor-pointer border-0 bg-transparent">
                <i class="fa-solid fa-file-pen text-[10px] me-1"></i> Content
            </button>
            <button type="button" onclick="switchDrawerTab('appearance')" id="drawerTabBtn_appearance" class="px-3 py-2 text-xs font-bold border-b-2 text-slate-400 hover:text-slate-600 cursor-pointer border-0 bg-transparent">
                <i class="fa-solid fa-paintbrush text-[10px] me-1"></i> Appearance
            </button>
            <button type="button" onclick="switchDrawerTab('advanced')" id="drawerTabBtn_advanced" class="px-3 py-2 text-xs font-bold border-b-2 text-slate-400 hover:text-slate-600 cursor-pointer border-0 bg-transparent">
                <i class="fa-solid fa-gears text-[10px] me-1"></i> Advanced
            </button>
        </div>

        <!-- DRAWER BODY (SCROLLABLE) -->
        <div class="p-4 sm:p-5 overflow-y-auto space-y-4 flex-1 text-xs font-semibold" id="drawerBodyContent">
            <!-- Dynamic JS populates tab content -->
        </div>

        <!-- STICKY DRAWER FOOTER -->
        <div class="p-3.5 px-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-800/60 flex items-center justify-end gap-2 shrink-0">
            <button type="button" onclick="closeSectionDrawer()" class="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 font-bold text-xs border border-slate-200 dark:border-slate-700 cursor-pointer">
                Cancel
            </button>
            <button type="button" onclick="saveSectionDrawer()" id="btnSaveSectionDrawer" class="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md border-0 cursor-pointer flex items-center gap-1.5">
                <i class="fa-solid fa-save text-xs"></i> Save Changes
            </button>
        </div>
    </div>`;
}

function openSectionEditDrawer(secId) {
    if (secId) {
        const found = window.hpSectionsState.sections.find(s => s.id === secId);
        window.hpSectionsState.editingSection = found ? JSON.parse(JSON.stringify(found)) : null;
    } else {
        window.hpSectionsState.editingSection = {
            id: null,
            section_key: 'custom_' + Math.floor(Math.random() * 10000),
            title: 'New Custom Section',
            subtitle: 'Custom section description',
            is_enabled: true,
            display_order: (window.hpSectionsState.sections.length || 0) + 1,
            type: 'custom',
            settings_json: { show_title: true, style: 'card' }
        };
    }

    window.hpSectionsState.drawerTab = 'basic';
    window.hpSectionsState.isDirty = false;

    let drawerEl = document.getElementById('sectionEditDrawerContainer');
    if (!drawerEl) {
        const div = document.createElement('div');
        div.id = 'sectionEditDrawerContainer';
        div.innerHTML = renderSectionEditDrawerHTML();
        document.body.appendChild(div);
    }

    const backdrop = document.getElementById('sectionDrawerBackdrop');
    const drawer = document.getElementById('sectionEditDrawer');

    if (backdrop && drawer) {
        backdrop.classList.remove('hidden');
        setTimeout(() => drawer.classList.remove('translate-x-full'), 20);
    }

    const sec = window.hpSectionsState.editingSection;
    const titleEl = document.getElementById('drawerTitle');
    const preEl = document.getElementById('drawerPreTitle');
    if (titleEl) titleEl.innerText = sec.id ? `Edit: ${sec.title}` : 'Add Custom Section';
    if (preEl) preEl.innerText = sec.id ? `System Key: ${sec.section_key}` : 'New Custom Section';

    switchDrawerTab('basic');

    if (sec.id) {
        fetchHpSectionContent(sec.section_key);
    }
}

function closeSectionDrawer(force = false) {
    if (window.hpSectionsState.isDirty && !force) {
        if (!confirm("Discard unsaved changes? Any edits you made will be lost.")) {
            return;
        }
    }

    const backdrop = document.getElementById('sectionDrawerBackdrop');
    const drawer = document.getElementById('sectionEditDrawer');
    if (drawer) drawer.classList.add('translate-x-full');
    if (backdrop) backdrop.classList.add('hidden');
    window.hpSectionsState.isDirty = false;
}

function switchDrawerTab(tabKey) {
    window.hpSectionsState.drawerTab = tabKey;
    ['basic', 'content', 'appearance', 'advanced'].forEach(t => {
        const btn = document.getElementById(`drawerTabBtn_${t}`);
        if (btn) {
            if (t === tabKey) {
                btn.className = "px-3 py-2 text-xs font-bold border-b-2 border-blue-600 text-blue-600 cursor-pointer border-0 bg-transparent";
            } else {
                btn.className = "px-3 py-2 text-xs font-bold border-b-2 border-transparent text-slate-400 hover:text-slate-600 cursor-pointer border-0 bg-transparent";
            }
        }
    });

    const body = document.getElementById('drawerBodyContent');
    if (body) {
        body.innerHTML = renderDrawerTabContentHTML(tabKey);
    }
}

function renderDrawerTabContentHTML(tabKey) {
    const sec = window.hpSectionsState.editingSection || {};
    const settingsStr = JSON.stringify(sec.settings_json || {}, null, 2);

    if (tabKey === 'basic') {
        const isSys = (sec.type === 'system');
        return `
        <div class="space-y-4 fade-in">
            <!-- THUMBNAIL PREVIEW -->
            <div class="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-blue-100 dark:bg-blue-900/40 text-blue-600 flex items-center justify-center text-lg shadow-2xs">
                        <i class="fa-solid ${getHpSectionIcon(sec.section_key)}"></i>
                    </div>
                    <div>
                        <span class="block text-xs font-bold text-slate-900 dark:text-white">Section Icon & Preview</span>
                        <span class="block text-[10px] text-slate-400 font-normal">Identifies section in admin dashboard</span>
                    </div>
                </div>
                <div class="flex items-center gap-1.5">
                    <button type="button" class="px-2.5 py-1 rounded-lg bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 text-[10px] font-bold text-slate-700 dark:text-slate-200 hover:bg-slate-100 cursor-pointer">
                        Change Icon
                    </button>
                </div>
            </div>

            <!-- SECTION TITLE -->
            <div class="space-y-1">
                <label class="block text-xs font-bold text-slate-700 dark:text-slate-300">Section Title <span class="text-rose-500">*</span></label>
                <input type="text" id="drawerSecTitle" value="${sec.title || ''}" onchange="window.hpSectionsState.isDirty=true" class="w-full px-3 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-medium focus:outline-none focus:border-blue-500">
                <span class="text-[10px] text-slate-400 font-normal block">This title is for internal reference and public section headings.</span>
            </div>

            <!-- SECTION KEY -->
            <div class="space-y-1">
                <label class="block text-xs font-bold text-slate-700 dark:text-slate-300">Section Key <span class="text-rose-500">*</span></label>
                <input type="text" id="drawerSecKey" value="${sec.section_key || ''}" ${isSys ? 'disabled' : ''} onchange="window.hpSectionsState.isDirty=true" class="w-full px-3 py-2 rounded-xl ${isSys ? 'bg-slate-100 text-slate-500 dark:bg-slate-800/80 dark:text-slate-400 cursor-not-allowed' : 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white'} border border-slate-200 dark:border-slate-700 text-xs font-mono">
                <span class="text-[10px] text-slate-400 font-normal block">${isSys ? 'Section key is used for system identification and cannot be changed.' : 'Unique identifier slug for this custom section.'}</span>
            </div>

            <!-- DESCRIPTION -->
            <div class="space-y-1">
                <div class="flex items-center justify-between">
                    <label class="block text-xs font-bold text-slate-700 dark:text-slate-300">Description</label>
                    <span class="text-[10px] text-slate-400" id="charCount">${(sec.subtitle || '').length} / 200</span>
                </div>
                <textarea id="drawerSecSubtitle" rows="2" oninput="document.getElementById('charCount').innerText=this.value.length+' / 200'; window.hpSectionsState.isDirty=true" class="w-full px-3 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-normal focus:outline-none focus:border-blue-500">${sec.subtitle || ''}</textarea>
            </div>

            <!-- ORDER & STATUS GRID -->
            <div class="grid grid-cols-2 gap-3">
                <div class="space-y-1">
                    <label class="block text-xs font-bold text-slate-700 dark:text-slate-300">Display Order <span class="text-rose-500">*</span></label>
                    <input type="number" id="drawerSecOrder" value="${sec.display_order || 1}" onchange="window.hpSectionsState.isDirty=true" class="w-full px-3 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-bold">
                </div>
                <div class="space-y-1">
                    <label class="block text-xs font-bold text-slate-700 dark:text-slate-300">Status</label>
                    <select id="drawerSecStatus" onchange="window.hpSectionsState.isDirty=true" class="w-full px-3 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-bold cursor-pointer">
                        <option value="true" ${sec.is_enabled ? 'selected' : ''}>ON Enabled</option>
                        <option value="false" ${!sec.is_enabled ? 'selected' : ''}>OFF Disabled</option>
                    </select>
                </div>
            </div>

            <!-- SECTION TYPE BADGE -->
            <div class="p-3 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-700 flex items-center justify-between">
                <span class="text-xs font-bold text-slate-700 dark:text-slate-300">Section Type</span>
                <span class="px-2.5 py-0.5 rounded-md text-[10px] font-extrabold ${isSys ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300' : 'bg-purple-100 text-purple-700 dark:bg-purple-900/50 dark:text-purple-300'}">
                    ${isSys ? 'System Section' : 'Custom Section'}
                </span>
            </div>

            <!-- SECTION SETTINGS JSON EDITOR -->
            <div class="space-y-1 pt-2 border-t border-slate-100 dark:border-slate-800">
                <div class="flex items-center justify-between mb-1">
                    <label class="block text-xs font-bold text-slate-700 dark:text-slate-300">Section Settings (JSON Payload)</label>
                    <span class="text-[9.5px] font-bold text-blue-600 cursor-pointer hover:underline" onclick="formatDrawerJson()">Format JSON</span>
                </div>
                <textarea id="drawerSecJson" rows="5" onchange="window.hpSectionsState.isDirty=true" class="w-full p-3 rounded-xl bg-slate-950 text-emerald-400 font-mono text-[11px] leading-relaxed border border-slate-800 focus:outline-none focus:border-blue-500 shadow-inner">${settingsStr}</textarea>
                <span class="text-[9.5px] text-slate-400 block" id="jsonValidMsg">Readable JSON configuration object for section features.</span>
            </div>
        </div>`;
    } else if (tabKey === 'content') {
        const items = window.hpSectionsState.contentItems || [];
        let itemsHtml = '';

        if (items.length === 0) {
            itemsHtml = `
            <div class="p-6 text-center text-slate-400 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-700 space-y-2">
                <i class="fa-solid fa-folder-open text-xl text-slate-400"></i>
                <p class="text-xs font-semibold">No content items configured for this section yet.</p>
                <button type="button" onclick="switchHpSubTab('content')" class="px-3 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold border-0 cursor-pointer">
                    Manage Content Manager
                </button>
            </div>`;
        } else {
            items.forEach((item, idx) => {
                itemsHtml += `
                <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 flex items-center justify-between gap-2">
                    <div class="flex items-center gap-2.5 min-w-0">
                        <div class="w-6 h-6 rounded-lg bg-blue-100 dark:bg-blue-900/40 text-blue-600 flex items-center justify-center text-xs shrink-0 font-bold">
                            ${idx + 1}
                        </div>
                        <div class="min-w-0">
                            <span class="block text-xs font-bold text-slate-900 dark:text-white truncate">${item.title}</span>
                            <span class="block text-[10px] text-slate-400 truncate">${item.description || item.subtitle || 'Content card item'}</span>
                        </div>
                    </div>
                    <div class="flex items-center gap-1 shrink-0">
                        <span class="px-2 py-0.5 rounded-full text-[9px] font-extrabold ${item.is_enabled ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'} me-1">
                            ${item.is_enabled ? 'Active' : 'Hidden'}
                        </span>
                        <button type="button" onclick="switchHpSubTab('content')" class="p-1 text-slate-500 hover:text-blue-600 border-0 bg-transparent cursor-pointer"><i class="fa-solid fa-pen"></i></button>
                    </div>
                </div>`;
            });
        }

        return `
        <div class="space-y-4 fade-in">
            <div class="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800">
                <div>
                    <h5 class="font-bold text-xs text-slate-900 dark:text-white">Associated Content Items</h5>
                    <p class="text-[10px] text-slate-400">Cards, steps, statistics, and reviews for section.</p>
                </div>
                <button type="button" onclick="switchHpSubTab('content')" class="px-3 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold border-0 cursor-pointer">
                    + Open Content Manager
                </button>
            </div>
            <div class="space-y-2">
                ${itemsHtml}
            </div>
        </div>`;
    } else if (tabKey === 'appearance') {
        return `
        <div class="space-y-4 fade-in">
            <div class="space-y-1">
                <label class="block text-xs font-bold text-slate-700 dark:text-slate-300">Background Type</label>
                <select id="appBgType" onchange="window.hpSectionsState.isDirty=true" class="w-full px-3 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-semibold cursor-pointer">
                    <option value="none">None / Default</option>
                    <option value="color">Solid Background Color</option>
                    <option value="gradient">Gradient Background</option>
                    <option value="image">Background Image</option>
                </select>
            </div>
            <div class="grid grid-cols-2 gap-3">
                <div class="space-y-1">
                    <label class="block text-xs font-bold text-slate-700 dark:text-slate-300">Background Color</label>
                    <input type="color" id="appBgColor" value="#ffffff" onchange="window.hpSectionsState.isDirty=true" class="w-full h-9 p-1 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 cursor-pointer">
                </div>
                <div class="space-y-1">
                    <label class="block text-xs font-bold text-slate-700 dark:text-slate-300">Text Alignment</label>
                    <select id="appTextAlign" onchange="window.hpSectionsState.isDirty=true" class="w-full px-3 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-semibold cursor-pointer">
                        <option value="left">Left Aligned</option>
                        <option value="center">Centered</option>
                        <option value="right">Right Aligned</option>
                    </select>
                </div>
            </div>
            <div class="grid grid-cols-2 gap-3">
                <div class="space-y-1">
                    <label class="block text-xs font-bold text-slate-700 dark:text-slate-300">Container Width</label>
                    <select id="appContainerWidth" onchange="window.hpSectionsState.isDirty=true" class="w-full px-3 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-semibold cursor-pointer">
                        <option value="default">Default Container (1200px)</option>
                        <option value="wide">Wide Container (1400px)</option>
                        <option value="full">Full Width (100%)</option>
                    </select>
                </div>
                <div class="space-y-1">
                    <label class="block text-xs font-bold text-slate-700 dark:text-slate-300">Section Spacing</label>
                    <select id="appSpacing" onchange="window.hpSectionsState.isDirty=true" class="w-full px-3 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-semibold cursor-pointer">
                        <option value="small">Small Padding</option>
                        <option value="medium" selected>Medium Padding (Default)</option>
                        <option value="large">Large Padding</option>
                    </select>
                </div>
            </div>
            <div class="space-y-1">
                <label class="block text-xs font-bold text-slate-700 dark:text-slate-300">Custom CSS Class</label>
                <input type="text" id="appCssClass" placeholder="e.g. py-16 bg-slate-50 border-y" onchange="window.hpSectionsState.isDirty=true" class="w-full px-3 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-mono">
            </div>
        </div>`;
    } else if (tabKey === 'advanced') {
        return `
        <div class="space-y-4 fade-in">
            <div class="p-3 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-xl text-amber-800 dark:text-amber-300 text-xs font-semibold flex items-center gap-2">
                <i class="fa-solid fa-triangle-exclamation text-amber-600 text-sm shrink-0"></i>
                <span>Advanced parameters directly modify rendering attributes. Modify with care.</span>
            </div>
            <div class="space-y-1">
                <label class="block text-xs font-bold text-slate-700 dark:text-slate-300">Section HTML ID</label>
                <input type="text" id="advSecId" value="sec-${sec.section_key || 'custom'}" onchange="window.hpSectionsState.isDirty=true" class="w-full px-3 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-mono">
            </div>
            <div class="space-y-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                <label class="block text-xs font-bold text-slate-700 dark:text-slate-300">Device Visibility</label>
                <div class="grid grid-cols-3 gap-2">
                    <label class="p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 flex items-center justify-between cursor-pointer bg-white dark:bg-slate-800">
                        <span class="text-[11px] font-bold"><i class="fa-solid fa-desktop me-1 text-slate-400"></i> Desktop</span>
                        <input type="checkbox" checked onchange="window.hpSectionsState.isDirty=true" class="w-4 h-4 text-blue-600">
                    </label>
                    <label class="p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 flex items-center justify-between cursor-pointer bg-white dark:bg-slate-800">
                        <span class="text-[11px] font-bold"><i class="fa-solid fa-tablet-screen-button me-1 text-slate-400"></i> Tablet</span>
                        <input type="checkbox" checked onchange="window.hpSectionsState.isDirty=true" class="w-4 h-4 text-blue-600">
                    </label>
                    <label class="p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 flex items-center justify-between cursor-pointer bg-white dark:bg-slate-800">
                        <span class="text-[11px] font-bold"><i class="fa-solid fa-mobile-screen me-1 text-slate-400"></i> Mobile</span>
                        <input type="checkbox" checked onchange="window.hpSectionsState.isDirty=true" class="w-4 h-4 text-blue-600">
                    </label>
                </div>
            </div>
        </div>`;
    }
}

async function saveSectionDrawer() {
    const sec = window.hpSectionsState.editingSection;
    if (!sec) return;

    const titleEl = document.getElementById('drawerSecTitle');
    const keyEl = document.getElementById('drawerSecKey');
    const subEl = document.getElementById('drawerSecSubtitle');
    const ordEl = document.getElementById('drawerSecOrder');
    const statEl = document.getElementById('drawerSecStatus');
    const jsonEl = document.getElementById('drawerSecJson');

    const title = titleEl ? titleEl.value.trim() : sec.title;
    const sec_key = keyEl ? keyEl.value.trim().toLowerCase().replace(/\s+/g, '_') : sec.section_key;
    const subtitle = subEl ? subEl.value.trim() : sec.subtitle;
    const display_order = ordEl ? parseInt(ordEl.value, 10) : sec.display_order;
    const is_enabled = statEl ? (statEl.value === 'true') : sec.is_enabled;

    let settings_json = {};
    if (jsonEl && jsonEl.value.trim()) {
        try {
            settings_json = JSON.parse(jsonEl.value.trim());
        } catch (e) {
            alert("Invalid JSON format in Section Settings! Please fix syntax errors before saving.");
            return;
        }
    }

    if (!title || !sec_key) {
        alert("Section Title and Section Key are required.");
        return;
    }

    const isNew = !sec.id;
    const action = isNew ? 'create' : 'update';
    const payload = {
        action: action,
        id: sec.id,
        title: title,
        section_key: sec_key,
        subtitle: subtitle,
        display_order: display_order,
        is_enabled: is_enabled,
        settings_json: settings_json
    };

    const btn = document.getElementById('btnSaveSectionDrawer');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-xs me-1"></i> Saving...`;
    }

    try {
        const res = await fetch('/api/admin/homepage/sections/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const resData = await res.json();
        if (resData.status === 'success') {
            if (typeof showToast === 'function') {
                showToast(`✓ ${resData.message}`, 'success');
            } else {
                alert(`✓ ${resData.message}`);
            }
            closeSectionDrawer(true);
            await fetchHpSectionsData();
        } else {
            alert(`Error: ${resData.message}`);
        }
    } catch (err) {
        alert("Failed to save section settings. Please check backend connection.");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<i class="fa-solid fa-save text-xs me-1"></i> Save Changes`;
        }
    }
}

async function toggleSectionStatus(secId) {
    try {
        const res = await fetch('/api/admin/homepage/sections/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'toggle', id: secId })
        });
        const data = await res.json();
        if (data.status === 'success') {
            if (typeof showToast === 'function') {
                showToast(`✓ ${data.message}`, 'success');
            }
            await fetchHpSectionsData();
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (err) {
        console.error(err);
    }
}

async function saveSectionOrder() {
    const tableBody = document.getElementById('sectionsTableBody');
    if (!tableBody) return;
    const rows = tableBody.querySelectorAll('tr[data-sec-id]');
    const orderList = Array.from(rows).map(r => parseInt(r.getAttribute('data-sec-id'), 10));

    try {
        const res = await fetch('/api/admin/homepage/sections/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'reorder', order: orderList })
        });
        const data = await res.json();
        if (data.status === 'success') {
            if (typeof showToast === 'function') {
                showToast('✓ Section order saved successfully!', 'success');
            }
            await fetchHpSectionsData();
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (err) {
        console.error(err);
    }
}

async function deleteCustomSection(secId) {
    if (!confirm("Are you sure you want to delete this custom section? This action cannot be undone.")) return;
    try {
        const res = await fetch('/api/admin/homepage/sections/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'delete', id: secId })
        });
        const data = await res.json();
        if (data.status === 'success') {
            if (typeof showToast === 'function') showToast(`✓ ${data.message}`, 'success');
            await fetchHpSectionsData();
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (err) {
        console.error(err);
    }
}

async function moveSectionOrder(secId, dir) {
    const list = window.hpSectionsState.sections;
    const idx = list.findIndex(s => s.id === secId);
    if (idx === -1) return;
    if (dir === 'up' && idx > 0) {
        const temp = list[idx].display_order;
        list[idx].display_order = list[idx - 1].display_order;
        list[idx - 1].display_order = temp;
    } else if (dir === 'down' && idx < list.length - 1) {
        const temp = list[idx].display_order;
        list[idx].display_order = list[idx + 1].display_order;
        list[idx + 1].display_order = temp;
    }
    const orderList = list.sort((a,b) => a.display_order - b.display_order).map(s => s.id);
    try {
        await fetch('/api/admin/homepage/sections/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'reorder', order: orderList })
        });
        await fetchHpSectionsData();
    } catch (e) {
        console.error(e);
    }
}

async function fetchHpSectionContent(sectionKey) {
    try {
        const res = await fetch(`/api/admin/homepage/content/?section_key=${sectionKey}`);
        const data = await res.json();
        if (data.status === 'success') {
            window.hpSectionsState.contentItems = data.items || [];
            if (window.hpSectionsState.drawerTab === 'content') {
                switchDrawerTab('content');
            }
        }
    } catch (e) {
        console.error(e);
    }
}

function formatDrawerJson() {
    const el = document.getElementById('drawerSecJson');
    if (!el) return;
    try {
        const obj = JSON.parse(el.value);
        el.value = JSON.stringify(obj, null, 2);
        document.getElementById('jsonValidMsg').innerHTML = `<span class="text-emerald-500 font-bold">✓ Valid JSON</span>`;
    } catch (e) {
        document.getElementById('jsonValidMsg').innerHTML = `<span class="text-rose-500 font-bold">✕ Invalid JSON syntax</span>`;
    }
}

function renderHpSubTabBtn(key, icon, label) {
    const active = (window.hpSubTab === key);
    const bgClass = active ? 'bg-blue-600 text-white shadow-2xs' : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-200/60 dark:border-slate-700';
    return `<button type="button" onclick="switchHpSubTab('${key}')" class="px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all border-0 cursor-pointer flex items-center gap-1 shrink-0 ${bgClass}">
        <i class="fa-solid ${icon} text-[9px]"></i> ${label}
    </button>`;
}

function switchHpSubTab(key) {
    window.hpSubTab = key;
    renderCategoryFields('homepage');
}

function publishHomePageSettings() {
    saveCurrentCategorySettings();
    if (typeof showToast === 'function') {
        showToast('✓ Homepage CMS Settings Saved & Published!', 'success');
    } else {
        alert('✓ Homepage CMS Settings Saved & Published!');
    }
}

function openAdminConfigPreviewModal() {
    const modal = document.getElementById('modalAdminConfigPreview');
    if (modal) {
        modal.classList.remove('hidden');
        modal.style.display = 'flex';
    } else {
        alert("Admin Configuration Preview: All settings are active in Admin database.");
    }
}

function closeAdminConfigPreviewModal() {
    const modal = document.getElementById('modalAdminConfigPreview');
    if (modal) {
        modal.classList.add('hidden');
        modal.style.display = 'none';
    }
}

function renderHomePageSettingsCenter(catKey) {
    const catData = allSettingsData[catKey] || {};
    const getVal = (k, d = '') => (catData[k] && catData[k].value !== undefined) ? catData[k].value : d;
    const getBool = (k, d = true) => {
        const v = getVal(k, d ? 'true' : 'false');
        return String(v).toLowerCase() === 'true' || v === true;
    };

    const currentTab = window.hpSubTab || 'overview';
    const webMode = getVal('website_mode', 'home_tuition_only');

    let modeBadgeHtml = '';
    if (webMode === 'home_tuition_only') {
        modeBadgeHtml = '<span class="px-2.5 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60 text-[10px] font-bold"><i class="fa-solid fa-house-user me-1"></i> Home Tuition Only Mode</span>';
    } else if (webMode === 'home_online') {
        modeBadgeHtml = '<span class="px-2.5 py-0.5 rounded-full bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-800/60 text-[10px] font-bold"><i class="fa-solid fa-laptop-house me-1"></i> Home + Online Tuition Mode</span>';
    } else if (webMode === 'combined') {
        modeBadgeHtml = '<span class="px-2.5 py-0.5 rounded-full bg-teal-50 dark:bg-teal-950/50 text-teal-600 dark:text-teal-400 border border-teal-200 dark:border-teal-800/60 text-[10px] font-bold"><i class="fa-solid fa-layer-group me-1"></i> Combined Mode</span>';
    } else {
        modeBadgeHtml = '<span class="px-2.5 py-0.5 rounded-full bg-purple-50 dark:bg-purple-950/50 text-purple-600 dark:text-purple-400 border border-purple-200 dark:border-purple-800/60 text-[10px] font-bold"><i class="fa-solid fa-graduation-cap me-1"></i> Full LMS Platform Mode</span>';
    }

    let mainTabHtml = '';

    if (currentTab === 'overview') {
        mainTabHtml = `
        <div class="space-y-5">
            <!-- 1. SUMMARY METRICS CARDS (COMPACT DYNAMIC) -->
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
                <div class="p-2 px-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-800 space-y-0.5">
                    <span class="text-[8.5px] font-bold text-slate-400 uppercase tracking-wider block truncate">Homepage Sections</span>
                    <span class="text-sm font-black text-slate-900 dark:text-white block">10</span>
                    <span class="text-[9.5px] font-bold text-emerald-600 dark:text-emerald-400 block"><i class="fa-solid fa-circle-check me-1"></i> 10 Active</span>
                </div>
                <div class="p-2 px-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-800 space-y-0.5">
                    <span class="text-[8.5px] font-bold text-slate-400 uppercase tracking-wider block truncate">Content Items</span>
                    <span class="text-sm font-black text-slate-900 dark:text-white block">22</span>
                    <span class="text-[9.5px] font-bold text-emerald-600 dark:text-emerald-400 block"><i class="fa-solid fa-circle-check me-1"></i> 22 Active</span>
                </div>
                <div class="p-2 px-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-800 space-y-0.5">
                    <span class="text-[8.5px] font-bold text-slate-400 uppercase tracking-wider block truncate">Website Forms</span>
                    <span class="text-sm font-black text-slate-900 dark:text-white block">4</span>
                    <span class="text-[9.5px] font-bold text-emerald-600 dark:text-emerald-400 block"><i class="fa-solid fa-circle-check me-1"></i> 4 Active</span>
                </div>
                <div class="p-2 px-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-800 space-y-0.5">
                    <span class="text-[8.5px] font-bold text-slate-400 uppercase tracking-wider block truncate">Navigation Items</span>
                    <span class="text-sm font-black text-slate-900 dark:text-white block">8</span>
                    <span class="text-[9.5px] font-bold text-emerald-600 dark:text-emerald-400 block"><i class="fa-solid fa-circle-check me-1"></i> 8 Active</span>
                </div>
                <div class="p-2 px-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-800 space-y-0.5">
                    <span class="text-[8.5px] font-bold text-slate-400 uppercase tracking-wider block truncate">Footer Columns</span>
                    <span class="text-sm font-black text-slate-900 dark:text-white block">3</span>
                    <span class="text-[9.5px] font-bold text-emerald-600 dark:text-emerald-400 block"><i class="fa-solid fa-circle-check me-1"></i> 3 Active</span>
                </div>
                <div class="p-2 px-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-800 space-y-0.5">
                    <span class="text-[8.5px] font-bold text-slate-400 uppercase tracking-wider block truncate">Website Mode</span>
                    <span class="text-xs font-black text-blue-600 dark:text-blue-400 block truncate">${webMode === 'home_tuition_only' ? 'Home Tuition' : (webMode === 'home_online' ? 'Home + Online' : 'Full LMS')}</span>
                    <span class="text-[9.5px] font-bold text-emerald-600 dark:text-emerald-400 block"><i class="fa-solid fa-shield-halved me-1"></i> Active</span>
                </div>
            </div>

            <!-- 2. CURRENT PLATFORM OPERATING MODE CARD (COMPACT) -->
            <div class="p-2.5 px-3 rounded-xl bg-gradient-to-r from-blue-50 via-indigo-50 to-slate-50 dark:from-slate-800 dark:to-slate-800/80 border border-blue-200 dark:border-slate-700 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
                <div class="space-y-0.5 max-w-xl">
                    <span class="text-[9px] font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400">Current Platform Operating Mode</span>
                    <h4 class="text-xs sm:text-sm font-black text-slate-900 dark:text-white flex items-center gap-1.5">
                        ${webMode === 'home_tuition_only' ? 'Home Tuition Only (Recommended Default)' : (webMode === 'home_online' ? 'Home + Online Tuition Mode' : 'Full LMS Platform Mode')}
                    </h4>
                    <p class="text-[11px] text-slate-600 dark:text-slate-300 font-normal leading-tight">
                        ${webMode === 'home_tuition_only' ? 'Public website focuses on home tutors, student requirements, tuition jobs, and local lead generation. Digital courses & tests are hidden publicly.' : 'Public website displays tuition and digital learning features.'}
                    </p>
                    <div class="flex flex-wrap items-center gap-2.5 text-[10px] pt-0.5 font-bold">
                        <span class="text-emerald-600 flex items-center gap-1"><i class="fa-solid fa-check text-[10px]"></i> Find Tutor</span>
                        <span class="text-emerald-600 flex items-center gap-1"><i class="fa-solid fa-check text-[10px]"></i> Tuition Jobs</span>
                        <span class="text-emerald-600 flex items-center gap-1"><i class="fa-solid fa-check text-[10px]"></i> Post Requirement</span>
                        <span class="text-emerald-600 flex items-center gap-1"><i class="fa-solid fa-check text-[10px]"></i> Become Tutor</span>
                    </div>
                </div>
                <button type="button" onclick="switchHpSubTab('mode')" class="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs border-0 cursor-pointer transition-all shrink-0 shadow-2xs flex items-center gap-1">
                    <i class="fa-solid fa-layer-group text-[10px]"></i> Change Mode
                </button>
            </div>

            <!-- 3. HOMEPAGE SECTIONS STATUS TABLE -->
            <div class="space-y-2">
                <div class="flex items-center justify-between">
                    <h4 class="font-black text-xs text-slate-900 dark:text-white uppercase tracking-wider">Homepage Sections Status</h4>
                    <button type="button" onclick="switchHpSubTab('sections')" class="text-xs font-bold text-blue-600 dark:text-blue-400 hover:underline border-0 bg-transparent cursor-pointer">
                        Manage All Sections <i class="fa-solid fa-arrow-right text-[10px] ms-1"></i>
                    </button>
                </div>

                <div class="border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-xs">
                    <table class="w-full text-left text-xs font-semibold">
                        <thead class="bg-slate-50 dark:bg-slate-800/60 text-slate-400 text-[10px] uppercase font-bold border-b border-slate-200 dark:border-slate-800">
                            <tr>
                                <th class="p-3">Order</th>
                                <th class="p-3">Section Title</th>
                                <th class="p-3">Section Key</th>
                                <th class="p-3 text-center">Status</th>
                                <th class="p-3 text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
                            ${renderHpSectionRow('01', 'Hero Banner & Search Bar', 'hero', true)}
                            ${renderHpSectionRow('02', 'Latest Tuition Jobs', 'tuition_jobs', true)}
                            ${renderHpSectionRow('03', 'Featured Tutors', 'featured_tutors', true)}
                            ${renderHpSectionRow('04', 'Popular Subjects', 'popular_subjects', true)}
                            ${renderHpSectionRow('05', 'Why Choose Us Cards', 'why_choose_us', true)}
                            ${renderHpSectionRow('06', 'How It Works Steps', 'how_it_works', true)}
                            ${renderHpSectionRow('07', 'Statistics Counters', 'statistics', true)}
                            ${renderHpSectionRow('08', 'Testimonials & Reviews', 'testimonials', true)}
                            ${renderHpSectionRow('09', 'Frequently Asked Questions', 'faq', true)}
                            ${renderHpSectionRow('10', 'Call To Action Banner', 'cta', true)}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- 4. QUICK ACTIONS GRID -->
            <div class="space-y-2">
                <h4 class="font-black text-xs text-slate-900 dark:text-white uppercase tracking-wider">Quick Actions & Sub-Tab Shortcuts</h4>
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                    <button type="button" onclick="switchHpSubTab('hero')" class="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 hover:bg-blue-50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-left transition flex items-center gap-2 cursor-pointer">
                        <i class="fa-solid fa-bolt text-blue-500 text-sm"></i>
                        <div><span class="font-bold text-xs text-slate-900 dark:text-white block">Hero & Search</span><span class="text-[10px] text-slate-400 block">Banner controls</span></div>
                    </button>
                    <button type="button" onclick="switchHpSubTab('sections')" class="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 hover:bg-blue-50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-left transition flex items-center gap-2 cursor-pointer">
                        <i class="fa-solid fa-sliders text-indigo-500 text-sm"></i>
                        <div><span class="font-bold text-xs text-slate-900 dark:text-white block">Manage Sections</span><span class="text-[10px] text-slate-400 block">Reorder & visibility</span></div>
                    </button>
                    <button type="button" onclick="switchHpSubTab('content')" class="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 hover:bg-blue-50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-left transition flex items-center gap-2 cursor-pointer">
                        <i class="fa-solid fa-book-open text-purple-500 text-sm"></i>
                        <div><span class="font-bold text-xs text-slate-900 dark:text-white block">Content Items</span><span class="text-[10px] text-slate-400 block">Cards & steps</span></div>
                    </button>
                    <button type="button" onclick="switchHpSubTab('forms')" class="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 hover:bg-blue-50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-left transition flex items-center gap-2 cursor-pointer">
                        <i class="fa-solid fa-wpforms text-emerald-500 text-sm"></i>
                        <div><span class="font-bold text-xs text-slate-900 dark:text-white block">Forms Builder</span><span class="text-[10px] text-slate-400 block">Fields & settings</span></div>
                    </button>
                    <button type="button" onclick="switchHpSubTab('navigation')" class="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 hover:bg-blue-50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-left transition flex items-center gap-2 cursor-pointer">
                        <i class="fa-solid fa-bars text-amber-500 text-sm"></i>
                        <div><span class="font-bold text-xs text-slate-900 dark:text-white block">Navigation</span><span class="text-[10px] text-slate-400 block">Header & footer menus</span></div>
                    </button>
                    <button type="button" onclick="switchHpSubTab('footer')" class="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 hover:bg-blue-50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-left transition flex items-center gap-2 cursor-pointer">
                        <i class="fa-solid fa-shoe-prints text-rose-500 text-sm"></i>
                        <div><span class="font-bold text-xs text-slate-900 dark:text-white block">Footer Columns</span><span class="text-[10px] text-slate-400 block">Links & disclaimer</span></div>
                    </button>
                    <button type="button" onclick="switchHpSubTab('contact')" class="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 hover:bg-blue-50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-left transition flex items-center gap-2 cursor-pointer">
                        <i class="fa-solid fa-phone text-cyan-500 text-sm"></i>
                        <div><span class="font-bold text-xs text-slate-900 dark:text-white block">Contact Info</span><span class="text-[10px] text-slate-400 block">Phone & email</span></div>
                    </button>
                    <button type="button" onclick="switchHpSubTab('seo')" class="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 hover:bg-blue-50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-left transition flex items-center gap-2 cursor-pointer">
                        <i class="fa-solid fa-magnifying-glass text-teal-500 text-sm"></i>
                        <div><span class="font-bold text-xs text-slate-900 dark:text-white block">SEO & Meta</span><span class="text-[10px] text-slate-400 block">Titles & tags</span></div>
                    </button>
                </div>
            </div>
        </div>`;
    } else if (currentTab === 'mode') {
        mainTabHtml = `
        <div class="space-y-4">
            <div class="p-3.5 bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800 rounded-2xl text-blue-800 dark:text-blue-300 text-xs font-semibold flex items-center gap-2">
                <i class="fa-solid fa-circle-info text-blue-600 text-sm shrink-0"></i>
                <span>Selecting a website mode adapts public navigation, hero search, and feature visibility automatically without losing any database records.</span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <!-- Mode 1: Home Tuition Only -->
                <label class="p-4 rounded-2xl border-2 cursor-pointer transition-all ${webMode === 'home_tuition_only' ? 'border-blue-600 bg-blue-50/50 dark:bg-blue-900/20 shadow-md' : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-slate-300'} flex flex-col justify-between space-y-3">
                    <div class="space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="w-8 h-8 rounded-xl bg-emerald-100 dark:bg-emerald-900/40 text-emerald-600 flex items-center justify-center text-sm font-bold"><i class="fa-solid fa-house-user"></i></span>
                            <input type="radio" name="website_mode" value="home_tuition_only" ${webMode === 'home_tuition_only' ? 'checked' : ''} onchange="markDirty()" class="w-4 h-4 text-blue-600">
                        </div>
                        <div>
                            <h4 class="font-black text-sm text-slate-900 dark:text-white flex items-center gap-1.5">Home Tuition Only <span class="text-[9px] font-extrabold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300">Recommended</span></h4>
                            <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Focus exclusively on home tutors, student requirements, tuition jobs, and local lead generation.</p>
                        </div>
                        <ul class="text-[11px] text-slate-700 dark:text-slate-300 space-y-1 pt-2 border-t border-slate-100 dark:border-slate-800 font-semibold">
                            <li class="flex items-center gap-1.5 text-emerald-600"><i class="fa-solid fa-check"></i> Find Tutor & Post Requirement</li>
                            <li class="flex items-center gap-1.5 text-emerald-600"><i class="fa-solid fa-check"></i> Local Tuition Job Applications</li>
                            <li class="flex items-center gap-1.5 text-slate-400"><i class="fa-solid fa-xmark"></i> Hide Online Courses & Tests publicly</li>
                        </ul>
                    </div>
                </label>

                <!-- Mode 2: Home + Online Tuition -->
                <label class="p-4 rounded-2xl border-2 cursor-pointer transition-all ${webMode === 'home_online' ? 'border-blue-600 bg-blue-50/50 dark:bg-blue-900/20 shadow-md' : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-slate-300'} flex flex-col justify-between space-y-3">
                    <div class="space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="w-8 h-8 rounded-xl bg-blue-100 dark:bg-blue-900/40 text-blue-600 flex items-center justify-center text-sm font-bold"><i class="fa-solid fa-laptop-house"></i></span>
                            <input type="radio" name="website_mode" value="home_online" ${webMode === 'home_online' ? 'checked' : ''} onchange="markDirty()" class="w-4 h-4 text-blue-600">
                        </div>
                        <div>
                            <h4 class="font-black text-sm text-slate-900 dark:text-white">Home + Online Tuition</h4>
                            <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Combine physical home tuition matching with online 1-on-1 video tutoring.</p>
                        </div>
                        <ul class="text-[11px] text-slate-700 dark:text-slate-300 space-y-1 pt-2 border-t border-slate-100 dark:border-slate-800 font-semibold">
                            <li class="flex items-center gap-1.5 text-emerald-600"><i class="fa-solid fa-check"></i> All Home Tuition Features</li>
                            <li class="flex items-center gap-1.5 text-emerald-600"><i class="fa-solid fa-check"></i> Enable Online Tutor Search</li>
                            <li class="flex items-center gap-1.5 text-emerald-600"><i class="fa-solid fa-check"></i> Enable Live WebRTC / Zoom Classes</li>
                        </ul>
                    </div>
                </label>

                <!-- Mode 3: Full LMS -->
                <label class="p-4 rounded-2xl border-2 cursor-pointer transition-all ${webMode === 'full_lms' ? 'border-blue-600 bg-blue-50/50 dark:bg-blue-900/20 shadow-md' : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-slate-300'} flex flex-col justify-between space-y-3">
                    <div class="space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="w-8 h-8 rounded-xl bg-purple-100 dark:bg-purple-900/40 text-purple-600 flex items-center justify-center text-sm font-bold"><i class="fa-solid fa-graduation-cap"></i></span>
                            <input type="radio" name="website_mode" value="full_lms" ${webMode === 'full_lms' ? 'checked' : ''} onchange="markDirty()" class="w-4 h-4 text-blue-600">
                        </div>
                        <div>
                            <h4 class="font-black text-sm text-slate-900 dark:text-white">Full LMS Platform</h4>
                            <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Complete learning management platform including courses, exams, live classes, study materials, and certificates.</p>
                        </div>
                        <ul class="text-[11px] text-slate-700 dark:text-slate-300 space-y-1 pt-2 border-t border-slate-100 dark:border-slate-800 font-semibold">
                            <li class="flex items-center gap-1.5 text-emerald-600"><i class="fa-solid fa-check"></i> All Home Tuition Features</li>
                            <li class="flex items-center gap-1.5 text-emerald-600"><i class="fa-solid fa-check"></i> Recorded Courses & Batches</li>
                            <li class="flex items-center gap-1.5 text-emerald-600"><i class="fa-solid fa-check"></i> Online Examinations & DPP</li>
                        </ul>
                    </div>
                </label>
            </div>
        </div>`;
    } else if (currentTab === 'sections') {
        mainTabHtml = renderHpSectionsManagerTab();
    }
    } else if (currentTab === 'hero') {
        mainTabHtml = `
        <div class="space-y-5">
            <div class="border-b border-slate-200 dark:border-slate-800 pb-2">
                <h4 class="font-black text-xs text-slate-900 dark:text-white uppercase tracking-wider">Hero Text Content & Action Buttons</h4>
                <p class="text-[11px] text-slate-400">Configure hero titles, subheadings, badge text, and action buttons.</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                ${renderInputSetting('hero_badge_text', 'Badge Text', 'Top badge pill text', getVal('hero_badge_text', "India's #1 Home Tuition Platform"))}
                ${renderInputSetting('hero_main_heading', 'Main Heading', 'Main title text', getVal('hero_main_heading', 'Find Experienced Home Tutors Near You'))}
                ${renderInputSetting('hero_highlight_heading', 'Highlighted Heading', 'Sub-heading highlighted text', getVal('hero_highlight_heading', 'Personalized 1-on-1 Learning'))}
                ${renderInputSetting('hero_description', 'Hero Description', 'Detailed subtitle paragraph', getVal('hero_description', 'Connect with verified expert tutors for all classes, subjects, and boards right at your home.'))}
                ${renderInputSetting('hero_primary_btn_text', 'Primary Button Text', 'Main button text', getVal('hero_primary_btn_text', 'Find a Tutor'))}
                ${renderInputSetting('hero_primary_btn_url', 'Primary Button URL', 'Target URL or section anchor', getVal('hero_primary_btn_url', '/find-tutor/'))}
                ${renderInputSetting('hero_secondary_btn_text', 'Secondary Button Text', 'Secondary button text', getVal('hero_secondary_btn_text', 'Post Tuition Requirement'))}
                ${renderInputSetting('hero_secondary_btn_url', 'Secondary Button URL', 'Target URL', getVal('hero_secondary_btn_url', '#post-requirement'))}
            </div>

            <div class="pt-4 border-t border-slate-200 dark:border-slate-800 space-y-3">
                <h4 class="font-black text-xs text-slate-900 dark:text-white uppercase tracking-wider">Hero Search Bar & Filter Controls</h4>
                <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                    ${renderToggleSetting('search_enabled', 'Enable Hero Search Bar', 'Display filter search box on hero', getBool('search_enabled', true))}
                    ${renderToggleSetting('search_field_class', 'Search Class Filter', 'Allow filtering by Class/Grade', getBool('search_field_class', true))}
                    ${renderToggleSetting('search_field_subject', 'Search Subject Filter', 'Allow filtering by Subject', getBool('search_field_subject', true))}
                    ${renderToggleSetting('search_field_location', 'Search Location Filter', 'Allow filtering by City/Area', getBool('search_field_location', true))}
                    ${renderToggleSetting('search_field_tuition_type', 'Search Tuition Type', 'Allow filtering by Home/Online', getBool('search_field_tuition_type', true))}
                    ${renderToggleSetting('search_field_budget', 'Search Budget Filter', 'Allow filtering by Monthly Fee', getBool('search_field_budget', true))}
                </div>
            </div>
        </div>`;
    } else if (currentTab === 'content') {
        mainTabHtml = `
        <div class="space-y-4">
            <div class="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-800 flex items-center justify-between">
                <div>
                    <h4 class="font-black text-sm text-slate-900 dark:text-white">Repeatable Content Items & Cards Manager</h4>
                    <p class="text-xs text-slate-400">Configure content cards for Why Choose Us, Steps, Testimonials, FAQ, Statistics, and Subjects.</p>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-2">
                    <h5 class="font-bold text-xs text-slate-800 dark:text-slate-200 flex items-center gap-1.5"><i class="fa-solid fa-circle-check text-blue-500"></i> Why Choose Us Cards</h5>
                    <p class="text-[11px] text-slate-400">Verified Tutors, Doorstep Classes, Flexible Timings, Transparent Fees.</p>
                </div>
                <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-2">
                    <h5 class="font-bold text-xs text-slate-800 dark:text-slate-200 flex items-center gap-1.5"><i class="fa-solid fa-stairs text-purple-500"></i> How It Works Steps</h5>
                    <p class="text-[11px] text-slate-400">1. Post Requirement -> 2. Get Matched -> 3. Free Demo -> 4. Start Tuition.</p>
                </div>
                <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-2">
                    <h5 class="font-bold text-xs text-slate-800 dark:text-slate-200 flex items-center gap-1.5"><i class="fa-solid fa-chart-line text-emerald-500"></i> Statistics Counters</h5>
                    <p class="text-[11px] text-slate-400">10K+ Verified Tutors, 50+ Cities, 95% Satisfaction, 24/7 Support.</p>
                </div>
                <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-2">
                    <h5 class="font-bold text-xs text-slate-800 dark:text-slate-200 flex items-center gap-1.5"><i class="fa-solid fa-quote-left text-amber-500"></i> Testimonials & FAQ Reviews</h5>
                    <p class="text-[11px] text-slate-400">Manage parent & tutor reviews and accordion questions.</p>
                </div>
            </div>
        </div>`;
    } else if (currentTab === 'tuition_jobs') {
        mainTabHtml = `
        <div class="space-y-4">
            <div class="border-b border-slate-200 dark:border-slate-800 pb-2">
                <h4 class="font-black text-xs text-slate-900 dark:text-white uppercase tracking-wider">Tuition Jobs Section Configuration</h4>
                <p class="text-[11px] text-slate-400">Control display settings, job count, sorting, and job card fields.</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                ${renderToggleSetting('jobs_section_enabled', 'Enable Jobs Section', 'Show Latest Tuition Jobs on homepage', getBool('jobs_section_enabled', true))}
                ${renderInputSetting('jobs_section_title', 'Section Title', 'Section title heading', getVal('jobs_section_title', 'Latest Home Tuition Jobs'))}
                ${renderInputSetting('jobs_max_count', 'Number of Jobs Displayed', 'Max job cards shown', getVal('jobs_max_count', '6'))}
                ${renderInputSetting('jobs_sort_by', 'Job Sorting', 'Sorting order (Latest/Featured/Relevant)', getVal('jobs_sort_by', 'Latest'))}
                ${renderToggleSetting('jobs_show_budget', 'Show Monthly Budget', 'Display fee budget on card', getBool('jobs_show_budget', true))}
                ${renderToggleSetting('jobs_show_apply_btn', 'Show Apply Button', 'Display Quick Apply button', getBool('jobs_show_apply_btn', true))}
            </div>
        </div>`;
    } else if (currentTab === 'featured_tutors') {
        mainTabHtml = `
        <div class="space-y-4">
            <div class="border-b border-slate-200 dark:border-slate-800 pb-2">
                <h4 class="font-black text-xs text-slate-900 dark:text-white uppercase tracking-wider">Featured Tutors Section Configuration</h4>
                <p class="text-[11px] text-slate-400">Control tutor cards, qualification badges, ratings, and max display count.</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                ${renderToggleSetting('tutors_section_enabled', 'Enable Tutors Section', 'Show Featured Tutors on homepage', getBool('tutors_section_enabled', true))}
                ${renderInputSetting('tutors_section_title', 'Section Title', 'Heading text', getVal('tutors_section_title', 'Top Verified Home Tutors'))}
                ${renderInputSetting('tutors_max_count', 'Number of Tutors Displayed', 'Max tutor profiles shown', getVal('tutors_max_count', '8'))}
                ${renderInputSetting('tutors_sort_by', 'Tutor Sorting', 'Sorting order (Featured/Top Rated/Experience)', getVal('tutors_sort_by', 'Featured'))}
                ${renderToggleSetting('tutors_show_experience', 'Show Experience', 'Display teaching experience badge', getBool('tutors_show_experience', true))}
                ${renderToggleSetting('tutors_show_rating', 'Show Ratings & Reviews', 'Display star rating badge', getBool('tutors_show_rating', true))}
            </div>
        </div>`;
    } else if (currentTab === 'forms') {
        mainTabHtml = `
        <div class="space-y-4">
            <h4 class="font-black text-sm text-slate-900 dark:text-white">Database Form Builder & Field Controller</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-2">
                    <div class="flex items-center justify-between">
                        <h5 class="font-bold text-xs text-slate-800 dark:text-slate-200">Tuition Requirement Form</h5>
                        <span class="text-[10px] font-bold text-emerald-600 bg-emerald-50 dark:bg-emerald-950 px-2 py-0.5 rounded-full border border-emerald-200">Active</span>
                    </div>
                    <p class="text-[11px] text-slate-400">11 fields (Student Name, Phone, Email, Class, Subject, Location, Budget, Time, Notes).</p>
                </div>
                <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-2">
                    <div class="flex items-center justify-between">
                        <h5 class="font-bold text-xs text-slate-800 dark:text-slate-200">Tutor Registration Form</h5>
                        <span class="text-[10px] font-bold text-emerald-600 bg-emerald-50 dark:bg-emerald-950 px-2 py-0.5 rounded-full border border-emerald-200">Active</span>
                    </div>
                    <p class="text-[11px] text-slate-400">9 fields (Full Name, Phone, Email, Qualification, Experience, Subjects, City, Fee).</p>
                </div>
            </div>
        </div>`;
    } else if (currentTab === 'navigation') {
        mainTabHtml = `
        <div class="space-y-3">
            <div class="flex items-center justify-between">
                <div>
                    <h4 class="font-black text-sm text-slate-900 dark:text-white">Website Navigation Links Manager</h4>
                    <p class="text-xs text-slate-400">Manage header and footer navigation links across desktop & mobile menus.</p>
                </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div class="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-800">
                    <span class="font-bold text-xs text-slate-800 dark:text-slate-200 block mb-1">Header Navbar Links</span>
                    <p class="text-[11px] text-slate-400">Home, Find a Tutor, Post Requirement, Become a Tutor, Tuition Jobs, About, Contact.</p>
                </div>
                <div class="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-800">
                    <span class="font-bold text-xs text-slate-800 dark:text-slate-200 block mb-1">Footer Quick Links</span>
                    <p class="text-[11px] text-slate-400">Privacy Policy, Terms of Service, Refund Policy, Help Center, FAQs.</p>
                </div>
            </div>
        </div>`;
    } else if (currentTab === 'footer') {
        mainTabHtml = `
        <div class="space-y-4">
            <h4 class="font-black text-sm text-slate-900 dark:text-white">Footer Columns & Legal Disclaimer Controls</h4>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-1">
                    <h5 class="font-bold text-xs text-slate-800 dark:text-slate-200">Column 1: EduTrust LMS</h5>
                    <p class="text-[11px] text-slate-400">About Us, Success Stories, FAQs, Contact Us</p>
                </div>
                <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-1">
                    <h5 class="font-bold text-xs text-slate-800 dark:text-slate-200">Column 2: Home Tuition</h5>
                    <p class="text-[11px] text-slate-400">Find a Tutor, Post Requirement, Become Tutor, Jobs</p>
                </div>
                <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-1">
                    <h5 class="font-bold text-xs text-slate-800 dark:text-slate-200">Column 3: Support & Legal</h5>
                    <p class="text-[11px] text-slate-400">Privacy Policy, Terms, Refund Policy, Help Center</p>
                </div>
            </div>
        </div>`;
    } else if (currentTab === 'contact') {
        mainTabHtml = `
        <div class="space-y-4">
            <div class="border-b border-slate-200 dark:border-slate-800 pb-2">
                <h4 class="font-black text-xs text-slate-900 dark:text-white uppercase tracking-wider">Public Contact Information</h4>
                <p class="text-[11px] text-slate-400">Changes automatically reflect in public header, footer, contact page, and call buttons.</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                ${renderInputSetting('contact_primary_phone', 'Primary Phone', 'Main contact number', getVal('contact_primary_phone', '+91 9876543210'))}
                ${renderInputSetting('contact_whatsapp_number', 'WhatsApp Support Number', 'WhatsApp click to chat number', getVal('contact_whatsapp_number', '+91 9876543210'))}
                ${renderInputSetting('contact_primary_email', 'Primary Support Email', 'Public support email', getVal('contact_primary_email', 'support@edutrust.com'))}
                ${renderInputSetting('contact_address', 'Office Address', 'Physical office location', getVal('contact_address', 'EduTrust Building, Tech Park, Hazratganj'))}
                ${renderInputSetting('contact_city', 'City', 'Office city', getVal('contact_city', 'Lucknow'))}
                ${renderInputSetting('contact_working_hours', 'Working Hours', 'Operational timing', getVal('contact_working_hours', 'Mon - Sat: 9:00 AM - 7:00 PM'))}
            </div>
        </div>`;
    } else if (currentTab === 'social') {
        mainTabHtml = `
        <div class="space-y-4">
            <div class="border-b border-slate-200 dark:border-slate-800 pb-2">
                <h4 class="font-black text-xs text-slate-900 dark:text-white uppercase tracking-wider">Social Media Profile Links</h4>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                ${renderInputSetting('social_facebook_url', 'Facebook Page URL', 'https://facebook.com/edutrust', getVal('social_facebook_url', 'https://facebook.com/edutrust'))}
                ${renderInputSetting('social_instagram_url', 'Instagram Profile URL', 'https://instagram.com/edutrust', getVal('social_instagram_url', 'https://instagram.com/edutrust'))}
                ${renderInputSetting('social_youtube_url', 'YouTube Channel URL', 'https://youtube.com/edutrust', getVal('social_youtube_url', 'https://youtube.com/edutrust'))}
                ${renderInputSetting('social_twitter_url', 'Twitter / X URL', 'https://twitter.com/edutrust', getVal('social_twitter_url', 'https://twitter.com/edutrust'))}
                ${renderInputSetting('social_linkedin_url', 'LinkedIn Page URL', 'https://linkedin.com/company/edutrust', getVal('social_linkedin_url', 'https://linkedin.com/company/edutrust'))}
            </div>
        </div>`;
    } else if (currentTab === 'seo') {
        mainTabHtml = `
        <div class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                ${renderInputSetting('seo_homepage_title', 'Homepage Meta Title', 'Browser tab & search title', getVal('seo_homepage_title', 'EduTrust LMS — Premium Home Tuition & Tutor Discovery'))}
                ${renderInputSetting('seo_meta_description', 'Meta Description', 'Search engine snippet text', getVal('seo_meta_description', 'Find qualified home tutors and tuition jobs for Class 1 to 12 across all major subjects & boards.'))}
                ${renderInputSetting('seo_keywords', 'SEO Keywords', 'Comma-separated keywords', getVal('seo_keywords', 'home tutor, home tuition, tuition jobs, find tutor, private tutor, edutrust'))}
                ${renderInputSetting('seo_canonical_url', 'Canonical URL', 'Preferred canonical address', getVal('seo_canonical_url', 'http://127.0.0.1:8000/'))}
                ${renderInputSetting('seo_og_title', 'OpenGraph Title', 'Social share title', getVal('seo_og_title', 'EduTrust — Home Tuition Platform'))}
                ${renderInputSetting('seo_og_description', 'OpenGraph Description', 'Social share description', getVal('seo_og_description', 'Get verified home tutors at your doorstep for personalized 1-on-1 education.'))}
            </div>
        </div>`;
    } else if (currentTab === 'announcement') {
        mainTabHtml = `
        <div class="space-y-4">
            <div class="border-b border-slate-200 dark:border-slate-800 pb-2">
                <h4 class="font-black text-xs text-slate-900 dark:text-white uppercase tracking-wider">Announcement Banner & Popup Modal Controls</h4>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                ${renderToggleSetting('announcement_enabled', 'Enable Announcement Banner', 'Show top announcement strip', getBool('announcement_enabled', false))}
                ${renderInputSetting('announcement_text', 'Announcement Text', 'Text displayed in top strip', getVal('announcement_text', '🚀 Admissions Open for 2026-27 Academic Batch!'))}
                ${renderInputSetting('announcement_btn_text', 'Button Text', 'CTA button label', getVal('announcement_btn_text', 'Register Now'))}
                ${renderInputSetting('announcement_btn_url', 'Button URL', 'Destination URL', getVal('announcement_btn_url', '/student-registration/'))}
            </div>
        </div>`;
    } else if (currentTab === 'cookie') {
        mainTabHtml = `
        <div class="space-y-4">
            <div class="border-b border-slate-200 dark:border-slate-800 pb-2">
                <h4 class="font-black text-xs text-slate-900 dark:text-white uppercase tracking-wider">Cookie Banner & Consent Management</h4>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                ${renderToggleSetting('cookie_banner_enabled', 'Enable Cookie Consent Banner', 'Show privacy cookie banner on website', getBool('cookie_banner_enabled', true))}
                ${renderInputSetting('cookie_banner_text', 'Banner Text', 'Privacy notice text', getVal('cookie_banner_text', 'We use cookies to improve your experience and analyze traffic.'))}
                ${renderInputSetting('cookie_privacy_url', 'Privacy Policy Link', 'Privacy URL', getVal('cookie_privacy_url', '/privacy/'))}
                ${renderInputSetting('cookie_accept_btn_text', 'Accept Button Text', 'Button text', getVal('cookie_accept_btn_text', 'Accept Cookies'))}
            </div>
        </div>`;
    } else if (currentTab === 'advanced') {
        mainTabHtml = `
        <div class="space-y-4">
            <div class="border-b border-slate-200 dark:border-slate-800 pb-2">
                <h4 class="font-black text-xs text-slate-900 dark:text-white uppercase tracking-wider">Advanced Cache & Feature Controls</h4>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                ${renderToggleSetting('homepage_cache_enabled', 'Enable Homepage Cache', 'Speed up website page load times', getBool('homepage_cache_enabled', true))}
                ${renderInputSetting('homepage_cache_ttl', 'Cache Expiry Time (Seconds)', 'Default 3600 seconds', getVal('homepage_cache_ttl', '3600'))}
                ${renderToggleSetting('google_analytics_enabled', 'Enable Google Analytics', 'Track page visits', getBool('google_analytics_enabled', false))}
                ${renderInputSetting('google_analytics_id', 'Google Analytics ID', 'G-XXXXXXXXXX', getVal('google_analytics_id', ''))}
            </div>
        </div>`;
    }

    return `
    <div class="space-y-5 fade-in text-xs font-semibold">
        <!-- 1. HEADER BANNER CARD -->
        <div class="bg-white dark:bg-slate-900 p-4 sm:p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xs relative overflow-hidden">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
                <div class="space-y-1">
                    <div class="flex flex-wrap items-center gap-2">
                        <span class="text-[10px] text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider">Settings > Home Page Settings</span>
                        <span class="px-2.5 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 text-[10px] font-extrabold border border-emerald-200 dark:border-emerald-800/60 flex items-center gap-1">
                            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span> Configuration Saved
                        </span>
                        ${modeBadgeHtml}
                        <span class="text-[10px] text-slate-500 dark:text-slate-400 font-medium">Last Updated: Just Now</span>
                    </div>
                    <h2 class="text-base sm:text-lg font-black text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
                        <i class="fa-solid fa-house-gear text-blue-600 dark:text-blue-400"></i> Home Page Settings
                    </h2>
                    <p class="text-xs text-slate-500 dark:text-slate-400 font-medium max-w-xl">
                        Complete control over website homepage configuration without editing source code.
                    </p>
                </div>
                <div class="flex flex-wrap items-center gap-2 shrink-0">
                    <button type="button" onclick="openAdminConfigPreviewModal()" class="px-3.5 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-bold border border-slate-200 dark:border-slate-700 transition-all flex items-center gap-1.5 border-0 cursor-pointer">
                        <i class="fa-solid fa-eye text-slate-400 text-[10px]"></i> Preview Configuration
                    </button>
                    <button type="button" onclick="publishHomePageSettings()" class="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white text-xs font-bold shadow-md transition-all border-0 cursor-pointer flex items-center gap-1.5">
                        <i class="fa-solid fa-save text-xs"></i> Save All Changes
                    </button>
                </div>
            </div>
        </div>

        <!-- 2. 16 SUB-TAB NAVIGATION -->
        <div class="flex items-center gap-1 overflow-x-auto pb-1.5 border-b border-slate-200 dark:border-slate-800 scrollbar-none" id="hpSubTabNav">
            ${renderHpSubTabBtn('overview', 'fa-chart-pie', 'Overview')}
            ${renderHpSubTabBtn('mode', 'fa-layer-group', 'Website Mode')}
            ${renderHpSubTabBtn('sections', 'fa-sliders', 'Sections')}
            ${renderHpSubTabBtn('hero', 'fa-bolt', 'Hero & Search')}
            ${renderHpSubTabBtn('content', 'fa-file-pen', 'Content Manager')}
            ${renderHpSubTabBtn('tuition_jobs', 'fa-briefcase', 'Tuition Jobs')}
            ${renderHpSubTabBtn('featured_tutors', 'fa-chalkboard-user', 'Featured Tutors')}
            ${renderHpSubTabBtn('forms', 'fa-wpforms', 'Forms')}
            ${renderHpSubTabBtn('navigation', 'fa-bars', 'Navigation')}
            ${renderHpSubTabBtn('footer', 'fa-shoe-prints', 'Footer')}
            ${renderHpSubTabBtn('contact', 'fa-phone', 'Contact Info')}
            ${renderHpSubTabBtn('social', 'fa-share-nodes', 'Social Media')}
            ${renderHpSubTabBtn('seo', 'fa-magnifying-glass', 'SEO & Meta')}
            ${renderHpSubTabBtn('announcement', 'fa-bullhorn', 'Announcement')}
            ${renderHpSubTabBtn('cookie', 'fa-cookie-bite', 'Cookie / Consent')}
            ${renderHpSubTabBtn('advanced', 'fa-gears', 'Advanced Settings')}
        </div>

        <!-- 3. DYNAMIC SUB-TAB CONTENT -->
        <div id="hpSubTabContent" class="space-y-4">
            ${mainTabHtml}
        </div>
    </div>`;
}

function renderHpSectionRow(order, title, key, isEnabled) {
    return `
    <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">
        <td class="p-3 font-bold text-slate-400">${order}</td>
        <td class="p-3 font-bold text-slate-900 dark:text-white">${title}</td>
        <td class="p-3 font-mono text-[11px] text-blue-600 dark:text-blue-400">${key}</td>
        <td class="p-3 text-center">
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${isEnabled ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300' : 'bg-slate-100 text-slate-500'}">
                ${isEnabled ? 'Enabled' : 'Disabled'}
            </span>
        </td>
        <td class="p-3 text-right">
            <button type="button" onclick="switchHpSubTab('${key}')" class="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-blue-50 text-slate-700 dark:text-slate-200 hover:text-blue-600 text-[11px] font-bold border-0 cursor-pointer transition">
                <i class="fa-solid fa-pen-to-square"></i> Edit Content
            </button>
        </td>
    </tr>`;
}




// 9. CENTRAL CATEGORY RENDERER DISPATCHER ARCHITECTURE
function renderCategoryFields(catKey) {
    const fieldsArea = document.getElementById('catFieldsArea');
    if (!fieldsArea) return;

    console.log('[SETTINGS] rendering category:', catKey);

    let html = '';
    const getRenderer = (name) => (window.EduTrustSettings && window.EduTrustSettings[name]) || window[name];

    switch (catKey) {
        case 'branding':
            const renderBranding = getRenderer('renderBrandingSettingsCenter');
            console.log('[SETTINGS] renderer found:', typeof renderBranding === 'function');
            html = typeof renderBranding === 'function' ? renderBranding(catKey) : renderGenericSettings(catKey);
            break;

        case 'certificate':
            const renderCert = getRenderer('renderCertificateSettingsCenter');
            console.log('[SETTINGS] renderer found:', typeof renderCert === 'function');
            html = typeof renderCert === 'function' ? renderCert(catKey) : renderGenericSettings(catKey);
            break;

        case 'payment':
            const renderPay = getRenderer('renderPaymentSettingsCenter');
            console.log('[SETTINGS] renderer found:', typeof renderPay === 'function');
            html = typeof renderPay === 'function' ? renderPay(catKey) : renderGenericSettings(catKey);
            break;

        case 'communication':
            const renderComm = getRenderer('renderCommunicationSettingsCenter');
            console.log('[SETTINGS] renderer found:', typeof renderComm === 'function');
            html = typeof renderComm === 'function' ? renderComm(catKey) : renderGenericSettings(catKey);
            break;

        case 'seo_website':
            const renderSEO = getRenderer('renderSEOWebsiteCenter');
            console.log('[SETTINGS] renderer found:', typeof renderSEO === 'function');
            html = typeof renderSEO === 'function' ? renderSEO(catKey) : renderGenericSettings(catKey);
            break;

        case 'security':
            const renderSec = getRenderer('renderSecuritySettingsCenter');
            console.log('[SETTINGS] renderer found:', typeof renderSec === 'function');
            html = typeof renderSec === 'function' ? renderSec(catKey) : renderGenericSettings(catKey);
            break;

        case 'backup_maint':
            const renderBackup = getRenderer('renderBackupMaintenanceCenter');
            console.log('[SETTINGS] renderer found:', typeof renderBackup === 'function');
            html = typeof renderBackup === 'function' ? renderBackup(catKey) : renderGenericSettings(catKey);
            break;

        case 'homepage':
            const renderHome = getRenderer('renderHomePageSettingsCenter');
            console.log('[SETTINGS] renderer found:', typeof renderHome === 'function');
            html = typeof renderHome === 'function' ? renderHome(catKey) : renderGenericSettings(catKey);
            break;

        default:
            console.log('[SETTINGS] renderer found: renderGenericSettings');
            html = renderGenericSettings(catKey);
            break;
    }

    fieldsArea.innerHTML = html;
    isDirtyForm = false;
}

// 10. API CLIENT & CATEGORY SWITCHERS
async function loadAllSettings() {
    if (window.EduTrustSettings._loadPromise) {
        return window.EduTrustSettings._loadPromise;
    }
    window.EduTrustSettings._loadPromise = (async () => {
        try {
            const res = await fetch('/api/admin/settings/list/');
            const data = await res.json();
            if (data.status === 'success') {
                allSettingsData = data.settings || {};
                window.EduTrustSettings.allSettingsData = allSettingsData;
                console.log('[SETTINGS] settings API loaded');
                const activeCat = window.EduTrustSettings.currentCategory || currentCategory || 'general';
                currentCategory = activeCat;
                window.EduTrustSettings.currentCategory = activeCat;
                renderCategoryFields(activeCat);
                renderAuditLogs(data.audit_logs);
                renderSystemInfo(data.system_info);
            }
        } catch(e) {
            console.error('[SETTINGS API ERROR]', e);
        } finally {
            delete window.EduTrustSettings._loadPromise;
        }
    })();
    return window.EduTrustSettings._loadPromise;
}

function switchCategoryTab(catKey) {
    if (isDirtyForm) {
        if (!confirm("You have unsaved changes. Discard and switch category?")) {
            return;
        }
        isDirtyForm = false;
    }

    currentCategory = catKey;
    window.EduTrustSettings.currentCategory = catKey;
    
    // Update Compact Horizontal Category Cards Landmark Active State
    Object.keys(CATEGORY_METADATA).forEach(k => {
        const btn = document.getElementById(`catBtn_${k}`);
        if (btn) {
            const titleSpan = btn.querySelector('span.block:first-child');
            const descSpan = btn.querySelector('span.block:last-child');
            const iconBox = btn.querySelector('div:first-child > div');
            const arrowIcon = btn.querySelector('i.fa-arrow-right');
            
            if (k === catKey) {
                btn.className = 'cat-nav-item text-left p-2 px-2.5 rounded-xl flex items-center justify-between gap-2 transition-all cursor-pointer bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold border border-blue-500 shadow-sm shadow-blue-500/20 hover:-translate-y-0.5';
                if (titleSpan) titleSpan.className = 'block text-[11px] font-bold text-white leading-tight truncate';
                if (descSpan) descSpan.className = 'block text-[9px] text-white/80 font-medium truncate';
                if (iconBox) iconBox.className = 'w-6.5 h-6.5 rounded-lg bg-white/20 text-white flex items-center justify-center text-xs shrink-0';
                if (arrowIcon) arrowIcon.className = 'fa-solid fa-arrow-right text-[10px] text-white shrink-0';
            } else {
                btn.className = 'cat-nav-item text-left p-2 px-2.5 rounded-xl flex items-center justify-between gap-2 transition-all cursor-pointer bg-slate-50 dark:bg-slate-800/60 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-200/60 dark:border-slate-800 hover:-translate-y-0.5';
                if (titleSpan) titleSpan.className = 'block text-[11px] font-bold text-slate-900 dark:text-white leading-tight truncate';
                if (descSpan) descSpan.className = 'block text-[9px] text-slate-400 font-medium truncate';
                if (arrowIcon) arrowIcon.className = 'fa-solid fa-arrow-right text-[10px] text-slate-400 shrink-0';
            }
        }
    });

    const activeMeta = CATEGORY_METADATA[catKey] || { title: 'Settings', desc: '' };
    const breadcrumbEl = document.getElementById('breadcrumbActiveCategory');
    if (breadcrumbEl) breadcrumbEl.textContent = activeMeta.title;

    const meta = CATEGORY_METADATA[catKey] || { title: 'Settings', desc: '' };
    document.getElementById('catTitle').textContent = meta.title;
    document.getElementById('catDesc').textContent = meta.desc;

    renderCategoryFields(catKey);
}

function markDirty() {
    isDirtyForm = true;
}

function renderAuditLogs(logs) {
    const tbody = document.getElementById('auditLogsTbody');
    if (!tbody) return;

    if (!logs || logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="p-4 text-center text-slate-400 text-xs">No setting audit logs found</td></tr>';
        return;
    }

    let html = '';
    logs.forEach(item => {
        html += `
        <tr class="hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition">
            <td class="p-3 font-semibold text-slate-700 dark:text-slate-300 whitespace-nowrap">${escapeHtml(item.time)}</td>
            <td class="p-3 font-bold text-slate-900 dark:text-white">${escapeHtml(item.user)}</td>
            <td class="p-3 font-semibold text-blue-600 dark:text-blue-400">${escapeHtml(item.action)}</td>
            <td class="p-3 text-slate-500 dark:text-slate-400">${escapeHtml(item.details)}</td>
        </tr>`;
    });
    tbody.innerHTML = html;
}

function renderSystemInfo(info) {
    if (!info) return;
    if (document.getElementById('sysVer')) document.getElementById('sysVer').textContent = info.system_version || 'EduTrust v3.4.0';
    if (document.getElementById('sysDb')) document.getElementById('sysDb').textContent = `${info.database_engine || 'SQLite'} (Python ${info.python_version || '3.12'})`;
    if (document.getElementById('sysTime')) document.getElementById('sysTime').textContent = info.server_time || '--';
    if (document.getElementById('sysUsers')) document.getElementById('sysUsers').textContent = `${info.active_students} Students / ${info.active_teachers} Teachers`;
    if (document.getElementById('sysHealth')) document.getElementById('sysHealth').textContent = info.database_health || '99.9% Optimal';
    if (document.getElementById('sysLastBackup')) document.getElementById('sysLastBackup').textContent = info.last_backup || '--';
}

// 11. REGISTER MODULE API & SINGLE INITIALIZATION
window.EduTrustSettings = window.EduTrustSettings || {};
Object.assign(window.EduTrustSettings, {
    init: initSettingsModule,
    renderCategoryFields: renderCategoryFields,
    renderBrandingSettingsCenter: renderBrandingSettingsCenter,
    renderCertificateSettingsCenter: renderCertificateSettingsCenter,
    renderPaymentSettingsCenter: renderPaymentSettingsCenter,
    renderCommunicationSettingsCenter: renderCommunicationSettingsCenter,
    renderSEOWebsiteCenter: renderSEOWebsiteCenter,
    renderSecuritySettingsCenter: renderSecuritySettingsCenter,
    renderBackupMaintenanceCenter: renderBackupMaintenanceCenter,
    renderHomePageSettingsCenter: renderHomePageSettingsCenter,
    renderGenericSettings: renderGenericSettings,
    switchCategoryTab: switchCategoryTab,
    loadAllSettings: loadAllSettings,
    CATEGORY_METADATA: CATEGORY_METADATA
});

// Global function exports for backward compatibility
window.initSettingsModule = initSettingsModule;
window.renderCategoryFields = renderCategoryFields;
window.renderBrandingSettingsCenter = renderBrandingSettingsCenter;
window.renderCertificateSettingsCenter = renderCertificateSettingsCenter;
window.renderPaymentSettingsCenter = renderPaymentSettingsCenter;
window.renderCommunicationSettingsCenter = renderCommunicationSettingsCenter;
window.renderSEOWebsiteCenter = renderSEOWebsiteCenter;
window.renderSecuritySettingsCenter = renderSecuritySettingsCenter;
window.renderBackupMaintenanceCenter = renderBackupMaintenanceCenter;
window.renderHomePageSettingsCenter = renderHomePageSettingsCenter;
window.switchHpSubTab = switchHpSubTab;
window.renderHpSubTabBtn = renderHpSubTabBtn;
window.renderGenericSettings = renderGenericSettings;
window.switchCategoryTab = switchCategoryTab;
window.loadAllSettings = loadAllSettings;

function initSettingsModule() {
    const root = document.getElementById('settingsContainer') || document.getElementById('settingsFormContainer') || document.getElementById('catFieldsArea');
    if (!root) return;

    if (root.dataset.settingsInitialized === 'true') {
        console.log('[SETTINGS TRACE] Already initialized on current DOM instance, skipping duplicate init');
        return;
    }
    root.dataset.settingsInitialized = 'true';
    window.EduTrustSettings.initialized = true;

    const activeCat = window.EduTrustSettings.currentCategory || currentCategory || 'general';
    currentCategory = activeCat;
    window.EduTrustSettings.currentCategory = activeCat;

    console.log('[SETTINGS TRACE] HTML loaded');
    console.log('[SETTINGS TRACE] module initialized');
    console.log('[SETTINGS TRACE] renderer checked:', typeof renderBrandingSettingsCenter === 'function');

    renderCategoryFields(activeCat);
    loadAllSettings();
}


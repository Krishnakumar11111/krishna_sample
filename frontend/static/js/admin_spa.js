/**
 * EduTrust LMS - Super Admin Single Page Application (SPA) Engine
 * Handles client routing, real REST/AJAX CRUD integrations, Chart.js lifecycle management,
 * global search API, persistent dark mode, and modal form handlers.
 */

window.AdminSPA = {
    currentModule: 'dashboard',
    charts: {},

    init: function() {
        this.bindEvents();
        this.initTheme();
    },

    highlightSidebar: function(moduleId) {
        if (typeof window.highlightSidebar === 'function') {
            window.highlightSidebar(moduleId);
        }
    },

    bindEvents: function() {
        const self = this;
        // Global search input listener
        const searchInput = document.getElementById('globalSearchInput');
        if (searchInput) {
            let timeout = null;
            searchInput.addEventListener('input', function() {
                clearTimeout(timeout);
                const q = this.value.trim();
                timeout = setTimeout(() => { self.fetchGlobalSearch(q); }, 300);
            });
        }
    },

    initTheme: function() {
        const savedTheme = localStorage.getItem('edutrust_admin_theme');
        if (savedTheme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    },

    toggleDarkMode: function() {
        const isDark = document.documentElement.classList.toggle('dark');
        localStorage.setItem('edutrust_admin_theme', isDark ? 'dark' : 'light');
        this.showToast(isDark ? 'Dark Mode Enabled' : 'Light Mode Enabled');
    },

    navTo: function(moduleId, updateHistory = true, event) {
        const e = event || window.event;
        if (e) {
            if (typeof e.preventDefault === 'function') e.preventDefault();
            if (typeof e.stopPropagation === 'function') e.stopPropagation();
        }
        if (typeof window.loadAdminModule === 'function') {
            return window.loadAdminModule(moduleId, updateHistory);
        }
    },

    onModuleLoaded: function(moduleId) {
        if (moduleId === 'dashboard') {
            this.initDashboardCharts();
        }
        if (moduleId === 'courses' || moduleId === 'batches') {
            if (typeof initBatchControlCenter === 'function') {
                initBatchControlCenter();
            }
        }
        if (moduleId === 'study_material' || moduleId === 'recorded_lectures') {
            initStudyMaterialModule();
            if (typeof loadAdminRealtimeRecordedLectures === 'function') {
                loadAdminRealtimeRecordedLectures();
            }
        }
        if (moduleId === 'user_logs') {
            initUserLogsModule();
        }
        if (moduleId === 'payments') {
            initPaymentsModule();
        }
        if (moduleId === 'settings') {
            if (typeof initSettingsModule === 'function') {
                initSettingsModule();
            }
        }
    },

    destroyCharts: function() {
        Object.keys(this.charts).forEach(key => {
            if (this.charts[key] && typeof this.charts[key].destroy === 'function') {
                this.charts[key].destroy();
            }
        });
        this.charts = {};
    },

    initDashboardCharts: function() {
        if (typeof Chart === 'undefined') return;

        this.destroyCharts();

        const ctxAnalytics = document.getElementById('analyticsChart');
        if (ctxAnalytics) {
            this.charts.analytics = new Chart(ctxAnalytics.getContext('2d'), {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                    datasets: [
                        { label: 'Students', data: [120, 250, 450, 780, 1100, 1500, 1900, 2400], borderColor: '#2563eb', tension: 0.4, fill: false },
                        { label: 'Teachers', data: [15, 30, 45, 60, 80, 95, 110, 130], borderColor: '#9333ea', tension: 0.4, fill: false },
                        { label: 'Revenue (₹k)', data: [50, 120, 220, 340, 510, 680, 890, 1245], borderColor: '#059669', tension: 0.4, fill: false }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });
        }

        const ctxRevenue = document.getElementById('revenueBarChart');
        if (ctxRevenue) {
            this.charts.revenue = new Chart(ctxRevenue.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: ['W1', 'W2', 'W3', 'W4'],
                    datasets: [{ label: 'Revenue', data: [250000, 310000, 290000, 395000], backgroundColor: '#10b981', borderRadius: 6 }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });
        }

        const ctxDoughnut = document.getElementById('studentDoughnutChart');
        if (ctxDoughnut) {
            this.charts.doughnut = new Chart(ctxDoughnut.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: ['Class 10', 'Class 11', 'Class 12', 'Others'],
                    datasets: [{ data: [34, 25, 23, 18], backgroundColor: ['#2563eb', '#4f46e5', '#9333ea', '#94a3b8'], cutout: '75%' }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });
        }
    },

    toggleSidebar: function(show) {
        const sidebar = document.getElementById('adminSidebar');
        const overlay = document.getElementById('sidebarOverlay');
        if (!sidebar) return;

        if (show === undefined) {
            sidebar.classList.toggle('-translate-x-full');
            if (overlay) overlay.classList.toggle('hidden');
        } else if (show) {
            sidebar.classList.remove('-translate-x-full');
            if (overlay) overlay.classList.remove('hidden');
        } else {
            sidebar.classList.add('-translate-x-full');
            if (overlay) overlay.classList.add('hidden');
        }
    },

    toggleDropdown: function(id) {
        const el = document.getElementById(id);
        if (el) el.classList.toggle('hidden');
    },

    openModal: function(id) {
        const el = document.getElementById(id);
        if (el) el.classList.remove('hidden');
    },

    closeModal: function(id) {
        const el = document.getElementById(id);
        if (el) el.classList.add('hidden');
    },

    showToast: function(msg, type = 'success', duration = 3500) {
        let toastType = type;
        if (typeof type === 'boolean') {
            toastType = type ? 'error' : 'success';
        }
        if (typeof window.renderGlobalAdminToast === 'function') {
            window.renderGlobalAdminToast(msg, toastType, duration);
        } else if (typeof window.showToast === 'function') {
            window.showToast(msg, toastType, duration);
        }
    },

    filterTable: function(tableId, query) {
        const table = document.getElementById(tableId);
        if (!table) return;
        const rows = table.querySelectorAll('tbody tr');
        const q = query.toLowerCase();
        rows.forEach(row => {
            const text = row.innerText.toLowerCase();
            row.style.display = text.includes(q) ? '' : 'none';
        });
    },

    fetchGlobalSearch: function(query) {
        if (!query) {
            const dropdown = document.getElementById('globalSearchResults');
            if (dropdown) dropdown.classList.add('hidden');
            return;
        }

        fetch(`/api/admin/global-search/?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(res => {
            const dropdown = document.getElementById('globalSearchResults');
            if (!dropdown) return;

            if (res.data && res.data.results && res.data.results.length > 0) {
                dropdown.innerHTML = res.data.results.map(r => `
                    <div onclick="navTo('${r.module_id}'); toggleDropdown('globalSearchResults');" class="p-3 border-b hover:bg-slate-50 cursor-pointer text-xs">
                        <span class="text-[9px] font-extrabold text-blue-600 uppercase block">${r.category}</span>
                        <span class="font-extrabold text-slate-900 block">${r.title}</span>
                        <span class="text-[10px] text-slate-400">${r.subtitle}</span>
                    </div>
                `).join('');
                dropdown.classList.remove('hidden');
            } else {
                dropdown.innerHTML = `<div class="p-4 text-center text-slate-400 text-xs font-bold">No results found for "${query}"</div>`;
                dropdown.classList.remove('hidden');
            }
        })
        .catch(err => console.log('Global search error:', err));
    }
};

// Global Helper Functions
if (typeof window.navTo === 'undefined') {
    window.navTo = function(id, e) {
        if (typeof window.loadAdminModule === 'function') {
            return window.loadAdminModule(id, true);
        }
        AdminSPA.navTo(id, true, e);
    };
}
function toggleSidebar(show) { AdminSPA.toggleSidebar(show); }
function toggleDropdown(id) { AdminSPA.toggleDropdown(id); }
function openModal(id) { AdminSPA.openModal(id); }
function closeModal(id) { AdminSPA.closeModal(id); }
function showToast(msg, isError) { AdminSPA.showToast(msg, isError); }
function filterTable(tableId, query) { AdminSPA.filterTable(tableId, query); }
function toggleDarkMode() { AdminSPA.toggleDarkMode(); }

// AJAX Student Deletion
function deleteStudent(id, name) {
    if (!confirm(`Are you sure you want to delete student "${name}"?`)) return;

    fetch('/api/admin/students/', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: id })
    })
    .then(res => {
        if (!res.ok) throw new Error('Deletion failed');
        return res.json();
    })
    .then(data => {
        showToast(`Student ${name} deleted successfully!`);
        const row = document.getElementById(`student-row-${id}`);
        if (row) row.remove();
    })
    .catch(err => {
        showToast('Failed to delete student.', true);
    });
}

// AJAX Teacher Approval / Rejection
function updateTeacherStatus(id, action) {
    fetch('/api/admin/teachers/', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: id, action: action })
    })
    .then(res => res.json())
    .then(data => {
        showToast(`Teacher status updated to ${action.toUpperCase()}`);
        navTo('teachers');
    })
    .catch(err => {
        showToast('Failed to update teacher status', true);
    });
}

window.viewTeacherDetails = function(teacherId) {
    fetch('/api/admin/teachers/?id=' + teacherId)
        .then(res => res.json())
        .then(resData => {
            const t = (resData.data && resData.data.teacher) ? resData.data.teacher : resData.teacher;
            if (t) {
                const photoEl = document.getElementById('vTeacherPhoto');
                if (photoEl) photoEl.src = t.photo_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(t.full_name)}&background=2563eb&color=fff`;
                
                const nameEl = document.getElementById('vTeacherName');
                if (nameEl) nameEl.textContent = t.full_name;
                
                const metaEl = document.getElementById('vTeacherMeta');
                if (metaEl) metaEl.textContent = `ID: ${t.teacher_id} • Registered: ${t.registration_date} at ${t.registration_time}`;
                
                const emailEl = document.getElementById('vTeacherEmail'); if (emailEl) emailEl.textContent = t.email || 'N/A';
                const mobEl = document.getElementById('vTeacherMobile'); if (mobEl) mobEl.textContent = t.mobile || 'N/A';
                const genEl = document.getElementById('vTeacherGender'); if (genEl) genEl.textContent = t.gender || 'N/A';
                const locEl = document.getElementById('vTeacherLocation'); if (locEl) locEl.textContent = `${t.city || 'City'}, ${t.state || 'State'}`;
                const pinEl = document.getElementById('vTeacherPincode'); if (pinEl) pinEl.textContent = t.pincode || 'N/A';
                const accEl = document.getElementById('vTeacherAccountStatus'); if (accEl) accEl.textContent = t.account_status || 'Active';

                const qualEl = document.getElementById('vTeacherQualification'); if (qualEl) qualEl.textContent = t.qualification || 'Graduate';
                const expEl = document.getElementById('vTeacherExperience'); if (expEl) expEl.textContent = t.experience || 'Fresher';
                const modeEl = document.getElementById('vTeacherMode'); if (modeEl) modeEl.textContent = t.tuition_mode || 'Home & Online';
                const subjEl = document.getElementById('vTeacherSubjects'); if (subjEl) subjEl.textContent = t.subjects || 'General';
                const clsEl = document.getElementById('vTeacherClasses'); if (clsEl) clsEl.textContent = t.teaching_classes || 'All Classes';
                const feeEl = document.getElementById('vTeacherFee'); if (feeEl) feeEl.textContent = t.expected_fee ? (`₹${t.expected_fee}`) : 'Negotiable';
                const bioEl = document.getElementById('vTeacherBio'); if (bioEl) bioEl.textContent = t.bio || 'Experienced faculty specializing in subject concepts and student mentoring.';

                const vBadge = document.getElementById('vTeacherVerificationBadge');
                if (vBadge) {
                    vBadge.textContent = t.verification_status;
                    if (t.verification_status === 'Approved') vBadge.className = 'px-3 py-1 rounded-full text-xs font-black bg-emerald-100 text-emerald-800';
                    else if (t.verification_status === 'Rejected') vBadge.className = 'px-3 py-1 rounded-full text-xs font-black bg-rose-100 text-rose-800';
                    else vBadge.className = 'px-3 py-1 rounded-full text-xs font-black bg-amber-100 text-amber-800';
                }

                const actBtns = document.getElementById('vTeacherActionButtons');
                if (actBtns) {
                    actBtns.innerHTML = `
                        <button type="button" onclick="updateTeacherStatus(${t.id}, 'approve'); closeModal('modalViewTeacherDetails');" class="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs rounded-xl border-0 cursor-pointer transition-all shadow-xs">Approve</button>
                        <button type="button" onclick="updateTeacherStatus(${t.id}, 'reject'); closeModal('modalViewTeacherDetails');" class="px-3.5 py-2 bg-rose-600 hover:bg-rose-700 text-white font-extrabold text-xs rounded-xl border-0 cursor-pointer transition-all shadow-xs">Reject</button>
                        <button type="button" onclick="closeModal('modalViewTeacherDetails')" class="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold text-xs rounded-xl border-0 cursor-pointer transition-all">Close</button>
                    `;
                }

                if (typeof openModal === 'function') openModal('modalViewTeacherDetails');
            } else {
                alert('Error loading teacher details.');
            }
        })
        .catch(err => alert('Network error: ' + err.message));
};

window.viewStudentDetails = function(studentId) {
    fetch('/api/admin/students/?id=' + studentId)
        .then(res => res.json())
        .then(resData => {
            const s = (resData.data && resData.data.student) ? resData.data.student : resData.student;
            if (s) {
                const av = document.getElementById('vStudentAvatar');
                if (av) av.textContent = (s.full_name || 'ST').substring(0, 2).toUpperCase();

                const nameEl = document.getElementById('vStudentName'); if (nameEl) nameEl.textContent = s.full_name;
                const metaEl = document.getElementById('vStudentMeta'); if (metaEl) metaEl.textContent = `ID: ${s.student_id} • Joined: ${s.registration_date}`;

                const emailEl = document.getElementById('vStudentEmail'); if (emailEl) emailEl.textContent = s.email || 'N/A';
                const mobEl = document.getElementById('vStudentMobile'); if (mobEl) mobEl.textContent = s.mobile || 'N/A';
                const clsEl = document.getElementById('vStudentClass'); if (clsEl) clsEl.textContent = s.student_class || 'Class 10 CBSE';
                const genEl = document.getElementById('vStudentGender'); if (genEl) genEl.textContent = s.gender || 'Not Specified';
                const locEl = document.getElementById('vStudentLocation'); if (locEl) locEl.textContent = `${s.city || 'City'}, ${s.state || 'State'}`;
                const stEl = document.getElementById('vStudentStatus'); if (stEl) stEl.textContent = s.account_status || 'Active';

                const regEl = document.getElementById('vStudentRegDate'); if (regEl) regEl.textContent = `${s.registration_date} at ${s.registration_time}`;
                const devEl = document.getElementById('vStudentDeviceInfo'); if (devEl) devEl.textContent = s.device_info || 'Web Browser';

                if (typeof openModal === 'function') openModal('modalViewStudentDetails');
            } else {
                alert('Error loading student details.');
            }
        })
        .catch(err => alert('Network error: ' + err.message));
};

// Form Submit AJAX Handler
function handleFormSubmit(e, successMsg) {
    e.preventDefault();
    const form = e.target;
    const isTeacherForm = form.closest('#modalAddTeacher') !== null;
    const isCourseForm = form.closest('#modalAddCourse') !== null;
    const isCreateBatchForm = form.closest('#modalCreateBatch') !== null;

    let endpoint = '/api/admin/students/';
    let targetModule = 'students';

    if (isTeacherForm) {
        endpoint = '/api/admin/teachers/';
        targetModule = 'teachers';
    } else if (isCourseForm || isCreateBatchForm) {
        endpoint = '/api/admin/courses/';
        targetModule = 'courses';
    }

    const hasFile = form.querySelector('input[type="file"]') && form.querySelector('input[type="file"]').files.length > 0;
    let requestOptions = {};

    if (hasFile) {
        const multipartData = new FormData(form);
        requestOptions = {
            method: 'POST',
            body: multipartData
        };
    } else {
        const inputs = form.querySelectorAll('input, select, textarea');
        const formData = {};
        inputs.forEach(input => {
            if (input.name) {
                formData[input.name] = input.value;
            }
        });
        requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        };
    }

    fetch(endpoint, requestOptions)
    .then(res => {
        if (!res.ok) {
            return res.json().then(json => { throw new Error(json.message || 'Operation failed'); });
        }
        return res.json();
    })
    .then(data => {
        document.querySelectorAll('#modalContainer > div').forEach(m => m.classList.add('hidden'));
        showToast(data.message || successMsg);
        form.reset();
        const imgPrev = document.getElementById('modalBannerImagePreview');
        if (imgPrev) imgPrev.classList.add('hidden');
        navTo(targetModule);
    })
    .catch(err => {
        showToast(err.message || 'Failed to submit form', true);
    });
}

function previewBatchBanner(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        const fileNameEl = document.getElementById('modalBannerFileName');
        const imgPrev = document.getElementById('modalBannerImagePreview');
        if (fileNameEl) fileNameEl.innerText = `Selected: ${file.name}`;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            if (imgPrev) {
                imgPrev.src = e.target.result;
                imgPrev.classList.remove('hidden');
            }
        };
        reader.readAsDataURL(file);
    }
}

// Session Dropdown Change Handler
function handleSessionChange(sessionValue) {
    fetch('/api/admin/settings/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session: sessionValue })
    })
    .then(res => res.json())
    .then(data => {
        showToast(`Academic Session updated to ${sessionValue}`);
        const textEl = document.getElementById('heroSessionText');
        if (textEl) textEl.innerText = sessionValue;
    });
}

// ==========================================
// COURSE CREATION WIZARD ENGINE
// ==========================================
let wizardState = {
    currentStep: 1,
    subjects: [
        { name: 'Mathematics', code: 'MATH-101', faculty_name: 'Krishna' },
        { name: 'Physics', code: 'PHY-101', faculty_name: 'Faculty TBD' },
        { name: 'Chemistry', code: 'CHEM-101', faculty_name: 'Ruchi' },
        { name: 'Hindi', code: 'HIN-101', faculty_name: 'Soni' },
        { name: 'English', code: 'ENG-101', faculty_name: 'Sweety' }
    ]
};

function goToWizardStep(stepNum) {
    wizardState.currentStep = stepNum;
    for (let i = 1; i <= 5; i++) {
        const stepEl = document.getElementById(`wizard-step-${i}`);
        const indEl = document.getElementById(`step-indicator-${i}`);
        if (stepEl) {
            if (i === stepNum) stepEl.classList.remove('hidden');
            else stepEl.classList.add('hidden');
        }
        if (indEl) {
            if (i === stepNum) {
                indEl.className = 'p-2.5 rounded-xl bg-amber-50 text-amber-700 border-2 border-amber-500 cursor-pointer transition-all shadow-xs';
            } else if (i < stepNum) {
                indEl.className = 'p-2.5 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-300 cursor-pointer transition-all';
            } else {
                indEl.className = 'p-2.5 rounded-xl bg-slate-100 text-slate-400 border border-slate-200 cursor-pointer transition-all';
            }
        }
    }
    if (stepNum === 2) renderWizardSubjects();
    updateLivePreview();
}

function renderWizardSubjects() {
    const container = document.getElementById('wizardSubjectsContainer');
    if (!container) return;

    container.innerHTML = wizardState.subjects.map((s, idx) => `
        <div class="p-3 bg-slate-50 rounded-2xl border border-slate-200 flex items-center justify-between gap-2">
            <div class="grid grid-cols-3 gap-2 flex-1">
                <input type="text" value="${s.name}" oninput="wizardState.subjects[${idx}].name=this.value; updateLivePreview();" placeholder="Subject Name" class="border p-2 rounded-xl text-xs bg-white font-bold">
                <input type="text" value="${s.code}" oninput="wizardState.subjects[${idx}].code=this.value;" placeholder="Code e.g. MATH-101" class="border p-2 rounded-xl text-xs bg-white">
                <select onchange="wizardState.subjects[${idx}].faculty_name=this.value; updateLivePreview();" class="border p-2 rounded-xl text-xs bg-white font-semibold">
                    <option value="Krishna" ${s.faculty_name === 'Krishna' ? 'selected' : ''}>Krishna</option>
                    <option value="Ruchi" ${s.faculty_name === 'Ruchi' ? 'selected' : ''}>Ruchi</option>
                    <option value="Soni" ${s.faculty_name === 'Soni' ? 'selected' : ''}>Soni</option>
                    <option value="Sweety" ${s.faculty_name === 'Sweety' ? 'selected' : ''}>Sweety</option>
                    <option value="Faculty TBD" ${s.faculty_name === 'Faculty TBD' ? 'selected' : ''}>Faculty TBD</option>
                </select>
            </div>
            <button onclick="removeWizardSubject(${idx})" class="text-rose-500 hover:text-rose-700 p-2 border-0 cursor-pointer text-xs"><i class="fas fa-trash"></i></button>
        </div>
    `).join('');
}

function addWizardSubjectRow() {
    const idx = wizardState.subjects.length + 1;
    wizardState.subjects.push({ name: `Subject ${idx}`, code: `SUB-10${idx}`, faculty_name: 'Faculty TBD' });
    renderWizardSubjects();
    updateLivePreview();
}

function removeWizardSubject(idx) {
    wizardState.subjects.splice(idx, 1);
    renderWizardSubjects();
    updateLivePreview();
}

function calculateWizardPrice() {
    const orig = parseFloat(document.getElementById('w_price')?.value || 3499);
    const type = document.getElementById('w_discount_type')?.value || 'Fixed Amount';
    const val = parseFloat(document.getElementById('w_discount_value')?.value || 500);

    let finalPrice = orig;
    if (type === 'Fixed Amount') {
        finalPrice = Math.max(0, orig - val);
    } else {
        finalPrice = Math.max(0, orig - (orig * (val / 100)));
    }

    const finalEl = document.getElementById('wizardFinalPriceDisplay');
    const origEl = document.getElementById('summaryOriginalFee');
    const discEl = document.getElementById('summaryDiscountOff');

    if (finalEl) finalEl.innerText = `₹${Math.round(finalPrice).toLocaleString()}`;
    if (origEl) origEl.innerText = `₹${Math.round(orig).toLocaleString()}`;
    if (discEl) discEl.innerText = type === 'Fixed Amount' ? `₹${val}` : `${val}%`;

    return finalPrice;
}

function updateLivePreview() {
    const title = document.getElementById('w_title')?.value || 'Class 9 CBSE';
    const className = document.getElementById('w_class')?.value || 'Class 9';
    const board = document.getElementById('w_board')?.value || 'CBSE';
    const session = document.getElementById('w_session')?.value || '2026–27';
    const shortDesc = document.getElementById('w_short_desc')?.value || 'Comprehensive batch covering complete syllabus';
    const batchName = document.getElementById('w_batch_name')?.value || 'Saksham Batch 2026–27';
    const maxStudents = document.getElementById('w_max_students')?.value || '50';
    const origPrice = parseFloat(document.getElementById('w_price')?.value || 3499);
    const finalPrice = calculateWizardPrice();

    // Bind Right Live Card Preview Elements
    if (document.getElementById('prevClassBadge')) document.getElementById('prevClassBadge').innerText = className;
    if (document.getElementById('prevBoardBadge')) document.getElementById('prevBoardBadge').innerText = `${className} • ${board}`;
    if (document.getElementById('prevSessionBadge')) document.getElementById('prevSessionBadge').innerText = session;
    if (document.getElementById('prevTitle')) document.getElementById('prevTitle').innerText = title;
    if (document.getElementById('prevShortDesc')) document.getElementById('prevShortDesc').innerText = shortDesc;
    if (document.getElementById('prevBatchName')) document.getElementById('prevBatchName').innerText = batchName;
    if (document.getElementById('prevMaxStudents')) document.getElementById('prevMaxStudents').innerText = maxStudents;
    if (document.getElementById('prevOriginalPrice')) document.getElementById('prevOriginalPrice').innerText = `₹${Math.round(origPrice).toLocaleString()}`;
    if (document.getElementById('prevFinalPrice')) document.getElementById('prevFinalPrice').innerText = `₹${Math.round(finalPrice).toLocaleString()}`;
    if (document.getElementById('prevSubjectCount')) document.getElementById('prevSubjectCount').innerText = wizardState.subjects.length;

    // Subjects Live List
    const subListEl = document.getElementById('prevSubjectsList');
    if (subListEl) {
        subListEl.innerHTML = wizardState.subjects.map(s => `
            <div class="flex justify-between"><span>${s.name}</span><span class="text-blue-600 font-bold">${s.faculty_name}</span></div>
        `).join('');
    }

    // Review Step updates
    if (document.getElementById('reviewTitle')) document.getElementById('reviewTitle').innerText = title;
    if (document.getElementById('reviewSession')) document.getElementById('reviewSession').innerText = `Academic Session: ${session} • Board: ${board}`;
    if (document.getElementById('reviewBatch')) document.getElementById('reviewBatch').innerText = `Batch: ${batchName} (Capacity: ${maxStudents})`;
    if (document.getElementById('reviewPrice')) document.getElementById('reviewPrice').innerText = `Final Enrollment Fee: ₹${Math.round(finalPrice).toLocaleString()}`;
}

function saveCourseWizard(status) {
    const payload = {
        title: document.getElementById('w_title')?.value || 'Class 9 CBSE',
        class_name: document.getElementById('w_class')?.value || 'Class 9',
        board: document.getElementById('w_board')?.value || 'CBSE',
        academic_session: document.getElementById('w_session')?.value || '2026-27',
        course_type: document.getElementById('w_type')?.value || 'Regular',
        short_description: document.getElementById('w_short_desc')?.value || '',
        description: document.getElementById('w_desc')?.value || '',
        course_status: status,
        subjects: wizardState.subjects,
        batch_name: document.getElementById('w_batch_name')?.value || 'Saksham Batch 2026–27',
        batch_code: document.getElementById('w_batch_code')?.value || 'SAK-2026',
        batch_mode: document.getElementById('w_batch_mode')?.value || 'Online',
        class_timing: document.getElementById('w_class_timing')?.value || '4:00 PM - 6:00 PM',
        days: document.getElementById('w_days')?.value || 'Mon, Wed, Fri',
        max_students: document.getElementById('w_max_students')?.value || 50,
        branch_classroom: document.getElementById('w_branch')?.value || 'Main Campus Room 101',
        price: parseFloat(document.getElementById('w_price')?.value || 3499),
        discount_type: document.getElementById('w_discount_type')?.value || 'Fixed Amount',
        discount_value: parseFloat(document.getElementById('w_discount_value')?.value || 500),
        final_price: calculateWizardPrice()
    };

    fetch('/api/admin/courses/wizard/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        showToast(data.message || 'Course Saved Successfully!');
        navTo('courses');
    })
    .catch(err => {
        showToast('Failed to save course wizard', true);
    });
}

function switchManageTab(tabId) {
    document.querySelectorAll('[id^="mtab-"]').forEach(btn => {
        btn.className = 'px-4 py-2 rounded-xl bg-slate-100 text-slate-600 hover:bg-slate-200 border-0 cursor-pointer shrink-0';
    });
    const activeBtn = document.getElementById(`mtab-${tabId}`);
    if (activeBtn) activeBtn.className = 'px-4 py-2 rounded-xl bg-blue-600 text-white border-0 cursor-pointer shrink-0 shadow-2xs';
}

// DYNAMIC SUBJECT TEACHERS PARSER & RENDERER
function handleDynamicSubjects(subjectVal) {
    const container = document.getElementById('dynamicSubjectTeachersContainer');
    if (!container) return;

    if (!subjectVal || !subjectVal.trim()) {
        container.innerHTML = `
            <div class="p-3 bg-slate-50 rounded-xl border border-dashed border-slate-200 text-[11px] text-slate-400 text-center font-medium">
                <i class="fas fa-info-circle mr-1 text-blue-500"></i> Type subjects above (e.g. <i>Mathematics, physics, hindi, english</i>) to assign teacher names.
            </div>
        `;
        return;
    }

    const subjects = subjectVal.split(',')
        .map(s => s.trim())
        .filter(s => s.length > 0);

    if (subjects.length === 0) {
        container.innerHTML = `
            <div class="p-3 bg-slate-50 rounded-xl border border-dashed border-slate-200 text-[11px] text-slate-400 text-center font-medium">
                Type subjects above to assign teacher names.
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div class="p-3.5 bg-slate-50/90 rounded-2xl border border-slate-200 space-y-2.5">
            <span class="text-[11px] font-extrabold text-slate-900 uppercase flex items-center gap-1.5">
                <i class="fas fa-user-tag text-amber-500"></i> Assign Teacher Name for Each Typed Subject (${subjects.length})
            </span>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                ${subjects.map((sub, idx) => `
                    <div class="bg-white p-2.5 rounded-xl border border-slate-200 shadow-2xs space-y-1">
                        <span class="text-[11px] font-black text-blue-700 block"><i class="fas fa-book mr-1 text-blue-400"></i>${sub}</span>
                        <input type="text" name="teacher_for_${sub}" placeholder="Teacher name for ${sub}..." class="w-full border p-2 rounded-lg text-xs outline-none focus:ring-2 focus:ring-amber-500/20 font-semibold text-slate-800 bg-slate-50/50">
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// DYNAMIC BOARD SELECTOR HANDLER
function handleBoardChange(val) {
    const container = document.getElementById('stateBoardSelectContainer');
    if (!container) return;
    if (val === 'State Board') {
        container.classList.remove('hidden');
    } else {
        container.classList.add('hidden');
    }
}

// REALTIME MODAL DISCOUNT CALCULATOR
function calculateModalDiscount() {
    const orig = parseFloat(document.getElementById('m_price')?.value || 0);
    const type = document.getElementById('m_disc_type')?.value || 'Fixed Amount';
    const val = parseFloat(document.getElementById('m_disc_val')?.value || 0);

    let finalPrice = orig;
    if (type === 'Fixed Amount') {
        finalPrice = Math.max(0, orig - val);
    } else {
        finalPrice = Math.max(0, orig - (orig * (val / 100)));
    }

    const badge = document.getElementById('modalFinalPriceBadge');
    if (badge) {
        if (val > 0) {
            badge.innerHTML = `Final Fee: <span class="text-emerald-600 font-black text-sm">₹${Math.round(finalPrice).toLocaleString()}</span> <span class="text-[10px] text-slate-400 font-normal">(${type === 'Fixed Amount' ? '₹' + val : val + '%'} off)</span>`;
        } else {
            badge.innerHTML = `Final Fee: <span class="text-emerald-600 font-black text-sm">₹${Math.round(orig).toLocaleString()}</span>`;
        }
    }
}

// ==========================================
// STUDY MATERIAL MODULE — 100% REAL DATA
// ==========================================

window.userHasSwitchedRecordedTab = false;

window.switchRecordedTab = function(tabType) {
    window.userHasSwitchedRecordedTab = true;
    const fileContent = document.getElementById('recTabContentFile');
    const linkContent = document.getElementById('recTabContentLink');
    const fileBtn = document.getElementById('recTabBtnFile');
    const linkBtn = document.getElementById('recTabBtnLink');

    if (!fileContent || !linkContent) return;

    if (tabType === 'file') {
        fileContent.classList.remove('hidden');
        linkContent.classList.add('hidden');
        if (fileBtn) fileBtn.className = 'px-3 py-1.5 rounded-lg bg-rose-600 text-white shadow-xs transition-all border-0 cursor-pointer flex items-center gap-1.5';
        if (linkBtn) linkBtn.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition-all border-0 cursor-pointer flex items-center gap-1.5';
    } else {
        fileContent.classList.add('hidden');
        linkContent.classList.remove('hidden');
        if (fileBtn) fileBtn.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition-all border-0 cursor-pointer flex items-center gap-1.5';
        if (linkBtn) linkBtn.className = 'px-3 py-1.5 rounded-lg bg-rose-600 text-white shadow-xs transition-all border-0 cursor-pointer flex items-center gap-1.5';
    }
};

window.loadAdminRealtimeRecordedLectures = function() {
    fetch('/api/admin/live-classes/')
        .then(res => res.json())
        .then(data => {
            const rawList = data.classes || data.live_classes || [];
            const fileContainer = document.querySelector('#recTabContentFile tbody');
            const linkContainer = document.querySelector('#recTabContentLink tbody');
            const fileBtn = document.getElementById('recTabBtnFile');
            const linkBtn = document.getElementById('recTabBtnLink');

            if (!fileContainer || !linkContainer) return;

            const fileList = rawList.filter(lc => lc.recorded_video_file_url || lc.video_source_type === 'file');
            const linkList = rawList.filter(lc => (lc.recorded_video_link || lc.meet_link) && lc.video_source_type !== 'file');

            const kpiRecordedEl = document.getElementById('kpiTotalRecordedLectures');
            if (kpiRecordedEl) {
                kpiRecordedEl.textContent = fileList.length + linkList.length;
            }

            if (fileBtn) fileBtn.innerHTML = `<i class="fas fa-file-video"></i> 📁 Uploaded Video Files (${fileList.length})`;
            if (linkBtn) linkBtn.innerHTML = `<i class="fab fa-youtube text-rose-500"></i> 🎥 YouTube / Stream Links (${linkList.length})`;

            // Auto-switch to YouTube tab if MP4 video files is 0 and links exist
            if (!window.userHasSwitchedRecordedTab && fileList.length === 0 && linkList.length > 0) {
                const fileContent = document.getElementById('recTabContentFile');
                const linkContent = document.getElementById('recTabContentLink');
                if (fileContent && linkContent) {
                    fileContent.classList.add('hidden');
                    linkContent.classList.remove('hidden');
                    if (fileBtn) fileBtn.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition-all border-0 cursor-pointer flex items-center gap-1.5';
                    if (linkBtn) linkBtn.className = 'px-3 py-1.5 rounded-lg bg-rose-600 text-white shadow-xs transition-all border-0 cursor-pointer flex items-center gap-1.5';
                }
            }

            // Render File Table
            if (fileList.length > 0) {
                let fHtml = '';
                fileList.forEach(lc => {
                    fHtml += `
                    <tr class="hover:bg-slate-50/50 transition-colors">
                        <td class="p-3 font-mono text-[10px] text-slate-400">LC-${lc.id || lc.live_class_id}</td>
                        <td class="p-3 font-bold text-slate-800">${lc.title}</td>
                        <td class="p-3 text-slate-600"><span class="bg-blue-50 text-blue-700 font-bold px-2 py-0.5 rounded-md text-[10px]">${lc.class_name || 'Class 10'}</span> ${lc.subject || ''}</td>
                        <td class="p-3"><span class="bg-emerald-50 text-emerald-700 text-[10px] font-extrabold px-2.5 py-1 rounded-lg border border-emerald-200 flex items-center gap-1 w-fit"><i class="fas fa-file-video"></i> MP4 Video File</span></td>
                        <td class="p-3 text-slate-600 font-medium">${lc.teacher_name || 'EduTrust Faculty'}</td>
                        <td class="p-3 text-slate-700 font-bold text-[11px] whitespace-nowrap"><i class="far fa-clock text-emerald-600 mr-1"></i>${lc.created_at || 'Recently Shared'}</td>
                        <td class="p-3 text-right whitespace-nowrap">
                            <div class="flex items-center justify-end gap-1.5">
                                <button type="button" onclick="openEditRecordedLectureModal(${lc.id}, '${escapeJsStr(lc.title)}', '${escapeJsStr(lc.class_name)}', '${escapeJsStr(lc.subject)}', '${escapeJsStr(lc.chapter)}', '${escapeJsStr(lc.teacher_name)}', '${escapeJsStr(lc.recorded_video_file_url)}')" class="px-3 py-1.5 bg-amber-500 hover:bg-amber-600 text-white font-extrabold text-[11px] rounded-xl border-0 cursor-pointer transition-all inline-flex items-center gap-1 shadow-2xs">
                                    <i class="fas fa-edit"></i> Edit
                                </button>
                                <button type="button" onclick="deleteRecordedLecture(${lc.id}, '${escapeJsStr(lc.title)}')" class="px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white font-extrabold text-[11px] rounded-xl border-0 cursor-pointer transition-all inline-flex items-center gap-1 shadow-2xs">
                                    <i class="fas fa-trash-alt"></i> Delete
                                </button>
                            </div>
                        </td>
                    </tr>`;
                });
                fileContainer.innerHTML = fHtml;
            } else {
                fileContainer.innerHTML = `<tr><td colspan="7" class="p-8 text-center text-slate-400 text-xs"><i class="fas fa-file-video text-2xl mb-1 text-slate-300 block"></i><p class="font-bold text-slate-700">No MP4 video files uploaded yet</p><p class="text-[10px] text-slate-400">Direct MP4 video file uploads from Live Classes & Lectures will be listed here automatically.</p></td></tr>`;
            }

            // Render Link Table
            if (linkList.length > 0) {
                let lHtml = '';
                linkList.forEach(lc => {
                    const url = lc.recorded_video_link || lc.meet_link || '#';
                    lHtml += `
                    <tr class="hover:bg-slate-50/50 transition-colors">
                        <td class="p-3 font-mono text-[10px] text-slate-400">LC-${lc.id || lc.live_class_id}</td>
                        <td class="p-3 font-bold text-slate-800">${lc.title}</td>
                        <td class="p-3 text-slate-600"><span class="bg-purple-50 text-purple-700 font-bold px-2 py-0.5 rounded-md text-[10px]">${lc.class_name || 'Class 10'}</span> ${lc.subject || ''}</td>
                        <td class="p-3"><span class="bg-rose-50 text-rose-700 text-[10px] font-extrabold px-2.5 py-1 rounded-lg border border-rose-200 flex items-center gap-1 w-fit"><i class="fab fa-youtube"></i> YouTube / Stream Link</span></td>
                        <td class="p-3 text-slate-600 font-medium">${lc.teacher_name || 'EduTrust Faculty'}</td>
                        <td class="p-3 text-slate-700 font-bold text-[11px] whitespace-nowrap"><i class="far fa-clock text-rose-500 mr-1"></i>${lc.created_at || 'Recently Shared'}</td>
                        <td class="p-3 font-mono text-[10px] text-blue-600 truncate max-w-[150px]"><a href="${url}" target="_blank" class="text-blue-600 hover:text-blue-800 font-bold hover:underline inline-flex items-center gap-1"><i class="fas fa-external-link-alt text-[9px]"></i> ${url}</a></td>
                        <td class="p-3 text-right whitespace-nowrap">
                            <div class="flex items-center justify-end gap-1.5">
                                <button type="button" onclick="openEditRecordedLectureModal(${lc.id}, '${escapeJsStr(lc.title)}', '${escapeJsStr(lc.class_name)}', '${escapeJsStr(lc.subject)}', '${escapeJsStr(lc.chapter)}', '${escapeJsStr(lc.teacher_name)}', '${escapeJsStr(url)}')" class="px-3 py-1.5 bg-amber-500 hover:bg-amber-600 text-white font-extrabold text-[11px] rounded-xl border-0 cursor-pointer transition-all inline-flex items-center gap-1 shadow-2xs">
                                    <i class="fas fa-edit"></i> Edit
                                </button>
                                <button type="button" onclick="deleteRecordedLecture(${lc.id}, '${escapeJsStr(lc.title)}')" class="px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white font-extrabold text-[11px] rounded-xl border-0 cursor-pointer transition-all inline-flex items-center gap-1 shadow-2xs">
                                    <i class="fas fa-trash-alt"></i> Delete
                                </button>
                            </div>
                        </td>
                    </tr>`;
                });
                linkContainer.innerHTML = lHtml;
            } else {
                linkContainer.innerHTML = `<tr><td colspan="8" class="p-8 text-center text-slate-400 text-xs"><i class="fab fa-youtube text-2xl mb-1 text-slate-300 block"></i><p class="font-bold text-slate-700">No stream links recorded yet</p><p class="text-[10px] text-slate-400">YouTube & external video links will appear here automatically.</p></td></tr>`;
            }
        })
        .catch(err => console.log('Realtime admin recorded lectures fetch error:', err));
};

// Global 5-second polling interval for Super Admin Recorded Lectures
if (!window.adminRealtimeRecordedInterval) {
    window.adminRealtimeRecordedInterval = setInterval(function() {
        if (window.AdminSPA && (window.AdminSPA.currentModule === 'study_material' || window.AdminSPA.currentModule === 'recorded_lectures')) {
            if (typeof window.loadAdminRealtimeRecordedLectures === 'function') {
                window.loadAdminRealtimeRecordedLectures();
            }
        }
    }, 5000);
}

function initStudyMaterialModule() {
    const form = document.getElementById('formAddStudyMaterial');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const fd = new FormData(form);
            const submitBtn = form.querySelector('button[type="submit"]');
            const origHTML = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
            submitBtn.disabled = true;

            fetch('/api/admin/study-materials/', {
                method: 'POST',
                body: fd,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(r => r.json())
            .then(resp => {
                submitBtn.innerHTML = origHTML;
                submitBtn.disabled = false;
                if (resp.status === 201) {
                    closeModal('modalAddStudyMaterial');
                    form.reset();
                    showToast(resp.message || 'Study Material uploaded!', 'success');
                    // Refresh module from real database
                    navTo('study_material');
                } else {
                    showToast(resp.message || 'Upload failed.', 'error');
                }
            })
            .catch(err => {
                submitBtn.innerHTML = origHTML;
                submitBtn.disabled = false;
                showToast('Network error. Please try again.', 'error');
            });
        });
    }
}

function filterStudyMaterials() {
    const q = (document.getElementById('smSearchInput')?.value || '').toLowerCase();
    const cls = document.getElementById('smClassFilter')?.value || '';
    const subj = document.getElementById('smSubjectFilter')?.value || '';
    const status = document.getElementById('smStatusFilter')?.value || '';

    // If any filter is active, fetch from real API
    if (q || cls || subj || status) {
        let params = new URLSearchParams();
        if (q) params.set('q', q);
        if (cls) params.set('class_name', cls);
        if (subj) params.set('subject', subj);
        if (status) params.set('status', status);

        fetch(`/api/admin/study-materials/?${params.toString()}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(r => r.json())
        .then(resp => {
            if (resp.status === 200 && resp.data && resp.data.materials) {
                renderSMTable(resp.data.materials);
            }
        })
        .catch(() => {});
    } else {
        // No filters — reload the full module from real DB
        navTo('study_material');
    }
}

function renderSMTable(materials) {
    const tbody = document.getElementById('smTableBody');
    if (!tbody) return;
    if (materials.length === 0) {
        tbody.innerHTML = `<tr><td colspan="10" class="p-8 text-center"><div class="text-slate-400 space-y-2"><i class="fas fa-folder-open text-3xl"></i><p class="font-bold text-sm">No content found</p><p class="text-[10px]">No study materials match your filters.</p></div></td></tr>`;
        return;
    }
    tbody.innerHTML = materials.map(m => {
        let statusBadge = '';
        if (m.status === 'Published') statusBadge = '<span class="bg-emerald-50 text-emerald-600 text-[9px] font-extrabold px-2 py-0.5 rounded-full">Published</span>';
        else if (m.status === 'Draft') statusBadge = '<span class="bg-amber-50 text-amber-600 text-[9px] font-extrabold px-2 py-0.5 rounded-full">Draft</span>';
        else statusBadge = '<span class="bg-red-50 text-red-600 text-[9px] font-extrabold px-2 py-0.5 rounded-full">Deleted</span>';

        let actions = '';
        if (m.status === 'Published') actions += `<button onclick="smAction(${m.id}, 'unpublish')" title="Unpublish" class="w-6 h-6 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-600 border-0 cursor-pointer text-[10px] flex items-center justify-center"><i class="fas fa-eye-slash"></i></button>`;
        if (m.status === 'Draft') actions += `<button onclick="smAction(${m.id}, 'publish')" title="Publish" class="w-6 h-6 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-600 border-0 cursor-pointer text-[10px] flex items-center justify-center"><i class="fas fa-check-circle"></i></button>`;
        if (m.status === 'Deleted') actions += `<button onclick="smAction(${m.id}, 'restore')" title="Restore" class="w-6 h-6 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-600 border-0 cursor-pointer text-[10px] flex items-center justify-center"><i class="fas fa-undo"></i></button>`;
        if (m.status !== 'Deleted') actions += `<button onclick="smDelete(${m.id})" title="Delete" class="w-6 h-6 rounded-lg bg-red-50 hover:bg-red-100 text-red-500 border-0 cursor-pointer text-[10px] flex items-center justify-center"><i class="fas fa-trash"></i></button>`;
        if (m.pdf_url) actions += `<a href="${m.pdf_url}" target="_blank" title="Download" class="w-6 h-6 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-600 no-underline text-[10px] flex items-center justify-center"><i class="fas fa-download"></i></a>`;

        return `<tr class="border-t border-slate-100 hover:bg-slate-50/50 transition-colors">
            <td class="p-3 font-mono text-[10px] text-slate-400">${m.material_id}</td>
            <td class="p-3 font-bold text-slate-800 max-w-[200px] truncate">${m.pdf_url ? `<a href="${m.pdf_url}" target="_blank" class="hover:text-indigo-600 no-underline text-slate-800">${m.title}</a>` : m.title}</td>
            <td class="p-3 text-slate-600">${m.class_name}</td>
            <td class="p-3 text-slate-600">${m.subject}</td>
            <td class="p-3 text-slate-500 max-w-[120px] truncate">${m.chapter}</td>
            <td class="p-3 text-slate-500">${m.file_size || '—'}</td>
            <td class="p-3">${statusBadge}</td>
            <td class="p-3 text-slate-500">${m.uploaded_by}</td>
            <td class="p-3 text-slate-400 text-[10px]">${m.created_at}</td>
            <td class="p-3"><div class="flex items-center gap-1.5">${actions}</div></td>
        </tr>`;
    }).join('');
}

function smAction(id, action) {
    fetch(`/api/admin/study-materials/?id=${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
        body: JSON.stringify({ action: action })
    })
    .then(r => r.json())
    .then(resp => {
        showToast(resp.message || 'Action completed.', resp.status === 200 ? 'success' : 'error');
        // Refresh from real database
        navTo('study_material');
    })
    .catch(() => showToast('Network error.', 'error'));
}

function smDelete(id) {
    if (!confirm('Are you sure you want to delete this study material?')) return;
    fetch(`/api/admin/study-materials/?id=${id}`, {
        method: 'DELETE',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(r => r.json())
    .then(resp => {
        showToast(resp.message || 'Deleted.', resp.status === 200 ? 'success' : 'error');
        // Refresh from real database
        navTo('study_material');
    })
    .catch(() => showToast('Network error.', 'error'));
}

// ==========================================
// USER LOGS MODULE — 100% REAL DATA
// ==========================================

function initUserLogsModule() {
    // Load chart + top users from real API
    fetch('/api/admin/user-logs/', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
    .then(r => r.json())
    .then(resp => {
        if (resp.status === 200 && resp.data) {
            renderULChart(resp.data.chart_data || []);
            renderULTopUsers(resp.data.top_users || []);
            // Update KPI cards from real API data
            const s = resp.data.stats || {};
            const kpiMap = {
                'kpiTotalActivities': s.total_activities,
                'kpiTodayActivities': s.today_activities,
                'kpiLogins': s.successful_logins,
                'kpiFailedLogins': s.failed_logins,
                'kpiActiveUsers': s.active_users,
                'kpiSecurityEvents': s.security_events,
            };
            for (const [id, val] of Object.entries(kpiMap)) {
                const el = document.getElementById(id);
                if (el) el.textContent = val ?? 0;
            }
        }
    })
    .catch(() => {
        const chart = document.getElementById('ulChartContainer');
        if (chart) chart.innerHTML = '<p class="text-xs text-slate-400 text-center py-8">Unable to load activity data. <button onclick="initUserLogsModule()" class="text-blue-600 font-bold border-0 bg-transparent cursor-pointer">Retry</button></p>';
        const top = document.getElementById('ulTopUsers');
        if (top) top.innerHTML = '<p class="text-xs text-slate-400 text-center py-4">Unable to load data. <button onclick="initUserLogsModule()" class="text-blue-600 font-bold border-0 bg-transparent cursor-pointer">Retry</button></p>';
    });
}

function renderULChart(chartData) {
    const canvas = document.getElementById('ulActivityChart');
    if (!canvas || typeof Chart === 'undefined') return;
    const note = document.getElementById('ulChartNote');
    const allZero = chartData.every(d => d.count === 0);
    if (allZero) {
        const container = document.getElementById('ulChartContainer');
        if (container) container.innerHTML = '<p class="text-xs text-slate-400 text-center py-16"><i class="fas fa-chart-line text-2xl mb-2 block"></i>No activity data available</p>';
        if (note) note.textContent = '';
        return;
    }
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: chartData.map(d => d.date),
            datasets: [{
                label: 'Activities',
                data: chartData.map(d => d.count),
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99,102,241,0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#6366f1',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1, font: { size: 10 } }, grid: { color: '#f1f5f9' } },
                x: { ticks: { font: { size: 9 } }, grid: { display: false } }
            }
        }
    });
}

function renderULTopUsers(topUsers) {
    const container = document.getElementById('ulTopUsers');
    if (!container) return;
    if (!topUsers || topUsers.length === 0) {
        container.innerHTML = '<div class="p-4 text-center text-slate-400 text-xs"><i class="fas fa-users text-2xl mb-1"></i><p class="font-bold">No active users to display</p></div>';
        return;
    }
    container.innerHTML = topUsers.map((u, i) => {
        const colors = ['text-amber-500', 'text-slate-400', 'text-orange-400', 'text-slate-500', 'text-slate-500'];
        const icons = ['fa-trophy', 'fa-medal', 'fa-medal', 'fa-user', 'fa-user'];
        return `<div class="flex items-center gap-3 p-2.5 rounded-xl bg-slate-50">
            <span class="w-7 h-7 rounded-lg bg-white flex items-center justify-center shrink-0 ${colors[i] || 'text-slate-400'} text-xs font-black"><i class="fas ${icons[i] || 'fa-user'}"></i></span>
            <div class="flex-1 min-w-0">
                <p class="font-bold text-slate-800 text-xs truncate">${u.user_name}</p>
                <p class="text-[9px] text-slate-400">${u.user_role || 'User'}</p>
            </div>
            <span class="text-xs font-black text-indigo-600">${u.total}</span>
        </div>`;
    }).join('');
}

let currentLogDateGroup = '';

function setLogDateFilter(group, btnEl) {
    currentLogDateGroup = group;
    document.querySelectorAll('.ul-date-tab').forEach(t => {
        t.className = 'ul-date-tab bg-slate-100 hover:bg-slate-200 text-slate-700 font-extrabold text-xs px-4 py-2 rounded-xl border-0 cursor-pointer flex items-center gap-2 transition-all';
    });
    if (btnEl) {
        btnEl.className = 'ul-date-tab active-tab bg-indigo-600 text-white font-extrabold text-xs px-4 py-2 rounded-xl border-0 cursor-pointer flex items-center gap-2 transition-all';
    }
    filterUserLogs();
}

function filterUserLogs() {
    const q = (document.getElementById('ulSearchInput')?.value || '').trim();
    const user = document.getElementById('ulUserFilter')?.value || '';
    const role = document.getElementById('ulRoleFilter')?.value || '';
    const type = document.getElementById('ulTypeFilter')?.value || '';

    if (q || user || role || type || currentLogDateGroup) {
        let params = new URLSearchParams();
        if (q) params.set('q', q);
        if (user) params.set('user_name', user);
        if (role) params.set('user_role', role);
        if (type) params.set('activity_type', type);
        if (currentLogDateGroup) params.set('date_group', currentLogDateGroup);

        fetch(`/api/admin/user-logs/?${params.toString()}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(r => r.json())
        .then(resp => {
            if (resp.status === 200 && resp.data && resp.data.logs) {
                renderULTable(resp.data.logs);
            }
        })
        .catch(() => {});
    } else {
        navTo('user_logs');
    }
}

function renderULTable(logs) {
    const tbody = document.getElementById('ulTableBody');
    if (!tbody) return;
    if (!logs || logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="p-8 text-center"><div class="text-slate-400 space-y-2"><i class="fas fa-inbox text-3xl"></i><p class="font-bold text-sm">No user activity recorded yet.</p><p class="text-[10px]">No logs match your selected date/search filters.</p></div></td></tr>';
        return;
    }

    const groups = { 'Today': [], 'Yesterday': [], 'Older': [] };
    logs.forEach(l => {
        const cat = l.date_group || 'Older';
        if (groups[cat]) groups[cat].push(l);
        else groups['Older'].push(l);
    });

    let html = '';
    const groupConfigs = [
        { key: 'Today', icon: 'fa-calendar-day', bg: 'bg-blue-50/70', text: 'text-blue-900', pillBg: 'bg-blue-600', label: '📌 TODAY\'S ACTIVITY LOGS' },
        { key: 'Yesterday', icon: 'fa-history', bg: 'bg-amber-50/70', text: 'text-amber-900', pillBg: 'bg-amber-600', label: '📅 YESTERDAY\'S ACTIVITY LOGS' },
        { key: 'Older', icon: 'fa-archive', bg: 'bg-slate-100', text: 'text-slate-700', pillBg: 'bg-slate-600', label: '📁 OLDER ACTIVITY LOGS' },
    ];

    groupConfigs.forEach(cfg => {
        const list = groups[cfg.key];
        if (list && list.length > 0) {
            html += `<tr class="${cfg.bg} ${cfg.text} font-extrabold text-[11px]">
                <td colspan="8" class="px-4 py-2">
                    <div class="flex items-center gap-2">
                        <i class="fas ${cfg.icon}"></i>
                        <span>${cfg.label}</span>
                        <span class="${cfg.pillBg} text-white text-[9px] font-black px-2 py-0.5 rounded-full">${list.length}</span>
                    </div>
                </td>
            </tr>`;

            list.forEach(l => {
                let roleBadge = '';
                if (l.user_role === 'Super Admin') roleBadge = '<span class="bg-purple-50 text-purple-600 text-[9px] font-extrabold px-2 py-0.5 rounded-full">Super Admin</span>';
                else if (l.user_role === 'Teacher') roleBadge = '<span class="bg-blue-50 text-blue-600 text-[9px] font-extrabold px-2 py-0.5 rounded-full">Teacher</span>';
                else if (l.user_role === 'Student') roleBadge = '<span class="bg-emerald-50 text-emerald-600 text-[9px] font-extrabold px-2 py-0.5 rounded-full">Student</span>';
                else roleBadge = `<span class="bg-slate-100 text-slate-500 text-[9px] font-extrabold px-2 py-0.5 rounded-full">${l.user_role}</span>`;

                html += `<tr class="border-t border-slate-100 hover:bg-slate-50/50 transition-colors">
                    <td class="p-3 text-slate-400 text-[10px] whitespace-nowrap">${l.created_at}</td>
                    <td class="p-3 font-bold text-slate-800 whitespace-nowrap">${l.user_name}</td>
                    <td class="p-3">${roleBadge}</td>
                    <td class="p-3 whitespace-nowrap"><span class="bg-indigo-50 text-indigo-600 text-[9px] font-extrabold px-2 py-0.5 rounded-full">${l.activity_type}</span></td>
                    <td class="p-3 text-slate-600 max-w-[250px] truncate">${l.description}</td>
                    <td class="p-3 text-slate-400 font-mono text-[10px]">${l.ip_address || '\u2014'}</td>
                    <td class="p-3 text-slate-400 text-[10px] max-w-[120px] truncate">${l.browser || '\u2014'}</td>
                    <td class="p-3 text-slate-400 text-[10px]">${l.device_type || '\u2014'}</td>
                </tr>`;
            });
        }
    });

    tbody.innerHTML = html;
}

function refreshUserLogs() {
    navTo('user_logs');
}

// ==========================================
// PAYMENTS & INVOICES MODULE — 100% REAL DATA
// ==========================================

let currentPaymentData = [];

function initPaymentsModule() {
    // Fetch stats, charts data, and top courses from real API
    fetch('/api/admin/payments/', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
    .then(r => r.json())
    .then(resp => {
        if (resp.status === 200 && resp.data) {
            currentPaymentData = resp.data.transactions || [];
            
            // Update KPI Card Badges
            const s = resp.data.stats || {};
            const kpiMap = {
                'kpiTotalRevenue': '₹' + (s.total_revenue || 0).toLocaleString(),
                'kpiTodayRevenue': '₹' + (s.today_revenue || 0).toLocaleString(),
                'kpiPendingAmount': '₹' + (s.pending_amount || 0).toLocaleString(),
                'kpiTotalTxns': s.total_transactions || 0,
                'kpiSuccessPayments': s.successful_count || 0,
                'kpiFailedPayments': s.failed_count || 0,
                'kpiRefundedAmount': '₹' + (s.refunded_amount || 0).toLocaleString(),
                'kpiDiscountsGiven': '₹' + (s.discounts_given || 0).toLocaleString(),
            };
            for (const [id, val] of Object.entries(kpiMap)) {
                const el = document.getElementById(id);
                if (el) el.textContent = val;
            }
            const pendCntEl = document.getElementById('kpiPendingCount');
            if (pendCntEl) pendCntEl.textContent = `(${s.pending_count || 0} pending)`;
            const succRateEl = document.getElementById('kpiSuccessRate');
            if (succRateEl) succRateEl.textContent = `${s.success_rate || 0}% rate`;
            const failRateEl = document.getElementById('kpiFailureRate');
            if (failRateEl) failRateEl.textContent = `${s.failure_rate || 0}% rate`;
            const refCountEl = document.getElementById('kpiRefundCount');
            if (refCountEl) refCountEl.textContent = `(${s.refund_count || 0} refunded)`;

            // Render Charts & Widgets
            renderPayRevenueChart(resp.data.revenue_trend || []);
            renderPayMethodChart(resp.data.method_dist || []);
            renderPayTopCourses(resp.data.top_courses || []);
        }
    })
    .catch(() => {});

    // Wire Create Invoice Form
    const form = document.getElementById('formCreateInvoice');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const submitBtn = form.querySelector('button[type="submit"]');
            const origHTML = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            submitBtn.disabled = true;

            const payload = {
                student_name: form.student_name.value,
                student_email: form.student_email.value,
                student_id_code: form.student_id_code.value,
                course_title: form.course_title.value,
                batch_title: form.batch_title.value,
                subtotal: form.subtotal.value,
                discount_amount: form.discount_amount.value,
                tax_amount: form.tax_amount.value,
                payment_method: form.payment_method.value,
                status: form.status.value,
                notes: form.notes.value,
            };

            fetch('/api/admin/payments/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
                body: JSON.stringify(payload)
            })
            .then(r => r.json())
            .then(resp => {
                submitBtn.innerHTML = origHTML;
                submitBtn.disabled = false;
                if (resp.status === 201) {
                    closeModal('modalCreateInvoice');
                    form.reset();
                    showToast(resp.message || 'Invoice generated successfully!', 'success');
                    navTo('payments');
                } else {
                    showToast(resp.message || 'Failed to generate invoice.', 'error');
                }
            })
            .catch(() => {
                submitBtn.innerHTML = origHTML;
                submitBtn.disabled = false;
                showToast('Network error. Please try again.', 'error');
            });
        });
    }
}

function calcInvoiceTotals() {
    const sub = parseFloat(document.getElementById('invSubtotal')?.value || 0);
    const disc = parseFloat(document.getElementById('invDiscount')?.value || 0);
    const tax = parseFloat(document.getElementById('invTax')?.value || 0);
    const finalVal = Math.max(0, sub - disc + tax);
    const badge = document.getElementById('invFinalTotalBadge');
    if (badge) badge.textContent = `₹${Math.round(finalVal).toLocaleString()}`;
}

function filterPayments() {
    const q = (document.getElementById('paySearchInput')?.value || '').trim();
    const status = document.getElementById('payStatusFilter')?.value || '';
    const method = document.getElementById('payMethodFilter')?.value || '';

    if (q || status || method) {
        let params = new URLSearchParams();
        if (q) params.set('q', q);
        if (status) params.set('status', status);
        if (method) params.set('payment_method', method);

        fetch(`/api/admin/payments/?${params.toString()}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(r => r.json())
        .then(resp => {
            if (resp.status === 200 && resp.data && resp.data.transactions) {
                currentPaymentData = resp.data.transactions;
                renderPayTable(resp.data.transactions);
            }
        })
        .catch(() => {});
    } else {
        navTo('payments');
    }
}

function resetPaymentFilters() {
    if (document.getElementById('paySearchInput')) document.getElementById('paySearchInput').value = '';
    if (document.getElementById('payStatusFilter')) document.getElementById('payStatusFilter').value = '';
    if (document.getElementById('payMethodFilter')) document.getElementById('payMethodFilter').value = '';
    navTo('payments');
}

function renderPayTable(txns) {
    const tbody = document.getElementById('payTableBody');
    if (!tbody) return;
    if (!txns || txns.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" class="p-8 text-center"><div class="text-slate-400 space-y-2"><i class="fas fa-receipt text-3xl"></i><p class="font-bold text-sm">No payment transactions found</p><p class="text-[10px]">No transactions match your search filters.</p></div></td></tr>`;
        return;
    }
    tbody.innerHTML = txns.map(p => {
        let statusBadge = '';
        if (p.status === 'Success') statusBadge = '<span class="bg-emerald-50 text-emerald-600 text-[9px] font-extrabold px-2 py-0.5 rounded-full">SUCCESS</span>';
        else if (p.status === 'Pending') statusBadge = '<span class="bg-amber-50 text-amber-600 text-[9px] font-extrabold px-2 py-0.5 rounded-full">PENDING</span>';
        else if (p.status === 'Failed') statusBadge = '<span class="bg-rose-50 text-rose-600 text-[9px] font-extrabold px-2 py-0.5 rounded-full">FAILED</span>';
        else statusBadge = `<span class="bg-purple-50 text-purple-600 text-[9px] font-extrabold px-2 py-0.5 rounded-full">${p.status.toUpperCase()}</span>`;

        return `<tr class="border-t border-slate-100 hover:bg-slate-50/50 transition-colors">
            <td class="p-3 font-mono text-[10px] font-bold text-slate-700">${p.transaction_id}</td>
            <td class="p-3 font-extrabold text-slate-900 max-w-[140px] truncate">${p.student_name} ${p.student_email ? `<span class="block text-[9px] font-normal text-slate-400 truncate">${p.student_email}</span>` : ''}</td>
            <td class="p-3 text-slate-600 max-w-[130px] truncate">${p.course_title}</td>
            <td class="p-3 font-black text-slate-900">₹${p.amount}</td>
            <td class="p-3"><span class="bg-slate-100 text-slate-700 text-[10px] font-bold px-2 py-0.5 rounded-lg">${p.payment_method}</span></td>
            <td class="p-3 text-slate-400 text-[10px] whitespace-nowrap">${p.created_at}</td>
            <td class="p-3">${statusBadge}</td>
            <td class="p-3 font-mono text-[10px] text-blue-600 font-bold">${p.invoice_number || '—'}</td>
            <td class="p-3">
                <div class="flex items-center gap-1.5">
                    <button onclick="viewPaymentDetail(${p.id})" title="View Details" class="w-6 h-6 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-600 border-0 cursor-pointer text-[10px] flex items-center justify-center"><i class="fas fa-eye"></i></button>
                    <button onclick="previewInvoice(${p.id})" title="Invoice Receipt" class="w-6 h-6 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-600 border-0 cursor-pointer text-[10px] flex items-center justify-center"><i class="fas fa-file-invoice"></i></button>
                    ${p.status === 'Pending' ? `<button onclick="markPaymentPaid(${p.id})" title="Mark Paid" class="w-6 h-6 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-600 border-0 cursor-pointer text-[10px] flex items-center justify-center"><i class="fas fa-check"></i></button>` : ''}
                </div>
            </td>
        </tr>`;
    }).join('');
}

function renderPayRevenueChart(trendData) {
    const canvas = document.getElementById('payRevenueChart');
    if (!canvas || typeof Chart === 'undefined') return;
    const container = document.getElementById('payRevenueChartContainer');
    const allZero = trendData.every(d => d.amount === 0);
    if (allZero) {
        if (container) container.innerHTML = '<p class="text-xs text-slate-400 text-center py-16"><i class="fas fa-chart-line text-2xl mb-2 block"></i>No revenue data available</p>';
        return;
    }
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: trendData.map(d => d.date),
            datasets: [{
                label: 'Revenue (₹)',
                data: trendData.map(d => d.amount),
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#2563eb'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { font: { size: 9 }, callback: v => '₹' + v }, grid: { color: '#f1f5f9' } },
                x: { ticks: { font: { size: 9 } }, grid: { display: false } }
            }
        }
    });
}

function renderPayMethodChart(methodDist) {
    const canvas = document.getElementById('payMethodChart');
    if (!canvas || typeof Chart === 'undefined') return;
    const container = document.getElementById('payMethodChartContainer');
    if (!methodDist || methodDist.length === 0) {
        if (container) container.innerHTML = '<p class="text-xs text-slate-400 text-center py-8"><i class="fas fa-chart-pie text-xl mb-1 block"></i>No payment data available</p>';
        return;
    }
    new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: methodDist.map(m => m.payment_method),
            datasets: [{
                data: methodDist.map(m => m.total),
                backgroundColor: ['#2563eb', '#10b981', '#8b5cf6', '#f59e0b', '#ef4444', '#64748b']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom', labels: { font: { size: 9 }, boxWidth: 10 } } }
        }
    });
}

function renderPayTopCourses(topCourses) {
    const container = document.getElementById('payTopCourses');
    if (!container) return;
    if (!topCourses || topCourses.length === 0) {
        container.innerHTML = '<div class="p-3 text-center text-slate-400 text-xs"><i class="fas fa-book text-xl mb-1 block"></i><p class="font-bold">No revenue data available</p></div>';
        return;
    }
    container.innerHTML = topCourses.map((c, i) => {
        const ranks = ['text-amber-500 bg-amber-50', 'text-slate-400 bg-slate-100', 'text-orange-400 bg-orange-50', 'text-slate-400 bg-slate-50', 'text-slate-400 bg-slate-50'];
        return `<div class="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 text-xs">
            <div class="flex items-center gap-2 min-w-0">
                <span class="w-5 h-5 rounded-md ${ranks[i] || 'bg-slate-100 text-slate-500'} font-black flex items-center justify-center text-[10px] shrink-0">#${i+1}</span>
                <span class="font-bold text-slate-800 truncate">${c.course_title}</span>
            </div>
            <span class="font-black text-emerald-600 shrink-0">₹${c.total_rev.toLocaleString()}</span>
        </div>`;
    }).join('');
}

function viewPaymentDetail(id) {
    fetch(`/api/admin/payments/?id=${id}`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
    .then(r => r.json())
    .then(resp => {
        if (resp.status === 200 && resp.data && resp.data.transactions) {
            const p = resp.data.transactions.find(t => t.id === id) || resp.data.transactions[0];
            if (!p) return;
            const drawer = document.getElementById('payDetailBody');
            if (drawer) {
                drawer.innerHTML = `
                    <div class="p-3 bg-slate-50 rounded-xl space-y-1">
                        <span class="text-[9px] font-extrabold uppercase text-slate-400 block">Transaction Reference</span>
                        <h4 class="font-mono text-sm font-black text-slate-900">${p.transaction_id}</h4>
                        <p class="text-[10px] text-slate-500 font-bold">Invoice: ${p.invoice_number}</p>
                    </div>
                    <div class="space-y-2">
                        <div class="flex justify-between border-b pb-1.5"><span class="text-slate-400">Student:</span><span class="font-bold text-slate-900">${p.student_name}</span></div>
                        <div class="flex justify-between border-b pb-1.5"><span class="text-slate-400">Email:</span><span class="font-bold text-slate-700">${p.student_email || 'Not available'}</span></div>
                        <div class="flex justify-between border-b pb-1.5"><span class="text-slate-400">Course:</span><span class="font-bold text-slate-800">${p.course_title}</span></div>
                        <div class="flex justify-between border-b pb-1.5"><span class="text-slate-400">Batch:</span><span class="font-bold text-slate-800">${p.batch_title || 'Regular'}</span></div>
                        <div class="flex justify-between border-b pb-1.5"><span class="text-slate-400">Payment Method:</span><span class="font-bold text-slate-800">${p.payment_method}</span></div>
                        <div class="flex justify-between border-b pb-1.5"><span class="text-slate-400">Gateway:</span><span class="font-bold text-slate-800">${p.gateway_name} (${p.gateway_txn_id || 'Direct'})</span></div>
                        <div class="flex justify-between border-b pb-1.5"><span class="text-slate-400">Subtotal:</span><span class="font-bold text-slate-700">₹${p.subtotal}</span></div>
                        <div class="flex justify-between border-b pb-1.5"><span class="text-slate-400">Discount:</span><span class="font-bold text-emerald-600">-₹${p.discount_amount}</span></div>
                        <div class="flex justify-between border-b pb-1.5"><span class="text-slate-400">Tax / GST:</span><span class="font-bold text-slate-700">+₹${p.tax_amount}</span></div>
                        <div class="flex justify-between border-b pb-1.5"><span class="text-slate-700 font-extrabold text-sm">Final Amount:</span><span class="font-black text-emerald-600 text-sm">₹${p.amount}</span></div>
                        <div class="flex justify-between border-b pb-1.5"><span class="text-slate-400">Status:</span><span class="font-black ${p.status === 'Success' ? 'text-emerald-600' : 'text-amber-600'}">${p.status}</span></div>
                        <div class="flex justify-between border-b pb-1.5"><span class="text-slate-400">Date:</span><span class="font-bold text-slate-700">${p.created_at}</span></div>
                    </div>
                `;
                openModal('modalPaymentDetail');
            }
        }
    });
}

function previewInvoice(id) {
    fetch(`/api/admin/payments/?id=${id}`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
    .then(r => r.json())
    .then(resp => {
        if (resp.status === 200 && resp.data && resp.data.transactions) {
            const p = resp.data.transactions.find(t => t.id === id) || resp.data.transactions[0];
            if (!p) return;
            const invNum = document.getElementById('invPreviewNumber');
            if (invNum) invNum.textContent = p.invoice_number;
            const invStat = document.getElementById('invPreviewStatus');
            if (invStat) {
                invStat.textContent = p.status.toUpperCase();
                invStat.className = p.status === 'Success' ? 'bg-emerald-100 text-emerald-700 text-xs font-black px-3 py-1 rounded-full uppercase' : 'bg-amber-100 text-amber-700 text-xs font-black px-3 py-1 rounded-full uppercase';
            }
            const body = document.getElementById('invPreviewBody');
            if (body) {
                body.innerHTML = `
                    <div class="grid grid-cols-2 gap-6 bg-slate-50 p-4 rounded-2xl">
                        <div>
                            <span class="text-[9px] font-extrabold uppercase text-slate-400 block">Billed To</span>
                            <h4 class="font-black text-slate-900 text-sm mt-0.5">${p.student_name}</h4>
                            <p class="text-slate-500 font-bold">${p.student_email || 'No email registered'}</p>
                            <p class="text-slate-400 font-mono">ID: ${p.student_id_code || 'STD-' + p.id}</p>
                        </div>
                        <div class="text-right">
                            <span class="text-[9px] font-extrabold uppercase text-slate-400 block">Payment Information</span>
                            <p class="font-bold text-slate-800 mt-0.5">${p.payment_method} (${p.gateway_name})</p>
                            <p class="font-mono text-slate-500">${p.transaction_id}</p>
                            <p class="text-slate-400">${p.created_at}</p>
                        </div>
                    </div>

                    <div class="border rounded-2xl overflow-hidden">
                        <table class="w-full">
                            <thead class="bg-slate-100 text-slate-600 font-extrabold text-[10px] uppercase">
                                <tr><th class="p-3 text-left">Course / Item</th><th class="p-3 text-right">Subtotal</th></tr>
                            </thead>
                            <tbody>
                                <tr class="border-t">
                                    <td class="p-3 font-bold text-slate-900">${p.course_title} <span class="block text-[10px] font-normal text-slate-400">${p.batch_title || 'Regular Batch'}</span></td>
                                    <td class="p-3 text-right font-bold text-slate-900">₹${p.subtotal || p.amount}</td>
                                </tr>
                                ${p.discount_amount > 0 ? `<tr class="border-t text-emerald-600"><td class="p-3 font-bold">Discount Applied</td><td class="p-3 text-right font-bold">-₹${p.discount_amount}</td></tr>` : ''}
                                ${p.tax_amount > 0 ? `<tr class="border-t text-slate-600"><td class="p-3 font-bold">Tax / GST</td><td class="p-3 text-right font-bold">+₹${p.tax_amount}</td></tr>` : ''}
                            </tbody>
                        </table>
                    </div>

                    <div class="flex justify-end">
                        <div class="w-48 space-y-1 text-right">
                            <div class="flex justify-between text-slate-500"><span class="font-bold">Total Net:</span><span class="font-black text-slate-900 text-base">₹${p.amount}</span></div>
                            <div class="flex justify-between text-emerald-600 font-bold"><span>Amount Paid:</span><span>₹${p.status === 'Success' ? p.amount : '0.00'}</span></div>
                        </div>
                    </div>
                `;
                openModal('modalInvoicePreview');
            }
        }
    });
}

function markPaymentPaid(id) {
    fetch(`/api/admin/payments/?id=${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
        body: JSON.stringify({ status: 'Success' })
    })
    .then(r => r.json())
    .then(resp => {
        showToast(resp.message || 'Payment marked as Paid.', 'success');
        navTo('payments');
    })
    .catch(() => showToast('Network error.', 'error'));
}

function exportPaymentsCSV() {
    if (!currentPaymentData || currentPaymentData.length === 0) {
        showToast('No payment transactions to export.', 'error');
        return;
    }
    let csv = 'Transaction ID,Invoice Number,Student Name,Email,Course,Amount,Payment Method,Gateway,Status,Date\n';
    currentPaymentData.forEach(p => {
        csv += `"${p.transaction_id}","${p.invoice_number}","${p.student_name}","${p.student_email}","${p.course_title}",${p.amount},"${p.payment_method}","${p.gateway_name}","${p.status}","${p.created_at}"\n`;
    });
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `edutrust_payments_export_${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
    showToast('Payment report exported successfully!', 'success');
}

// DOM Ready Initialization
document.addEventListener('DOMContentLoaded', function() {
    AdminSPA.init();
});



// =========================================================


// =========================================================
// SUPER ADMIN RECORDED LECTURES EDIT & DELETE ACTIONS
// =========================================================
window.escapeJsStr = function(str) {
    if (!str) return '';
    return String(str).replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '&quot;');
};

window.openEditRecordedLectureModal = function(id, title, className, subject, chapter, teacher, link) {
    const modal = document.getElementById('modalEditRecordedLecture');
    if (!modal) return;

    document.getElementById('editLectureId').value = id || '';
    document.getElementById('editLectureTitle').value = title || '';
    document.getElementById('editLectureClass').value = className || 'Class 10';
    document.getElementById('editLectureSubject').value = subject || '';
    document.getElementById('editLectureChapter').value = chapter || '';
    document.getElementById('editLectureTeacher').value = teacher || '';
    document.getElementById('editLectureLink').value = link || '';

    modal.classList.remove('hidden');
};

window.closeEditRecordedLectureModal = function() {
    const modal = document.getElementById('modalEditRecordedLecture');
    if (modal) modal.classList.add('hidden');
};

window.submitEditRecordedLectureForm = async function(event) {
    event.preventDefault();
    const id = document.getElementById('editLectureId').value;
    if (!id) return;

    const form = document.getElementById('formEditRecordedLecture');
    const formData = new FormData(form);
    formData.append('action', 'update');

    try {
        const res = await fetch('/api/admin/live-classes/' + id + '/action/', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        if (res.ok && data.status === 'success') {
            alert(data.message || 'Recorded lecture updated successfully!');
            closeEditRecordedLectureModal();
            if (typeof window.loadAdminRealtimeRecordedLectures === 'function') {
                window.loadAdminRealtimeRecordedLectures();
            }
        } else {
            alert(data.message || 'Error updating recorded lecture.');
        }
    } catch(err) {
        console.error('Error submitting edit lecture form:', err);
        alert('Network error while saving changes.');
    }
};

window.deleteRecordedLecture = async function(id, title) {
    const confirmMsg = 'Are you sure you want to delete "' + (title || 'this lecture') + '"?\n\nThis will permanently delete it from the database and remove it from student view everywhere.';
    if (!confirm(confirmMsg)) {
        return;
    }

    try {
        const res = await fetch('/api/admin/live-classes/' + id + '/action/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'permanent_delete' })
        });
        const data = await res.json();
        if (res.ok && data.status === 'success') {
            alert(data.message || 'Lecture deleted permanently from everywhere!');
            if (typeof window.loadAdminRealtimeRecordedLectures === 'function') {
                window.loadAdminRealtimeRecordedLectures();
            }
        } else {
            alert(data.message || 'Error deleting lecture.');
        }
    } catch(err) {
        console.error('Error deleting recorded lecture:', err);
        alert('Network error while deleting lecture.');
    }
};

/**
 * tutor_application_flow.js
 * Authoritative Tutor Job Application & Authentication Flow Engine.
 */

(function () {
    "use strict";

    // Helper: CSRF Token
    function getCsrfToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === 'csrftoken=') {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        if (!cookieValue) {
            const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
            if (csrfInput) cookieValue = csrfInput.value;
        }
        return cookieValue || '';
    }

    // Helper: Get Current Page Source
    function getSourcePage() {
        const path = window.location.pathname.toLowerCase();
        if (path.includes('latest')) {
            return 'Latest Tuition Job Page';
        }
        return 'Home Page';
    }

    // 1. Authoritative Apply Entry Point
    window.handleTutorApply = function (jobId, jobTitle) {
        if (!jobId || String(jobId).trim() === '' || String(jobId).includes('REQ-LIVE') || String(jobId).includes('UNKNOWN')) {
            alert('Unable to identify this tuition job. Please refresh and try again.');
            return;
        }

        const cleanJobId = String(jobId).trim();
        const cleanJobTitle = String(jobTitle || 'Tuition Job Requirement').trim();

        // Save pending intent in sessionStorage ONLY for temporary continuity
        sessionStorage.setItem('pendingJobId', cleanJobId);
        sessionStorage.setItem('pendingJobTitle', cleanJobTitle);
        sessionStorage.setItem('pendingApplicationIntent', 'true');

        // ALWAYS open Teacher Login Popup first! Never check database or bypass login modal!
        window.openTutorLoginModal();
    };

    // Alias for legacy templates
    window.applyForJobDirect = function (jobId, jobTitle) {
        window.handleTutorApply(jobId, jobTitle);
    };

    // 2. Open Login Modal
    window.openTutorLoginModal = function () {
        const modal = document.getElementById('tutorLoginModal');
        const card = document.getElementById('tutorLoginModalCard');
        const errDiv = document.getElementById('tutorLoginError');

        if (errDiv) {
            errDiv.classList.add('hidden');
            errDiv.innerHTML = '';
        }

        if (modal) {
            modal.classList.remove('hidden');
            modal.style.display = 'flex';
            setTimeout(() => {
                if (card) {
                    card.classList.remove('scale-95', 'opacity-0');
                    card.classList.add('scale-100', 'opacity-100');
                }
            }, 10);
        }
    };

    // Close Login Modal
    window.closeTutorLoginModal = function () {
        const modal = document.getElementById('tutorLoginModal');
        const card = document.getElementById('tutorLoginModalCard');
        if (card) {
            card.classList.remove('scale-100', 'opacity-100');
            card.classList.add('scale-95', 'opacity-0');
        }
        setTimeout(() => {
            if (modal) {
                modal.classList.add('hidden');
                modal.style.display = 'none';
            }
        }, 200);
    };

    // Toggle Password Visibility
    window.toggleTutorPasswordVisibility = function () {
        const pwdInput = document.getElementById('tutorLoginPassword');
        const icon = document.getElementById('tutorPasswordToggleIcon');
        if (pwdInput && icon) {
            if (pwdInput.type === 'password') {
                pwdInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                pwdInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        }
    };

    // 3. Submit Login Form Handler
    window.submitTutorLogin = function (event) {
        if (event) event.preventDefault();

        const emailInput = document.getElementById('tutorLoginEmail');
        const pwdInput = document.getElementById('tutorLoginPassword');
        const submitBtn = document.getElementById('tutorLoginSubmitBtn');
        const errDiv = document.getElementById('tutorLoginError');

        const identifier = emailInput ? emailInput.value.trim() : '';
        const password = pwdInput ? pwdInput.value.trim() : '';

        if (!identifier || !password) {
            if (errDiv) {
                errDiv.className = 'mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-bold text-center';
                errDiv.innerHTML = 'Please enter both Email/Mobile and Password.';
                errDiv.classList.remove('hidden');
            }
            return;
        }

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerText = 'Logging in...';
        }

        // STEP 1: Account Exists Check (POST /api/check-account/)
        fetch('/api/check-account/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ identifier: identifier })
        })
            .then(res => res.json())
            .then(chk => {
                if (!chk.exists) {
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.innerText = 'LOGIN';
                    }
                    if (errDiv) {
                        errDiv.className = 'mb-4 p-4 rounded-2xl bg-amber-50 border border-amber-200 text-amber-800 text-xs text-center font-medium';
                        errDiv.innerHTML = `
                            <div class="font-bold text-amber-900 text-sm mb-1">Account Not Registered</div>
                            <div class="mb-2">This email is not registered with EduTrust. Please register as a teacher first.</div>
                            <div>
                                <a href="/teacher-registration.html" class="inline-block px-3 py-1.5 bg-amber-600 text-white rounded-lg text-xs font-bold hover:bg-amber-700 transition-colors">Register as Teacher</a>
                            </div>
                        `;
                        errDiv.classList.remove('hidden');
                    }
                    return;
                }

                // STEP 2: Account Exists = YES -> POST /login/
                fetch('/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({ email: identifier, password: password })
                })
                    .then(res => res.json())
                    .then(loginRes => {
                        if (submitBtn) {
                            submitBtn.disabled = false;
                            submitBtn.innerText = 'LOGIN';
                        }

                        if (loginRes.status === 'success') {
                            window.closeTutorLoginModal();

                            // Restore pending job and submit application automatically ONLY AFTER SUCCESSFUL LOGIN
                            const pendingJobId = sessionStorage.getItem('pendingJobId');
                            const pendingJobTitle = sessionStorage.getItem('pendingJobTitle');

                            if (pendingJobId) {
                                window.submitJobApplication(pendingJobId, pendingJobTitle);
                            }
                        } else {
                            if (errDiv) {
                                errDiv.className = 'mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-bold text-center';
                                errDiv.innerHTML = loginRes.message || 'Invalid email or password. Please try again.';
                                errDiv.classList.remove('hidden');
                            }
                        }
                    })
                    .catch(err => {
                        if (submitBtn) {
                            submitBtn.disabled = false;
                            submitBtn.innerText = 'LOGIN';
                        }
                        if (errDiv) {
                            errDiv.className = 'mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-bold text-center';
                            errDiv.innerHTML = 'Login failed. Please check network and try again.';
                            errDiv.classList.remove('hidden');
                        }
                    });
            })
            .catch(err => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerText = 'LOGIN';
                }
                if (errDiv) {
                    errDiv.className = 'mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-bold text-center';
                    errDiv.innerHTML = 'Account check error. Please try again.';
                    errDiv.classList.remove('hidden');
                }
            });
    };

    // 4. Submit Job Application API Call (POST /api/jobs/apply/)
    window.submitJobApplication = function (jobId, jobTitle) {
        if (!jobId) {
            jobId = sessionStorage.getItem('pendingJobId');
            jobTitle = sessionStorage.getItem('pendingJobTitle');
        }

        if (!jobId) {
            alert('Unable to identify this tuition job. Please try again.');
            return;
        }

        const sourcePage = getSourcePage();

        // Update button visual state to processing
        const buttons = document.querySelectorAll(`[data-job-id="${jobId}"]`);
        buttons.forEach(btn => {
            btn.disabled = true;
            btn.dataset.originalText = btn.innerText;
            btn.innerText = 'Applying...';
        });

        fetch('/api/jobs/apply/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                job_id: String(jobId).trim(),
                job_title: String(jobTitle || 'Tuition Job Requirement').trim(),
                source_page: sourcePage
            })
        })
            .then(res => {
                if (res.status === 401) {
                    return { status: 'unauthenticated' };
                }
                return res.json();
            })
            .then(data => {
                // Always re-enable buttons so tutor can apply again
                buttons.forEach(btn => {
                    btn.disabled = false;
                    btn.innerText = btn.dataset.originalText || 'Apply';
                });

                if (data.status === 'success') {
                    // Show Application Success Popup
                    window.showSuccessPopup(data.application_id, data.job_title || jobTitle);

                    // Clear pending session storage after success
                    sessionStorage.removeItem('pendingJobId');
                    sessionStorage.removeItem('pendingJobTitle');
                    sessionStorage.removeItem('pendingApplicationIntent');

                } else if (data.status === 'already_applied') {
                    // Show Already Applied Popup ONLY AFTER SUCCESSFUL LOGIN AND DB CHECK
                    window.showAlreadyAppliedPopup(data.application_id, data.applied_at, data.current_status);

                    // Clear pending session storage after already applied
                    sessionStorage.removeItem('pendingJobId');
                    sessionStorage.removeItem('pendingJobTitle');
                    sessionStorage.removeItem('pendingApplicationIntent');

                } else if (data.status === 'unauthenticated') {
                    window.openTutorLoginModal();

                } else {
                    sessionStorage.removeItem('pendingJobId');
                    sessionStorage.removeItem('pendingJobTitle');
                    sessionStorage.removeItem('pendingApplicationIntent');
                    alert(data.message || 'Application submission failed.');
                }
            })
            .catch(err => {
                console.error('Error submitting application:', err);
                buttons.forEach(btn => {
                    btn.disabled = false;
                    btn.innerText = btn.dataset.originalText || 'Apply';
                });
                alert('Network error occurred while submitting application.');
            });
    };

    // 5. Success Popup Triggers
    window.showSuccessPopup = function (appId, jobTitle) {
        const popup = document.getElementById('jobAppSuccessPopup');
        const content = document.getElementById('successPopupContent');
        const appIdEl = document.getElementById('successAppId');

        if (appIdEl) {
            appIdEl.innerText = `Application ID: ${appId}`;
        }

        if (popup) {
            popup.classList.remove('hidden');
            popup.style.display = 'flex';
            setTimeout(() => {
                popup.classList.remove('opacity-0');
                if (content) {
                    content.classList.remove('scale-95');
                    content.classList.add('scale-100');
                }
            }, 10);
        }
    };

    window.closeSuccessPopup = function () {
        const popup = document.getElementById('jobAppSuccessPopup');
        const content = document.getElementById('successPopupContent');
        if (content) {
            content.classList.remove('scale-100');
            content.classList.add('scale-95');
        }
        if (popup) {
            popup.classList.add('opacity-0');
            setTimeout(() => {
                popup.classList.add('hidden');
                popup.style.display = 'none';
            }, 200);
        }
    };

    // 6. Already Applied Popup Triggers
    window.showAlreadyAppliedPopup = function (appId, dateStr, statusStr) {
        const modal = document.getElementById('alreadyAppliedModal');
        const appIdEl = document.getElementById('alreadyAppId');
        const dateEl = document.getElementById('alreadyAppDate');
        const statusEl = document.getElementById('alreadyAppStatus');

        if (appIdEl) appIdEl.innerText = appId || 'APP-XXXXXX';
        if (dateEl) dateEl.innerText = dateStr || 'N/A';
        if (statusEl) statusEl.innerText = statusStr || 'Applied';

        if (modal) {
            modal.classList.remove('hidden');
            modal.style.display = 'flex';
        }
    };

    window.closeAlreadyAppliedPopup = function () {
        const modal = document.getElementById('alreadyAppliedModal');
        if (modal) {
            modal.classList.add('hidden');
            modal.style.display = 'none';
        }
    };

    // 7. Update Buttons State (Keeps buttons enabled as 'Apply')
    window.updateJobButtonsState = function (jobId, stateText, appId) {
        const cleanId = String(jobId).trim();
        const selector = `button[data-job-id="${cleanId}"], button[onclick*="${cleanId}"]`;
        const buttons = document.querySelectorAll(selector);

        buttons.forEach(btn => {
            btn.disabled = false;
            if (btn.dataset.originalText) {
                btn.innerText = btn.dataset.originalText;
            }
        });
    };

    // 8. Page Load Initialization
    document.addEventListener('DOMContentLoaded', function () {
        // Page load MUST NEVER automatically trigger job applications or popups.
    });
})();

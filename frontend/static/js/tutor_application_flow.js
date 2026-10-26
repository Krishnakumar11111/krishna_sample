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
        const cleanJobId = String(jobId || '').trim();
        const cleanJobTitle = String(jobTitle || 'Tuition Job Requirement').trim();

        sessionStorage.setItem('pendingJobId', cleanJobId);
        sessionStorage.setItem('pendingJobTitle', cleanJobTitle);
        sessionStorage.setItem('pendingApplicationIntent', 'true');

        if (typeof window.openTutorLoginModal === 'function') {
            window.openTutorLoginModal(cleanJobId, cleanJobTitle);
        } else {
            const modal = document.getElementById('tutorLoginModal');
            const card = document.getElementById('tutorLoginModalCard');
            if (modal) {
                modal.classList.remove('hidden', 'opacity-0');
                modal.style.display = 'flex';
                if (card) {
                    card.classList.remove('scale-95', 'opacity-0');
                    card.classList.add('scale-100', 'opacity-100');
                }
            }
        }
    };

    // Alias for legacy templates
    window.applyForJobDirect = function (jobId, jobTitle) {
        window.handleTutorApply(jobId, jobTitle);
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
    window.copySuccessApplicationId = function(event) {
        if (event) event.stopPropagation();
        const appIdEl = document.getElementById('successAppIdDisplay') || document.getElementById('successAppId') || document.getElementById('tutorJobSuccessAppId');
        const btnText = document.getElementById('copyAppIdBtnText');
        const icon = document.getElementById('copyAppIdIcon');
        const textToCopy = appIdEl ? appIdEl.textContent.trim() : '';

        if (!textToCopy) return;

        const setCopiedState = () => {
            if (btnText) btnText.textContent = 'Copied!';
            if (icon) icon.className = 'fas fa-check text-emerald-600 text-sm';
            setTimeout(() => {
                if (btnText) btnText.textContent = 'Copy';
                if (icon) icon.className = 'far fa-copy text-sm group-hover:scale-110 transition-transform';
            }, 2000);
        };

        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(textToCopy).then(setCopiedState).catch(() => fallbackCopy(textToCopy));
        } else {
            fallbackCopy(textToCopy);
        }

        function fallbackCopy(text) {
            const temp = document.createElement('input');
            temp.value = text;
            document.body.appendChild(temp);
            temp.select();
            document.execCommand('copy');
            document.body.removeChild(temp);
            setCopiedState();
        }
    };

    window.showSuccessPopup = function (appId, jobTitle) {
        const popup = document.getElementById('jobAppSuccessPopup') || document.getElementById('tutorJobSuccessModal');
        const content = document.getElementById('successPopupContent') || document.getElementById('tutorJobSuccessCard');
        const appIdDisplay = document.getElementById('successAppIdDisplay');
        const appIdEl = document.getElementById('successAppId');
        const tutorAppIdEl = document.getElementById('tutorJobSuccessAppId');

        const cleanAppId = appId ? (String(appId).startsWith('APP-') ? appId : `APP-${appId}`) : 'APP-1001';
        if (appIdDisplay) appIdDisplay.textContent = cleanAppId;
        if (appIdEl) appIdEl.textContent = cleanAppId;
        if (tutorAppIdEl) tutorAppIdEl.textContent = cleanAppId;

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
        const popup = document.getElementById('jobAppSuccessPopup') || document.getElementById('tutorJobSuccessModal');
        const content = document.getElementById('successPopupContent') || document.getElementById('tutorJobSuccessCard');
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

/**
 * EduTrust Super Admin SPA Router & Navigation Controller
 * Single Authoritative Router Engine for Client Routing, Active State Management, and Module Lifecycle
 */

(function(window, document) {
    'use strict';

    // Global Admin Module Mapping Registry
    window.ADMIN_MODULES = window.ADMIN_MODULES || {
        'dashboard': '/admin/dashboard/',
        'students': '/admin/students/',
        'teachers': '/admin/teachers/',
        'student_parent_enquiries': '/admin/student-parent-enquiries/',
        'teacher_enquiries': '/admin/teacher-enquiries/',
        'demo_bookings': '/admin/demo-bookings/',
        'demo_enquiries': '/admin/demo-bookings/',
        'user_logs': '/admin/user-logs/',
        'profile_changes': '/admin/profile-changes/',
        'courses': '/admin/courses/',
        'subjects': '/admin/subjects/',
        'chapters': '/admin/chapters/',
        'live_classes': '/admin/live-classes/',
        'recorded_lectures': '/admin/study-material/',
        'study_material': '/admin/study-material/',
        'study_material/assignments': '/admin/study-material/assignments/',
        'study_material/dpp-practice': '/admin/study-material/dpp-practice/',
        'study_material/tests-quizzes': '/admin/study-material/tests-quizzes/',
        'study_material/test-series': '/admin/study-material/test-series/',
        'study_material/pyq-model-papers': '/admin/study-material/pyq-model-papers/',
        'study_material/e-library': '/admin/study-material/e-library/',
        'study_material/e-newspaper': '/admin/study-material/e-newspaper/',
        'notices': '/admin/notices/',
        'announcements': '/admin/announcements/',
        'notifications': '/admin/notifications/',
        'messages': '/admin/messages/',
        'payments': '/admin/payments/',
        'reports': '/admin/reports/',
        'location_analytics': '/admin/location-analytics/',
        'coupons_rewards': '/admin/coupons-rewards/',
        'coupons-rewards': '/admin/coupons-rewards/',
        'roles_permissions': '/admin/roles-permissions/',
        'settings': '/admin/settings/'
    };

    // State Tracking
    const moduleLoadPromises = {};
    let activeLoadingModule = null;
    let currentNavGeneration = 0;

    // Helper: Compute clean canonical URL path for history state
    function getCleanAdminModulePath(canonical) {
        if (!canonical || canonical === 'dashboard') return '/admin/';
        if (canonical === 'demo_enquiries') return '/admin/demo-bookings/';
        const slug = canonical.replace(/_/g, '-');
        return `/admin/${slug}/`;
    }
    window.getCleanAdminModulePath = getCleanAdminModulePath;

    // 1. Highlight Active Sidebar Navigation Item
    function highlightSidebar(moduleId) {
        let primaryModule = moduleId || 'dashboard';
        if (primaryModule.startsWith('reports/')) {
            primaryModule = 'reports';
        }
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('sidebar-active-item');
        });
        const activeNav = document.getElementById('nav-' + primaryModule);
        if (activeNav) {
            activeNav.classList.add('sidebar-active-item');
        }
        if (primaryModule === 'student_parent_enquiries' || primaryModule === 'teacher_enquiries' || primaryModule === 'demo_enquiries' || primaryModule === 'demo_bookings') {
            const menu = document.getElementById('enquiriesSubmenu') || document.getElementById('enquiryDropdownMenu');
            const chevron = document.getElementById('enquiriesChevron') || document.getElementById('enquiryChevron');
            if (menu) {
                menu.classList.remove('hidden');
                menu.style.display = 'block';
                menu.style.visibility = 'visible';
                menu.style.opacity = '1';
            }
            if (chevron) {
                chevron.style.transform = 'rotate(180deg)';
                chevron.classList.add('rotate-180');
            }
        }
    }
    window.highlightSidebar = highlightSidebar;

    // 2. Trigger Module Specific Initializer
    function triggerModuleInit(moduleName) {
        console.log('[MODULE INIT TRIGGERED]', moduleName);
        if (moduleName === 'dashboard' && typeof window.initDashboardCharts === 'function') {
            window.initDashboardCharts();
            if (typeof window.initDashboardRealtimeSystem === 'function') {
                window.initDashboardRealtimeSystem();
            }
        } else if (moduleName === 'settings' && typeof window.initSettingsModule === 'function') {
            window.initSettingsModule();
        } else if ((moduleName === 'courses' || moduleName === 'batches') && typeof window.initBatchControlCenter === 'function') {
            window.initBatchControlCenter();
        } else if ((moduleName === 'study_material' || moduleName === 'recorded_lectures') && typeof window.initStudyMaterialModule === 'function') {
            window.initStudyMaterialModule();
            if (typeof window.loadAdminRealtimeRecordedLectures === 'function') {
                window.loadAdminRealtimeRecordedLectures();
            }
        } else if (moduleName === 'user_logs' && typeof window.initUserLogsModule === 'function') {
            window.initUserLogsModule();
        } else if (moduleName === 'payments' && typeof window.initPaymentsModule === 'function') {
            window.initPaymentsModule();
        } else if (moduleName === 'teacher_enquiries') {
            if (typeof window.initTeacherEnquiries === 'function') {
                try { window.initTeacherEnquiries(); } catch (e) { console.error('[ADMIN MODULE INIT ERROR] teacher_enquiries:', e); }
            }
            if (typeof window.switchAdminTab === 'function') {
                window.switchAdminTab('teachers_enquiry');
            }
        } else if (moduleName === 'student_parent_enquiries') {
            if (typeof window.initStudentParentEnquiries === 'function') {
                try { window.initStudentParentEnquiries(); } catch (e) { console.error('[ADMIN MODULE INIT ERROR] student_parent_enquiries:', e); }
            }
        } else if (moduleName === 'messages' || moduleName === 'notices' || moduleName === 'announcements') {
            if (typeof window.initMessagesModule === 'function') window.initMessagesModule();
        } else if (moduleName === 'live_classes' || moduleName === 'live_class') {
            if (typeof window.initLiveClassesModule === 'function') window.initLiveClassesModule();
            else if (typeof window.initLiveClasses === 'function') window.initLiveClasses();
        } else if (moduleName === 'demo_bookings' || moduleName === 'demo_enquiries') {
            if (typeof window.initDemoBookings === 'function') window.initDemoBookings();
        }
    }
    window.triggerModuleInit = triggerModuleInit;

    // 3. Authoritative Module Loader (Single In-Flight Fetch & Safe Script Lifecycle)
    async function loadAdminModule(rawName, updateHistory = true) {
        const canonical = (rawName || 'dashboard').replace(/-/g, '_');

        // In-flight deduplication: Return existing active Promise for module
        if (moduleLoadPromises[canonical]) {
            console.log('[ADMIN MODULE IN-FLIGHT REUSE]', canonical);
            return moduleLoadPromises[canonical];
        }

        const mainContent = document.getElementById('main-content');
        if (!mainContent) return false;

        const currentActive = mainContent.getAttribute('data-active-module') || mainContent.dataset.activeModule;
        if (currentActive === canonical && !moduleLoadPromises[canonical]) {
            console.log('[ADMIN NAV] Module already active, skipping duplicate request:', canonical);
            highlightSidebar(canonical);
            return false;
        }

        const navGen = ++currentNavGeneration;
        activeLoadingModule = canonical;

        moduleLoadPromises[canonical] = (async () => {
            try {
                let endpoint = window.ADMIN_MODULES[rawName] || window.ADMIN_MODULES[canonical];
                if (!endpoint) {
                    if (rawName && rawName.startsWith('/admin/')) {
                        endpoint = rawName;
                    } else {
                        const slug = rawName.replace(/_/g, '-');
                        endpoint = `/admin/${slug}/`;
                    }
                }

                console.log('[ADMIN NAV]', rawName);
                console.log('[ADMIN MODULE REQUEST]', endpoint);

                const response = await fetch(endpoint, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                console.log('[ADMIN MODULE RESPONSE]', response.status);

                // Prevent stale response from overwriting newer navigation DOM state
                if (navGen !== currentNavGeneration) {
                    console.log('[ADMIN MODULE STALE ABORT]', rawName, 'Gen:', navGen, 'CurrentGen:', currentNavGeneration);
                    return false;
                }

                if (!response.ok) {
                    console.error('[ADMIN MODULE ERROR]', rawName, 'Status:', response.status);
                    let errMsg = "Server error while loading admin module.";
                    if (response.status === 404) errMsg = "Admin module not found.";
                    if (response.status === 403) errMsg = "You do not have permission to access this module.";

                    mainContent.innerHTML = `
                        <div class="bg-red-50 border border-red-200 text-red-700 p-6 rounded-2xl text-center my-8 max-w-xl mx-auto space-y-2">
                            <i class="fas fa-exclamation-triangle text-3xl text-red-500 mb-2"></i>
                            <h3 class="font-black text-base text-red-900">${errMsg}</h3>
                            <p class="text-xs text-red-600 font-mono">${endpoint} (${response.status})</p>
                        </div>
                    `;
                    return false;
                }

                const html = await response.text();

                if (updateHistory) {
                    const cleanPath = getCleanAdminModulePath(canonical);
                    if (window.location.pathname !== cleanPath) {
                        history.pushState(null, null, cleanPath);
                    }
                }

                highlightSidebar(canonical);

                mainContent.setAttribute('data-active-module', canonical);
                mainContent.removeAttribute('data-server-rendered');
                mainContent.innerHTML = html;
                mainContent.style.opacity = '1';

                // Safe Script Evaluation Lifecycle:
                // Isolates top-level let/const in IIFE closure to eliminate SyntaxError collisions upon module reload,
                // while auto-binding top-level declared functions onto window for inline onclick handlers.
                const scriptTags = mainContent.querySelectorAll('script');
                scriptTags.forEach(oldScript => {
                    try {
                        const src = oldScript.getAttribute('src') || '';
                        const type = oldScript.getAttribute('type') || '';
                        if (src && (src.includes('admin_spa.js') || src.includes('admin_router.js') || src.includes('tailwindcss') || src.includes('fontawesome') || src.includes('chart.js') || src.includes('bootstrap'))) {
                            return; // Skip shared base scripts
                        }
                        const newScript = document.createElement('script');
                        Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
                        if (oldScript.src) {
                            newScript.src = oldScript.src;
                        } else {
                            const code = oldScript.textContent || oldScript.innerHTML || '';
                            if (code && code.trim()) {
                                if (type.toLowerCase().includes('json')) {
                                    newScript.textContent = code;
                                } else {
                                    const funcMatches = code.matchAll(/(?:^|\n)\s*(?:async\s+)?function\s+([a-zA-Z0-9_]+)\s*\(/g);
                                    let exportStatements = '';
                                    const seenFns = new Set();
                                    for (const match of funcMatches) {
                                        const fnName = match[1];
                                        if (!seenFns.has(fnName)) {
                                            seenFns.add(fnName);
                                            exportStatements += `try { if (typeof ${fnName} === 'function') window.${fnName} = ${fnName}; } catch(e){}\n`;
                                        }
                                    }
                                    newScript.textContent = "/* [SAFE SPA MODULE SCRIPT EVALUATION] */\n(function() {\n" + code + "\n" + exportStatements + "\n})();";
                                }
                            }
                        }
                        if (oldScript.parentNode) {
                            oldScript.parentNode.replaceChild(newScript, oldScript);
                        }
                    } catch (scriptErr) {
                        console.warn('[ADMIN ROUTER] Dynamic script execution error caught safely:', scriptErr);
                    }
                });

                triggerModuleInit(canonical);
                console.log('[ADMIN MODULE LOADED]', rawName);
                return true;

            } catch (error) {
                console.error('[ADMIN MODULE ERROR]', rawName, error);
                mainContent.innerHTML = `
                    <div class="bg-amber-50 border border-amber-200 text-amber-800 p-6 rounded-2xl text-center my-8 max-w-xl mx-auto space-y-2">
                        <i class="fas fa-wifi text-3xl text-amber-500 mb-2"></i>
                        <h3 class="font-black text-base text-amber-900">Unable to connect to the server.</h3>
                        <p class="text-xs text-amber-700">Please check your network connection and try again.</p>
                    </div>
                `;
                return false;
            } finally {
                activeLoadingModule = null;
                delete moduleLoadPromises[canonical];
            }
        })();

        return moduleLoadPromises[canonical];
    }
    window.loadAdminModule = loadAdminModule;

    // 4. Authoritative Single Page Router Navigation function
    function navTo(moduleId, event) {
        const e = event || window.event;
        if (e) {
            if (typeof e.preventDefault === 'function') e.preventDefault();
            if (typeof e.stopPropagation === 'function') e.stopPropagation();
        }

        let primaryModule = moduleId || 'dashboard';
        if (primaryModule === 'recorded_lectures' || primaryModule === 'recorded-lectures') {
            primaryModule = 'study_material';
        }
        const canonical = primaryModule.replace(/-/g, '_');

        const mainContent = document.getElementById('main-content');
        const currentActive = mainContent ? (mainContent.getAttribute('data-active-module') || mainContent.dataset.activeModule) : '';
        if (currentActive === canonical && !moduleLoadPromises[canonical]) {
            console.log('[ADMIN NAV] Module already active, skipping duplicate request:', canonical);
            highlightSidebar(canonical);
            return false;
        }

        return loadAdminModule(primaryModule, true);
    }
    window.navTo = navTo;

    // 5. Authoritative Route & Hash Handler (Handles Initial Server Render Preservation + History Popstate)
    function handleRouteHash() {
        const mainContent = document.getElementById('main-content');
        if (!mainContent) return;

        const isServerRendered = mainContent.getAttribute('data-server-rendered') === 'true' || mainContent.dataset.serverRendered === 'true';
        const activeModule = mainContent.getAttribute('data-active-module') || mainContent.dataset.activeModule || 'dashboard';

        let targetHash = window.location.hash.replace('#', '').trim();
        if (!targetHash) {
            const path = window.location.pathname.replace(/\/$/, '');
            const segs = path.split('/').filter(Boolean);
            const adminIdx = segs.indexOf('admin');
            if (adminIdx !== -1 && segs.length > adminIdx + 1) {
                targetHash = segs[adminIdx + 1].replace(/-/g, '_');
            } else {
                targetHash = 'dashboard';
            }
        }
        if (targetHash === 'recorded_lectures' || targetHash === 'recorded-lectures') {
            targetHash = 'study_material';
        }

        if (isServerRendered && (activeModule === targetHash || (!window.location.hash && activeModule))) {
            console.log('[INITIAL LOAD] Preserving server-rendered module:', activeModule || targetHash);
            highlightSidebar(activeModule || targetHash);
            triggerModuleInit(activeModule || targetHash);
            return;
        }

        if (activeModule && activeModule === targetHash && !isServerRendered) {
            console.log('[ROUTE HASH] Module content already rendered:', targetHash);
            highlightSidebar(targetHash);
            triggerModuleInit(targetHash);
            return;
        }

        loadAdminModule(targetHash, false);
    }
    window.handleRouteHash = handleRouteHash;

    // 6. Single Idempotent Router Listener Initialization
    if (!window.ADMIN_ROUTER_INITIALIZED) {
        window.ADMIN_ROUTER_INITIALIZED = true;
        window.addEventListener('popstate', handleRouteHash);
        window.addEventListener('hashchange', handleRouteHash);

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', handleRouteHash);
        } else {
            handleRouteHash();
        }

        // Single Delegated Navigation Interceptor for Sidebar Links
        document.addEventListener('click', function(e) {
            const navLink = e.target.closest('.nav-item, [onclick*="navTo"]');
            if (navLink) {
                const onclickAttr = navLink.getAttribute('onclick') || '';
                if (onclickAttr.includes('navTo') || onclickAttr.includes('loadAdminModule')) {
                    // Executed directly by inline onclick; return to avoid duplicate execution
                    return;
                }
                const match = onclickAttr.match(/navTo\(['"]([^'"]+)['"]\)/);
                let targetModule = match ? match[1] : '';

                if (!targetModule) {
                    const href = navLink.getAttribute('href') || '';
                    if (href.includes('#')) {
                        targetModule = href.split('#')[1];
                    } else if (href.includes('/admin/')) {
                        const segs = href.split('/admin/')[1].split('/').filter(Boolean);
                        if (segs.length > 0) {
                            targetModule = segs[0].replace('-', '_');
                        }
                    }
                }

                if (targetModule && targetModule !== '#' && !targetModule.startsWith('http')) {
                    e.preventDefault();
                    e.stopPropagation();
                    navTo(targetModule, e);
                }
            }
        });
    }

})(window, document);

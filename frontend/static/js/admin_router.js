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
        'enquiries': '/admin/contact-enquiries/',
        'contact_enquiries': '/admin/contact-enquiries/',
        'student_parent_enquiries': '/admin/student-parent-enquiries/',
        'student_enquiries': '/admin/student-parent-enquiries/',
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
        'settings': '/admin/settings/',
        'backup_restore': '/admin/backup-restore/',
        'backup-restore': '/admin/backup-restore/'
    };

    // State Tracking
    const moduleLoadPromises = {};
    let activeLoadingModule = null;
    let currentNavGeneration = 0;

    // Top Navigation Progress Bar
    function showNavProgressBar() {
        let bar = document.getElementById('admin-nav-progress');
        if (!bar) {
            bar = document.createElement('div');
            bar.id = 'admin-nav-progress';
            bar.style.cssText = 'position:fixed;top:0;left:0;height:3px;background:linear-gradient(90deg,#2563eb,#7c3aed,#38bdf8);z-index:99999;transition:width 0.25s ease-out,opacity 0.3s ease-out;width:0%;pointer-events:none;box-shadow:0 0 10px rgba(37,99,235,0.7);';
            document.body.appendChild(bar);
        }
        bar.style.opacity = '1';
        bar.style.width = '35%';
        setTimeout(() => { if (bar && bar.style.opacity === '1') bar.style.width = '75%'; }, 150);
    }

    function finishNavProgressBar() {
        const bar = document.getElementById('admin-nav-progress');
        if (bar) {
            bar.style.width = '100%';
            setTimeout(() => {
                bar.style.opacity = '0';
                setTimeout(() => { bar.style.width = '0%'; }, 300);
            }, 200);
        }
    }

    // Helper: Compute clean canonical URL path for history state
    function getCleanAdminModulePath(canonical) {
        if (!canonical || canonical === 'dashboard') return '/admin/';
        if (canonical === 'enquiries' || canonical === 'contact_enquiries') return '/admin/contact-enquiries/';
        if (canonical === 'student_parent_enquiries' || canonical === 'student_enquiries') return '/admin/student-parent-enquiries/';
        if (canonical === 'teacher_enquiries') return '/admin/teacher-enquiries/';
        if (canonical === 'demo_enquiries' || canonical === 'demo_bookings') return '/admin/demo-bookings/';
        if (canonical === 'backup_restore' || canonical === 'backup-restore') return '/admin/backup-restore/';
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

        // Normalize for ID lookup: e.g. 'study_material/assignments' -> 'study_material_assignments'
        const cleanId = primaryModule.replace(/[\/-]/g, '_');
        let activeNavId = 'nav-' + cleanId;

        if (primaryModule === 'enquiries' || primaryModule === 'contact_enquiries') {
            activeNavId = 'nav-contact_enquiries';
        } else if (primaryModule === 'demo_bookings' || primaryModule === 'demo_enquiries') {
            activeNavId = 'nav-demo_bookings';
        } else if (primaryModule === 'student_enquiries') {
            activeNavId = 'nav-student_parent_enquiries';
        } else if (primaryModule === 'teacher_enquiries') {
            activeNavId = 'nav-teacher_enquiries';
        }

        let activeNav = document.getElementById(activeNavId) || 
                        document.getElementById('nav-' + primaryModule) ||
                        (primaryModule.includes('demo') ? document.getElementById('nav-demo_enquiries') : null);

        if (activeNav) {
            activeNav.classList.add('sidebar-active-item');
        }

        // Auto-expand Enquiries submenu if enquiry module selected
        if (['enquiries', 'contact_enquiries', 'student_parent_enquiries', 'student_enquiries', 'teacher_enquiries', 'demo_enquiries', 'demo_bookings'].includes(primaryModule)) {
            const menu = document.getElementById('enquiriesSubmenu') || document.getElementById('enquiryDropdownMenu');
            const chevron = document.getElementById('enquiriesChevron') || document.getElementById('enquiryChevron');
            if (menu) {
                menu.classList.remove('hidden');
                menu.style.display = 'block';
                if (chevron) {
                    chevron.style.transform = 'rotate(180deg)';
                    chevron.classList.add('rotate-180');
                }
            }
        }

        // Auto-expand Study Material dropdown if study material child selected
        if (primaryModule.includes('study_material') || ['assignments', 'dpp', 'dpp_practice', 'tests', 'tests_quizzes', 'test_series', 'pyq', 'pyq_model_papers', 'e_library', 'e_newspaper', 'recorded_lectures'].includes(primaryModule)) {
            const dd = document.getElementById('dropdown-study-material');
            const chevron = document.getElementById('chevron-study-material');
            if (dd) {
                dd.classList.remove('hidden');
                dd.style.display = 'block';
            }
            if (chevron) {
                chevron.classList.remove('fa-chevron-right');
                chevron.classList.add('fa-chevron-down');
            }
        }
    }
    window.highlightSidebar = highlightSidebar;

    window.toggleEnquiriesDropdown = window.toggleEnquiriesDropdown || function(e) {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
        }
        if (typeof saveSidebarScrollPosition === 'function') saveSidebarScrollPosition();
        const sub = document.getElementById('enquiriesSubmenu');
        const chev = document.getElementById('enquiriesChevron');
        if (sub) {
            const isHidden = sub.classList.contains('hidden') || sub.style.display === 'none' || window.getComputedStyle(sub).display === 'none';
            if (isHidden) {
                sub.classList.remove('hidden');
                sub.style.display = 'block';
                if (chev) chev.style.transform = 'rotate(180deg)';
                if (typeof saveOpenSubmenusState === 'function') saveOpenSubmenusState();
            } else {
                sub.classList.add('hidden');
                sub.style.display = 'none';
                if (chev) chev.style.transform = 'rotate(0deg)';
                if (typeof saveOpenSubmenusState === 'function') saveOpenSubmenusState();
            }
        }
    };

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
        } else if (moduleName === 'contact_enquiries' || moduleName === 'enquiries') {
            if (typeof window.initContactEnquiries === 'function') {
                try { window.initContactEnquiries(); } catch (e) { console.error('[ADMIN MODULE INIT ERROR] contact_enquiries:', e); }
            }
        } else if (moduleName === 'demo_bookings' || moduleName === 'demo_enquiries') {
            if (typeof window.initDemoBookings === 'function') window.initDemoBookings();
        }
    }
    window.triggerModuleInit = triggerModuleInit;

    // In-Memory Module Cache & Prefetcher (Instantaneous SPA Navigation)
    const moduleHtmlCache = new Map();
    const MODULE_CACHE_TTL = 3 * 60 * 1000; // 3 minutes

    function invalidateAdminModuleCache(moduleName) {
        if (!moduleName) {
            moduleHtmlCache.clear();
            return;
        }
        const clean = moduleName.replace(/[\/-]/g, '_');
        for (const key of moduleHtmlCache.keys()) {
            if (key === clean || key.startsWith(clean + '?')) {
                moduleHtmlCache.delete(key);
            }
        }
    }
    window.invalidateAdminModuleCache = invalidateAdminModuleCache;

    function renderModuleHtml(html, canonical, updateHistory, queryPart) {
        const mainContent = document.getElementById('main-content');
        if (!mainContent) return false;

        if (updateHistory) {
            let cleanPath = getCleanAdminModulePath(canonical);
            if (queryPart) {
                cleanPath += '?' + queryPart;
            }
            if (window.location.pathname + window.location.search !== cleanPath) {
                history.pushState(null, null, cleanPath);
            }
        }

        highlightSidebar(canonical);

        mainContent.setAttribute('data-active-module', canonical);
        mainContent.removeAttribute('data-server-rendered');
        mainContent.innerHTML = html;
        mainContent.style.opacity = '1';
        mainContent.style.pointerEvents = 'auto';
        mainContent.scrollTop = 0;

        // Safe Script Evaluation Lifecycle
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
        finishNavProgressBar();
        return true;
    }

    function resolveEndpoint(rawName) {
        const rawStr = String(rawName || 'dashboard').trim();
        const parts = rawStr.split('?');
        const pathPart = parts[0];
        const queryPart = parts.slice(1).join('?');

        let canonical = pathPart;
        if (canonical.startsWith('/admin/')) {
            canonical = canonical.replace(/^\/admin\//, '').replace(/\/$/, '');
        } else if (canonical.startsWith('/admin-module/')) {
            canonical = canonical.replace(/^\/admin-module\//, '').replace(/\/$/, '');
        }
        canonical = (canonical || 'dashboard').replace(/-/g, '_');
        if (canonical === 'demo_enquiries') canonical = 'demo_bookings';
        if (canonical === 'student_enquiries') canonical = 'student_parent_enquiries';
        if (canonical === 'recorded_lectures') canonical = 'study_material';

        let baseEndpoint = '';
        if (pathPart.startsWith('/admin/') || pathPart.startsWith('/admin-module/')) {
            baseEndpoint = pathPart.endsWith('/') ? pathPart : (pathPart + '/');
        } else {
            baseEndpoint = window.ADMIN_MODULES[pathPart] || window.ADMIN_MODULES[canonical];
            if (!baseEndpoint) {
                const slug = canonical.replace(/_/g, '-');
                baseEndpoint = `/admin/${slug}/`;
            }
        }
        const endpoint = baseEndpoint + (queryPart ? ('?' + queryPart) : '');
        const requestKey = canonical + (queryPart ? ('?' + queryPart) : '');
        return { canonical, endpoint, requestKey, queryPart, pathPart };
    }

    // Speculative Module Prefetcher on Hover / Touch
    function prefetchAdminModule(rawName) {
        if (!rawName) return;
        const { endpoint, requestKey } = resolveEndpoint(rawName);
        const cached = moduleHtmlCache.get(requestKey);
        if (cached && (Date.now() - cached.time < MODULE_CACHE_TTL)) return;
        if (moduleLoadPromises[requestKey]) return;

        fetch(endpoint, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            priority: 'low'
        }).then(res => {
            if (res.ok) return res.text();
            throw new Error('Not ok');
        }).then(html => {
            moduleHtmlCache.set(requestKey, { html, time: Date.now() });
        }).catch(() => {});
    }
    window.prefetchAdminModule = prefetchAdminModule;

    // 3. Authoritative Module Loader (Instant Cache First + Single In-Flight Fetch & Safe Script Lifecycle)
    async function loadAdminModule(rawName, updateHistory = true, forceReload = false) {
        const { canonical, endpoint, requestKey, queryPart } = resolveEndpoint(rawName);

        const mainContent = document.getElementById('main-content');
        if (!mainContent) return false;

        const currentActive = mainContent.getAttribute('data-active-module') || mainContent.dataset.activeModule;
        const currentSearch = (window.location.search || '').replace(/^\?/, '');

        // If module and query are identical and not forceReload, avoid redundant fetch
        if (!forceReload && currentActive === canonical && currentSearch === queryPart && !moduleLoadPromises[requestKey]) {
            highlightSidebar(canonical);
            return false;
        }

        // Instant Cache Hit: 0ms Switch!
        if (!forceReload) {
            const cached = moduleHtmlCache.get(requestKey);
            if (cached && (Date.now() - cached.time < MODULE_CACHE_TTL)) {
                console.log('[ADMIN MODULE INSTANT CACHE HIT]', requestKey);
                highlightSidebar(canonical);
                renderModuleHtml(cached.html, canonical, updateHistory, queryPart);
                return true;
            }
        }

        // In-flight deduplication: Return existing active Promise for module
        if (moduleLoadPromises[requestKey]) {
            console.log('[ADMIN MODULE IN-FLIGHT REUSE]', requestKey);
            return moduleLoadPromises[requestKey];
        }

        highlightSidebar(canonical);
        showNavProgressBar();
        mainContent.style.transition = 'opacity 0.1s ease';
        mainContent.style.opacity = '0.7';

        const navGen = ++currentNavGeneration;
        activeLoadingModule = canonical;

        moduleLoadPromises[requestKey] = (async () => {
            try {
                console.log('[ADMIN NAV]', rawName);
                console.log('[ADMIN MODULE REQUEST]', endpoint);

                const response = await fetch(endpoint, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                console.log('[ADMIN MODULE RESPONSE]', response.status);

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
                moduleHtmlCache.set(requestKey, { html, time: Date.now() });

                renderModuleHtml(html, canonical, updateHistory, queryPart);
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
                delete moduleLoadPromises[requestKey];
                finishNavProgressBar();
                if (mainContent) {
                    mainContent.style.opacity = '1';
                    mainContent.style.pointerEvents = 'auto';
                }
            }
        })();

        return moduleLoadPromises[requestKey];
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

        let targetPath = window.location.pathname;
        let targetSearch = window.location.search || '';
        let targetHash = window.location.hash.replace('#', '').trim();

        let targetModule = targetHash;
        if (!targetModule) {
            const segs = targetPath.replace(/\/$/, '').split('/').filter(Boolean);
            const adminIdx = segs.indexOf('admin');
            if (adminIdx !== -1 && segs.length > adminIdx + 1) {
                targetModule = segs[adminIdx + 1].replace(/-/g, '_');
            } else {
                targetModule = 'dashboard';
            }
        }
        if (targetModule === 'recorded_lectures' || targetModule === 'recorded-lectures') {
            targetModule = 'study_material';
        }

        if (isServerRendered && (activeModule === targetModule || (!window.location.hash && activeModule)) && !targetSearch) {
            console.log('[INITIAL LOAD] Preserving server-rendered module:', activeModule || targetModule);
            highlightSidebar(activeModule || targetModule);
            triggerModuleInit(activeModule || targetModule);
            return;
        }

        const fullTarget = targetPath + targetSearch;
        loadAdminModule(fullTarget, false, true);
    }
    window.handleRouteHash = handleRouteHash;

    // 6. Seamless In-Module Filtering & Form Submissions (No Full Page Refresh)
    // Override HTMLFormElement.prototype.submit for GET forms inside #main-content
    const origFormSubmit = HTMLFormElement.prototype.submit;
    HTMLFormElement.prototype.submit = function() {
        if (this.closest && this.closest('#main-content')) {
            const method = (this.getAttribute('method') || 'GET').toUpperCase();
            if (method === 'GET') {
                const action = this.getAttribute('action') || window.location.pathname;
                const formData = new FormData(this);
                const queryString = new URLSearchParams(formData).toString();
                const cleanAction = action.split('?')[0];
                const targetUrl = cleanAction + (queryString ? '?' + queryString : '');
                window.loadAdminModule(targetUrl, true, true);
                return;
            }
        }
        return origFormSubmit.apply(this, arguments);
    };

    // 7. Single Idempotent Router Listener Initialization
    if (!window.ADMIN_ROUTER_INITIALIZED) {
        window.ADMIN_ROUTER_INITIALIZED = true;
        window.addEventListener('popstate', handleRouteHash);
        window.addEventListener('hashchange', handleRouteHash);

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', handleRouteHash);
        } else {
            handleRouteHash();
        }

        // Delegated Filter & Search Form Submit Interceptor inside #main-content
        document.addEventListener('submit', function(e) {
            const form = e.target.closest('#main-content form');
            if (!form) return;
            const method = (form.getAttribute('method') || 'GET').toUpperCase();
            if (method === 'GET') {
                e.preventDefault();
                e.stopPropagation();
                const action = form.getAttribute('action') || window.location.pathname;
                const formData = new FormData(form);
                const queryString = new URLSearchParams(formData).toString();
                const cleanAction = action.split('?')[0];
                const targetUrl = cleanAction + (queryString ? '?' + queryString : '');
                loadAdminModule(targetUrl, true, true);
            }
        });

        // Delegated Dropdown & Filter Element Change Interceptor inside #main-content
        document.addEventListener('change', function(e) {
            const target = e.target;
            if (!target || !target.closest) return;
            const filterElem = target.closest('#main-content form select, #main-content form input[type="radio"], #main-content form input[type="checkbox"]');
            if (!filterElem || !filterElem.form) return;
            const form = filterElem.form;
            const method = (form.getAttribute('method') || 'GET').toUpperCase();
            if (method === 'GET') {
                e.preventDefault();
                e.stopPropagation();
                const action = form.getAttribute('action') || window.location.pathname;
                const formData = new FormData(form);
                const queryString = new URLSearchParams(formData).toString();
                const cleanAction = action.split('?')[0];
                const targetUrl = cleanAction + (queryString ? '?' + queryString : '');
                loadAdminModule(targetUrl, true, true);
            }
        });

        // Delegated Link Click Interceptor for In-Module Pagination, Reset Buttons & Navigation
        document.addEventListener('click', function(e) {
            // A. Sidebar Nav Items
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
                return;
            }

            // B. Links inside #main-content (Pagination, Reset, Table Detail views)
            const mainLink = e.target.closest('#main-content a');
            if (mainLink) {
                const href = mainLink.getAttribute('href');
                if (!href || href === '#' || href.startsWith('javascript:') || href.startsWith('blob:') || mainLink.hasAttribute('download') || mainLink.getAttribute('target') === '_blank' || mainLink.dataset.noSpa === 'true') {
                    return;
                }

                // If link has an inline onclick handler that is not navTo / loadAdminModule, let it run
                const onclickAttr = mainLink.getAttribute('onclick') || '';
                if (onclickAttr && !onclickAttr.includes('navTo') && !onclickAttr.includes('loadAdminModule')) {
                    return;
                }

                if (href.startsWith('?') || href.startsWith('/admin/') || href.startsWith('/admin-module/')) {
                    e.preventDefault();
                    e.stopPropagation();

                    let targetUrl = href;
                    if (href.startsWith('?')) {
                        targetUrl = window.location.pathname + href;
                    }
                    loadAdminModule(targetUrl, true, true);
                }
            }
        });

        // C. Hover & Touch Speculative Prefetching on Admin Sidebar Items
        function extractTargetModule(el) {
            if (!el) return '';
            const onclickAttr = el.getAttribute('onclick') || '';
            const match = onclickAttr.match(/navTo\(['"]([^'"]+)['"]\)/);
            if (match && match[1]) return match[1];
            if (el.id && el.id.startsWith('nav-')) return el.id.replace('nav-', '');
            if (el.dataset && el.dataset.module) return el.dataset.module;
            const href = el.getAttribute('href') || '';
            if (href.includes('/admin/')) {
                const segs = href.split('/admin/')[1].split('/').filter(Boolean);
                if (segs.length > 0) return segs[0].replace(/-/g, '_');
            }
            return '';
        }

        document.addEventListener('mouseover', function(e) {
            const navLink = e.target.closest('.nav-item, [onclick*="navTo"]');
            const targetMod = extractTargetModule(navLink);
            if (targetMod && targetMod !== 'dashboard') {
                prefetchAdminModule(targetMod);
            }
        }, { passive: true });

        document.addEventListener('touchstart', function(e) {
            const navLink = e.target.closest('.nav-item, [onclick*="navTo"]');
            const targetMod = extractTargetModule(navLink);
            if (targetMod && targetMod !== 'dashboard') {
                prefetchAdminModule(targetMod);
            }
        }, { passive: true });

        // D. Automatic Idle Prefetch for Top Admin Modules (0ms First Click)
        function prefetchKeyAdminModules() {
            const keyModules = [
                'students', 'teachers', 'courses', 'contact_enquiries',
                'student_parent_enquiries', 'teacher_enquiries', 'live_classes',
                'study_material', 'payments', 'notices', 'roles_permissions', 'settings'
            ];
            keyModules.forEach(mod => {
                try { prefetchAdminModule(mod); } catch(err) {}
            });
        }

        if ('requestIdleCallback' in window) {
            requestIdleCallback(prefetchKeyAdminModules, { timeout: 2500 });
        } else {
            setTimeout(prefetchKeyAdminModules, 1200);
        }
    }

})(window, document);


/**
 * EduTrust Super Admin SPA Router & Navigation Controller
 * Single Authoritative Router Engine for Client Routing, Active State Management, and Hash Navigation
 */

(function(window, document) {
    'use strict';

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
        if (primaryModule === 'student_parent_enquiries' || primaryModule === 'teacher_enquiries' || primaryModule === 'demo_enquiries') {
            const menu = document.getElementById('enquiryDropdownMenu');
            const chevron = document.getElementById('enquiryChevron');
            if (menu) {
                menu.classList.remove('hidden');
                menu.style.display = 'block';
                menu.style.visibility = 'visible';
                menu.style.opacity = '1';
            }
            if (chevron) chevron.classList.add('rotate-180');
        }
    }
    window.highlightSidebar = highlightSidebar;

    // 2. Authoritative Single Page Router function
    function navTo(moduleId) {
        console.log('[ADMIN NAV]', moduleId);

        let primaryModule = moduleId || 'dashboard';
        if (primaryModule === 'recorded_lectures' || primaryModule === 'recorded-lectures') {
            primaryModule = 'study_material';
        }

        // Delegate all module navigation to loadAdminModule to fetch real Django views
        if (typeof window.loadAdminModule === 'function') {
            return window.loadAdminModule(primaryModule, true);
        }

        let subRoute = '';
        if (primaryModule.startsWith('reports/')) {
            const parts = primaryModule.split('/');
            primaryModule = parts[0];
            subRoute = parts[1] || 'overview';
        } else if (primaryModule === 'reports') {
            primaryModule = 'reports';
            subRoute = 'overview';
        }

        const renderers = window.MODULE_RENDERERS || (typeof MODULE_RENDERERS !== 'undefined' ? MODULE_RENDERERS : null);

        if (!renderers || typeof renderers[primaryModule] !== 'function') {
            console.error('[ADMIN NAV ERROR] Missing renderer for module:', primaryModule);
            return false;
        }

        // Update URL Hash without full page reload
        const rawMod = primaryModule || moduleId || 'dashboard';
        const cleanPath = '/admin/' + rawMod.replace(/_/g, '-') + '/';
        if (window.location.hash || window.location.pathname !== cleanPath) {
            history.pushState(null, null, cleanPath);
        }

        // Highlight Active Sidebar Item & Keep Dropdown Open
        highlightSidebar(primaryModule);

        // Render Dynamic Module Content
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
            mainContent.setAttribute('data-active-module', primaryModule);
            mainContent.removeAttribute('data-server-rendered');
            mainContent.innerHTML = renderers[primaryModule](subRoute);

            // Re-evaluate embedded <script> tags so dynamically injected SPA modules execute JS
            const scriptTags = mainContent.querySelectorAll('script');
            scriptTags.forEach(oldScript => {
                const newScript = document.createElement('script');
                Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
                newScript.appendChild(document.createTextNode(oldScript.innerHTML));
                if (oldScript.parentNode) {
                    oldScript.parentNode.replaceChild(newScript, oldScript);
                }
            });
        }

        // Initialize Charts & Real-time System if Dashboard module loaded
        if (primaryModule === 'dashboard' && typeof window.initDashboardCharts === 'function') {
            window.initDashboardCharts();
            if (typeof window.initDashboardRealtimeSystem === 'function') {
                window.initDashboardRealtimeSystem();
            }
        }

        // Ensure Batch Control Center initializes immediately if courses module loaded
        if (primaryModule === 'courses' && typeof window.initBatchControlCenter === 'function') {
            window.initBatchControlCenter();
        }

        // Close mobile sidebar drawer if open
        if (typeof window.toggleSidebar === 'function') {
            window.toggleSidebar(false);
        }
    }
    window.navTo = navTo;

    // 3. Handle Browser Back / Forward / Hash Navigation (popstate & hashchange)
    function handleRouteHash() {
        const mainContent = document.getElementById('main-content');
        const isServerRendered = mainContent && mainContent.getAttribute('data-server-rendered') === 'true';
        const activeModule = mainContent ? (mainContent.getAttribute('data-active-module') || '') : '';
        const hash = window.location.hash.replace('#', '').trim();
        
        if (hash === 'demo_enquiries') {
            navTo('demo_enquiries');
            return;
        }

        if (isServerRendered && (activeModule === 'student_parent_enquiries' || activeModule === 'teacher_enquiries' || activeModule === 'courses' || activeModule === 'live_classes' || activeModule === 'study_material')) {
            if (!hash || hash === activeModule) {
                return;
            }
        }

        let targetHash = hash;
        if (!targetHash) {
            const path = window.location.pathname.replace(/\/$/, '');
            const segs = path.split('/');
            const lastSeg = segs[segs.length - 1];
            if (lastSeg && lastSeg !== 'admin' && lastSeg !== 'dashboard') {
                targetHash = lastSeg.replace('-', '_');
            } else {
                targetHash = 'dashboard';
            }
        }
        if (targetHash === 'recorded_lectures' || targetHash === 'recorded-lectures') {
            targetHash = 'study_material';
        }

        const renderers = window.MODULE_RENDERERS || (typeof MODULE_RENDERERS !== 'undefined' ? MODULE_RENDERERS : null);
        if (renderers && renderers[targetHash]) {
            navTo(targetHash);
        } else if (typeof window.loadAdminModule === 'function') {
            window.loadAdminModule(targetHash, false);
        }
    }

    if (!window.ADMIN_ROUTER_INITIALIZED) {
        window.ADMIN_ROUTER_INITIALIZED = true;
        window.addEventListener('popstate', handleRouteHash);
        window.addEventListener('hashchange', handleRouteHash);
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', handleRouteHash);
        } else {
            setTimeout(handleRouteHash, 10);
        }
    }

    // 4. Toggle Enquiry Dropdown Accordion Menu
    function toggleEnquiryDropdown(e) {
        if (e && e.preventDefault) e.preventDefault();
        if (e && e.stopPropagation) e.stopPropagation();

        const menu = document.getElementById('enquiryDropdownMenu');
        const chevron = document.getElementById('enquiryChevron');
        if (!menu) return false;

        const isCurrentlyHidden = menu.classList.contains('hidden') || menu.style.display === 'none';
        
        if (isCurrentlyHidden) {
            menu.classList.remove('hidden');
            menu.style.display = 'block';
            menu.style.visibility = 'visible';
            menu.style.opacity = '1';
            if (chevron) chevron.classList.add('rotate-180');
        } else {
            menu.classList.add('hidden');
            menu.style.display = 'none';
            if (chevron) chevron.classList.remove('rotate-180');
        }
        return false;
    }
    window.toggleEnquiryDropdown = toggleEnquiryDropdown;

    // 5. Explicitly Bind Click Listener to Button on Load
    function initEnquiryBtnListener() {
        const btn = document.getElementById('enquiryDropdownBtn');
        if (btn) {
            btn.onclick = toggleEnquiryDropdown;
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initEnquiryBtnListener);
    } else {
        initEnquiryBtnListener();
    }

    // 6. Diagnostic Click Event Logger for Enquiry Links
    document.addEventListener('click', function(e) {
        const link = e.target.closest('#nav-student_parent_enquiries, #nav-teacher_enquiries, #nav-demo_enquiries');
        if (link) {
            console.log('[ENQUIRY CLICK]', link.id, link.getAttribute('href'));
        }
    });

})(window, document);

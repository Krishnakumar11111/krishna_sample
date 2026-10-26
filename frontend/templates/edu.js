

//         //            Frequently ask questions    //

        function toggleFaq(button) {
        const faqItem = button.parentElement;
        const content = faqItem.querySelector('.faq-content');
        const icon = button.querySelector('.faq-icon');
        
        // Check if currently open
        const isOpen = content.style.maxHeight && content.style.maxHeight !== '0px';
        
        // Optional: Agar aap chahte hain ki baaki sabhi FAQs click karne par band ho jayein
        document.querySelectorAll('.faq-content').forEach(item => {
            item.style.maxHeight = '0px';
            item.style.paddingTop = '0px';
            item.style.paddingBottom = '0px';
        });
        document.querySelectorAll('.faq-icon').forEach(i => {
            i.style.transform = 'rotate(0deg)';
        });

        // Agar pehle se open nahi tha, toh isko khol dein
        if (!isOpen) {
            content.style.maxHeight = content.scrollHeight + 'px';
            content.style.paddingTop = '0.5rem';
            content.style.paddingBottom = '1.25rem'; // py-5 padding match karne ke liye
            if (icon) {
                icon.style.transform = 'rotate(180deg)';
            }
        }
    }
            


"use strict";

document.addEventListener("DOMContentLoaded", () => {
    try {
        initHomeMobileMenu();
        initHomeNavbarAndScroll();
        initHomeScrollReveal();
        initHomeStatsCounter();
    } catch (error) {
        console.error("Error initializing home.js:", error);
    }
});

// ==================================================
// MOBILE MENU TOGGLE (Home Specific Elements)
// ==================================================
const initHomeMobileMenu = () => {
    const mobileBtn = document.getElementById("mobile-menu-btn");
    const mobileMenu = document.getElementById("mobile-menu");

    if (!mobileBtn || !mobileMenu) return;

    mobileBtn.addEventListener("click", () => {
        mobileMenu.classList.toggle("hidden");
        const icon = mobileBtn.querySelector("i");
        if (!icon) return;

        if (mobileMenu.classList.contains("hidden")) {
            icon.classList.remove("fa-times");
            icon.classList.add("fa-bars");
        } else {
            icon.classList.remove("fa-bars");
            icon.classList.add("fa-times");
        }
    });
};

// ==================================================
// STICKY NAVBAR & BACK TO TOP BUTTON
// ==================================================
const initHomeNavbarAndScroll = () => {
    const navbar = document.getElementById("navbar");
    const backToTop = document.getElementById("backToTop");

    window.addEventListener("scroll", () => {
        if (backToTop) {
            if (window.scrollY > 500) {
                backToTop.classList.remove("opacity-0", "invisible");
                backToTop.classList.add("opacity-100", "visible");
            } else {
                backToTop.classList.add("opacity-0", "invisible");
                backToTop.classList.remove("opacity-100", "visible");
            }
        }
    });

    if (backToTop) {
        backToTop.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }
};

// ==================================================
// SCROLL REVEAL ANIMATIONS (Intersection Observer)
// ==================================================
const initHomeScrollReveal = () => {
    const revealElements = document.querySelectorAll(".reveal");
    if (revealElements.length === 0) return;

    const revealOptions = {
        threshold: 0.15,
        rootMargin: "0px 0px -50px 0px"
    };

    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            entry.target.classList.add("active");
            observer.unobserve(entry.target);
        });
    }, revealOptions);

    revealElements.forEach(el => revealObserver.observe(el));
};

// ==================================================
// STATISTICS COUNTER ANIMATION
// ==================================================
const initHomeStatsCounter = () => {
    const counters = document.querySelectorAll(".counter");
    const statsContainer = document.getElementById("stats-container");
    
    if (counters.length === 0 || !statsContainer) return;

    let hasCounted = false;

    const counterObserver = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && !hasCounted) {
            hasCounted = true;
            counters.forEach(counter => {
                const target = +counter.getAttribute("data-target");
                const duration = 2000; 
                const increment = target / (duration / 16); 

                let current = 0;
                const updateCounter = () => {
                    current += increment;
                    if (current < target) {
                        counter.innerText = Math.ceil(current);
                        requestAnimationFrame(updateCounter);
                    } else {
                        counter.innerText = target;
                    }
                };
                updateCounter();
            });
        }
    }, { threshold: 0.5 });

    counterObserver.observe(statsContainer);
};



document.addEventListener('DOMContentLoaded', function() {
    const citySelect = document.querySelector('select[name="city"]');

    function renderSidebars(selectedCity = '') {
        // --- Left Jobs Sidebar is exclusively managed by latestJobsSliderController in edutrust_tuition_platform.html ---


        // --- Right Teachers Sidebar (Fetched Live from Django Database) ---
        const teachersTrack = document.querySelector('#topTeachersSlider .slider-track');
        if (teachersTrack) {
            const url = selectedCity ? `/api/tutors/search/?city=${encodeURIComponent(selectedCity)}` : '/api/tutors/search/';
            fetch(url)
                .then(res => res.json())
                .then(data => {
                    const tutors = (data.status === 'success' && data.tutors) ? data.tutors : [];
                    if (tutors.length === 0) {
                        teachersTrack.innerHTML = `<div class="text-center py-12 text-gray-500 text-xs px-2">No verified teachers currently available in this location.</div>`;
                    } else {
                        const loopItems = tutors;
                        loopItems.forEach(tutor => {
                            const photo = tutor.photo_url || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=200';
                            const name = tutor.full_name || 'Verified Tutor';
                            const rating = tutor.rating || '5.0';
                            const subj = tutor.subjects || 'Expert Tutor';
                            const exp = tutor.experience || 'Experienced';
                            const loc = tutor.city || 'Location N/A';

                            html += `
                                <div class="bg-white border border-gray-100 rounded-2xl p-3.5 shadow-sm hover:border-brand-400 hover:shadow-md transition-all text-xs flex gap-3 items-center mb-3">
                                    <img src="${photo}" alt="${name}" class="w-12 h-12 rounded-xl object-cover border border-gray-200 flex-shrink-0">
                                    <div class="flex-1 min-w-0">
                                        <div class="flex justify-between items-center mb-0.5">
                                            <h4 class="font-extrabold text-gray-900 truncate text-xs mb-0">${name}</h4>
                                            <span class="text-[10px] font-bold text-amber-500 flex items-center gap-0.5"><i class="fas fa-star text-[9px]"></i> ${rating}</span>
                                        </div>
                                        <p class="text-brand-600 font-semibold text-[11px] truncate mb-1">${subj} &bull; ${exp}</p>
                                        <div class="flex justify-between items-center mt-1 pt-1.5 border-t border-gray-100">
                                            <span class="text-[10px] text-gray-500 font-medium"><i class="fas fa-map-marker-alt text-rose-500 mr-0.5"></i>${loc}</span>
                                            <div class="flex items-center gap-1.5">
                                                <a href="/book-demo/" class="bg-brand-600 hover:bg-brand-700 text-white px-2.5 py-1 rounded-lg text-[10px] font-bold text-decoration-none shadow-sm transition-all">Free Trial</a>
                                                <a href="/find-tutor/" class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-2 py-1 rounded-lg text-[10px] font-semibold text-decoration-none transition-all">Profile</a>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `;
                        });
                        teachersTrack.innerHTML = html;
                    }
                })
                .catch(err => {
                    console.error("Error fetching live DB tutors:", err);
                });
        }

        // --- Homepage Tutors Horizontal Grid (#tutorsGrid) ---
        const tutorsGrid = document.getElementById('tutorsGrid');
        if (tutorsGrid && !document.getElementById('tutorsCarouselWrapper')) {
            const url = selectedCity ? `/api/tutors/search/?city=${encodeURIComponent(selectedCity)}` : '/api/tutors/search/';
            fetch(url)
                .then(res => res.json())
                .then(data => {
                    const tutors = (data.status === 'success' && data.tutors) ? data.tutors : [];
                    if (tutors.length === 0) {
                        tutorsGrid.innerHTML = `<div class="w-full text-center py-12 text-gray-500 text-xs px-2">No verified teachers currently available in this location.</div>`;
                    } else {
                        let html = '';
                        tutors.forEach(tutor => {
                            const photo = tutor.photo_url || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=300';
                            const name = tutor.full_name || 'Verified Tutor';
                            const rating = tutor.rating || '5.0';
                            const subj = tutor.subjects || 'Expert Tutor';
                            const exp = tutor.experience || 'Experienced';
                            const loc = tutor.city || 'Location N/A';
                            const tutorClass = tutor.teaching_classes || 'Class 1-12';

                            html += `
                                <div class="bg-white border border-gray-100 rounded-3xl p-6 flex flex-col justify-between flex-shrink-0 w-[280px] sm:w-[320px] shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
                                    <div>
                                        <div class="flex items-start gap-4 mb-4">
                                            <img src="${photo}" alt="${name}" class="w-14 h-14 rounded-2xl object-cover shadow-md border-2 border-white flex-shrink-0">
                                            <div class="flex-1 min-w-0">
                                                <h3 class="font-extrabold text-sm text-gray-900 truncate mb-0.5">${name}</h3>
                                                <p class="text-xs text-brand-600 font-bold truncate mb-1">${subj}</p>
                                                <div class="flex items-center gap-1 text-xs font-bold text-amber-500"><i class="fas fa-star text-amber-500"></i> ${rating}</div>
                                            </div>
                                        </div>
                                        <div class="space-y-1.5 text-xs text-gray-600 mb-4 border-t border-gray-100 pt-3">
                                            <div class="flex items-center justify-between"><span class="text-gray-400">📚 Classes:</span><span class="font-bold text-brand-700 truncate max-w-[150px]">${tutorClass}</span></div>
                                            <div class="flex items-center justify-between"><span class="text-gray-400">💼 Experience:</span><span class="font-semibold text-gray-800">${exp}</span></div>
                                            <div class="flex items-center justify-between"><span class="text-gray-400">📍 Location:</span><span class="font-semibold text-gray-800 truncate max-w-[150px]">${loc}</span></div>
                                        </div>
                                    </div>
                                    <div class="flex items-center gap-2 pt-2 border-t border-gray-100">
                                        <a href="/book-demo/" class="flex-1 bg-brand-600 hover:bg-brand-700 text-white font-bold py-2 rounded-xl text-xs shadow-md transition-colors text-center text-decoration-none">Free Trial</a>
                                        <a href="/find-tutor/" class="bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold px-3 py-2 rounded-xl text-xs transition-colors text-center text-decoration-none">Profile</a>
                                    </div>
                                </div>
                            `;
                        });
                        tutorsGrid.innerHTML = html;
                    }
                })
                .catch(err => console.error("Error fetching tutorsGrid:", err));
        }
    }

    renderSidebars(citySelect ? citySelect.value : '');

    if (citySelect) {
        citySelect.addEventListener('change', function(e) {
            renderSidebars(e.target.value);
        });
    }

    // --- Enhanced Auto-Scroll & Manual Mouse Wheel Control ---
    function initInteractiveVerticalSlider(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        let isPaused = false;
        let scrollPos = container.scrollTop;

        // Ensure container allows manual scrolling via CSS
        container.style.overflowY = 'auto';

        container.addEventListener('mouseenter', () => { 
            isPaused = true; 
        });

        container.addEventListener('mouseleave', () => { 
            scrollPos = container.scrollTop;
            isPaused = false; 
        });

        container.addEventListener('scroll', () => {
            if (isPaused) {
                scrollPos = container.scrollTop;
            }
        });

        container.addEventListener('wheel', (e) => {
            e.preventDefault();
            isPaused = true;
            scrollPos += e.deltaY;
            if (scrollPos < 0) {
                scrollPos = 0;
            } else if (container.scrollHeight > container.clientHeight && scrollPos >= container.scrollHeight / 2) {
                scrollPos = 0;
            }
            container.scrollTop = scrollPos;
        }, { passive: false });

        function animateScroll() {
            if (!isPaused && container.scrollHeight > container.clientHeight) {
                scrollPos += 0.6;
                if (scrollPos >= container.scrollHeight / 2) {
                    scrollPos = 0;
                }
                container.scrollTop = scrollPos;
            }
            requestAnimationFrame(animateScroll);
        }
        requestAnimationFrame(animateScroll);
    }

    initInteractiveVerticalSlider('latestJobsSlider');
    initInteractiveVerticalSlider('latestJobSlider');
    initInteractiveVerticalSlider('topTeachersSlider');
});
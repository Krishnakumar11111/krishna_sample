/**
 * slider.js
 * Renders compact colorful animated cards with togglable checkboxes and custom modals for delete and clear all.
 */

document.addEventListener('DOMContentLoaded', function() {
    const grid = document.getElementById('tutorsGrid');
    const deleteSelectedBtn = document.getElementById('deleteSelectedBtn');
    const clearAllBtn = document.getElementById('clearAllBtn');
    
    // Modals & Buttons
    const deleteModal = document.getElementById('deleteModal');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    
    const clearAllModal = document.getElementById('clearAllModal');
    const cancelClearAllBtn = document.getElementById('cancelClearAllBtn');
    const confirmClearAllBtn = document.getElementById('confirmClearAllBtn');
    
    let isSelectingForDelete = false; // Track whether delete mode is active

    function renderTutors() {
        if (!grid) return;
        grid.innerHTML = ''; 
        const tutors = JSON.parse(localStorage.getItem('registeredTutors')) || [];

        if (tutors.length === 0) {
            grid.innerHTML = `
                <div class="w-full text-center py-16 bg-white/85 backdrop-blur rounded-3xl border border-dashed border-purple-200 shadow-lg" style="grid-column: 1 / -1;">
                    <div class="w-14 h-14 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-xl mx-auto mb-3 shadow-inner">
                        <i class="fas fa-users-slash"></i>
                    </div>
                    <h3 class="text-lg font-bold text-gray-800 mb-1">No Registered Tutors Yet</h3>
                    <p class="text-xs text-gray-500 mb-5">Abhi tak koi teacher register nahi hua hai, pehle register karein!</p>
                    <a href="/teacher_registration/" class="inline-block bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold text-xs px-6 py-3 rounded-xl shadow-lg shadow-purple-500/20 hover:scale-105 transition-all text-decoration-none">Register As Tutor</a>
                </div>
            `;
        } else {
            tutors.forEach((tutor, index) => {
                const name = tutor.name || 'Verified Tutor';
                const skill = tutor.skill || tutor.skills || 'Expert Tutor';
                const exp = tutor.exp || tutor.experience || '';
                const tutorClass = tutor.tutorClass || tutor.teachingClass || '';
                const location = tutor.location || tutor.address || '';
                const photo = tutor.photo || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=400';

                const gradients = [
                    'from-pink-500 to-rose-500',
                    'from-purple-500 to-indigo-500',
                    'from-blue-500 to-cyan-500',
                    'from-amber-500 to-orange-500'
                ];
                const badgeGradient = gradients[index % gradients.length];

                // Checkbox only visible if isSelectingForDelete is true
                const checkboxDisplay = isSelectingForDelete ? 'flex' : 'hidden';

                const cardHTML = `
                    <div class="min-w-[240px] max-w-[240px] flex-shrink-0 bg-white/95 backdrop-blur-md rounded-2xl shadow-lg border border-gray-100 overflow-hidden flex flex-col justify-between relative transform transition-all duration-300 hover:-translate-y-1.5 hover:shadow-xl">
                        
                        <!-- Dynamic Checkbox Container -->
                        <div class="absolute top-2.5 left-2.5 z-20 bg-white/95 backdrop-blur-md px-2 py-1 rounded-lg shadow-sm border border-gray-100 items-center gap-1.5 ${checkboxDisplay} delete-checkbox-wrapper">
                            <input type="checkbox" class="tutor-checkbox w-4 h-4 text-purple-600 rounded cursor-pointer accent-purple-600" data-index="${index}">
                            <span class="text-[10px] font-bold text-purple-700">Select</span>
                        </div>

                        <div>
                            <div class="relative h-40 overflow-hidden bg-gradient-to-tr from-gray-100 to-gray-200">
                                <img src="${photo}" alt="${name}" class="w-full h-full object-cover transition-transform duration-500 hover:scale-110">
                                <div class="absolute top-2.5 right-2.5 bg-gradient-to-r ${badgeGradient} text-white px-2.5 py-0.5 rounded-lg text-[10px] font-extrabold shadow-md tracking-wide uppercase">
                                    ⭐ Verified
                                </div>
                            </div>
                            <div class="p-3.5">
                                <h3 class="font-extrabold text-base text-gray-900 mb-0.5 truncate">${name}</h3>
                                <p class="text-[11px] font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2.5 truncate">${skill}</p>

                                <div class="space-y-1.5 text-[11px] text-gray-600 mb-2.5 bg-gray-50/90 p-2.5 rounded-xl border border-gray-100">
                                    <div class="flex justify-between font-medium"><span>Exp:</span> <strong class="text-gray-900">${exp}</strong></div>
                                    <div class="flex justify-between font-medium"><span>Class:</span> <strong class="text-gray-900">${tutorClass}</strong></div>
                                    <div class="flex justify-between font-medium"><span>City:</span> <strong class="text-gray-900 truncate max-w-[110px]">${location}</strong></div>
                                </div>
                            </div>
                        </div>
                        <div class="p-3.5 pt-0 flex gap-2">
                            <button onclick="window.location.href='/findtutor.html'" class="flex-1 bg-purple-50 text-purple-700 hover:bg-purple-100 py-2 rounded-xl font-bold text-[11px] border-0 cursor-pointer transition-colors shadow-sm">Profile</button>
                            <button onclick="applyForJobDirect('DEMO', 'Book Demo Request')" class="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:opacity-90 py-2 rounded-xl font-bold text-[11px] border-0 cursor-pointer transition-all shadow-md shadow-purple-500/20">Book Demo</button>
                        </div>
                    </div>
                `;
                grid.insertAdjacentHTML('beforeend', cardHTML);
            });
        }
    }

    // Initial render
    renderTutors();

    // Toggle Checkboxes On/Off on clicking "Delete Selected"
    if (deleteSelectedBtn) {
        deleteSelectedBtn.addEventListener('click', function() {
            if (!isSelectingForDelete) {
                isSelectingForDelete = true;
                renderTutors();
                deleteSelectedBtn.innerHTML = `<i class="fas fa-check mr-1.5"></i> Confirm Delete Selection`;
                deleteSelectedBtn.classList.remove('bg-red-50', 'text-red-600');
                deleteSelectedBtn.classList.add('bg-red-600', 'text-white');
            } else {
                const checkboxes = document.querySelectorAll('.tutor-checkbox:checked');
                
                if (checkboxes.length === 0) {
                    isSelectingForDelete = false;
                    renderTutors();
                    deleteSelectedBtn.innerHTML = `<i class="fas fa-trash-alt mr-1.5"></i> Delete Selected`;
                    deleteSelectedBtn.classList.remove('bg-red-600', 'text-white');
                    deleteSelectedBtn.classList.add('bg-red-50', 'text-red-600');
                    return;
                }

                deleteModal.classList.remove('hidden');
            }
        });
    }

    // Close Delete Modal on Cancel
    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', function() {
            deleteModal.classList.add('hidden');
            isSelectingForDelete = false;
            deleteSelectedBtn.innerHTML = `<i class="fas fa-trash-alt mr-1.5"></i> Delete Selected`;
            deleteSelectedBtn.classList.remove('bg-red-600', 'text-white');
            deleteSelectedBtn.classList.add('bg-red-50', 'text-red-600');
            renderTutors();
        });
    }

    // Confirm Deletion from Delete Modal
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function() {
            const checkboxes = document.querySelectorAll('.tutor-checkbox:checked');
            let tutors = JSON.parse(localStorage.getItem('registeredTutors')) || [];
            const indexesToDelete = Array.from(checkboxes).map(cb => parseInt(cb.getAttribute('data-index')));
            
            tutors = tutors.filter((_, index) => !indexesToDelete.includes(index));
            
            localStorage.setItem('registeredTutors', JSON.stringify(tutors));
            deleteModal.classList.add('hidden');
            
            isSelectingForDelete = false;
            deleteSelectedBtn.innerHTML = `<i class="fas fa-trash-alt mr-1.5"></i> Delete Selected`;
            deleteSelectedBtn.classList.remove('bg-red-600', 'text-white');
            deleteSelectedBtn.classList.add('bg-red-50', 'text-red-600');
            renderTutors();
        });
    }

    // Clear All Tutors Feature with Custom Modal
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', function() {
            const tutors = JSON.parse(localStorage.getItem('registeredTutors')) || [];
            if (tutors.length === 0) {
                alert('Pehle se hi koi data maujud nahi hai!');
                return;
            }
            clearAllModal.classList.remove('hidden');
        });
    }

    if (cancelClearAllBtn) {
        cancelClearAllBtn.addEventListener('click', function() {
            clearAllModal.classList.add('hidden');
        });
    }

    if (confirmClearAllBtn) {
        confirmClearAllBtn.addEventListener('click', function() {
            localStorage.removeItem('registeredTutors');
            clearAllModal.classList.add('hidden');
            isSelectingForDelete = false;
            deleteSelectedBtn.innerHTML = `<i class="fas fa-trash-alt mr-1.5"></i> Delete Selected`;
            deleteSelectedBtn.classList.remove('bg-red-600', 'text-white');
            deleteSelectedBtn.classList.add('bg-red-50', 'text-red-600');
            renderTutors();
        });
    }
});
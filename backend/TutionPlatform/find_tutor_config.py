import json
from django.db.models import Q
from .models import SystemSetting, AcademicSubject, TeacherProfile, StudentProfile

DEFAULT_FIND_TUTOR_CONFIG = {
    "enabled": True,
    "title": "Explore Verified Tutors",
    "subtitle": "Book expert home and online tutors tailored to your class and learning goals.",
    "search_placeholder": "City or Area...",
    "filters_enabled": True,
    "filters": [
        { "id": "location", "name": "Location", "label": "Location", "placeholder": "City or Area...", "enabled": True, "order": 1 },
        { "id": "gender", "name": "Gender", "label": "Gender", "placeholder": "Any", "enabled": True, "order": 2 },
        { "id": "class", "name": "Class / Grade", "label": "Class", "placeholder": "All Classes", "enabled": True, "order": 3 },
        { "id": "subject", "name": "Subject", "label": "Subject", "placeholder": "All Subjects", "enabled": True, "order": 4 },
        { "id": "experience", "name": "Experience", "label": "Exp", "placeholder": "Any Exp", "enabled": True, "order": 5 },
        { "id": "mode", "name": "Teaching Mode", "label": "Mode", "placeholder": "All Modes", "enabled": True, "order": 6 },
        { "id": "rating", "name": "Rating", "label": "Rating", "placeholder": "Any Rating", "enabled": True, "order": 7 }
    ],
    "popular_locations_enabled": True,
    "popular_locations": [
        { "id": "loc1", "name": "Lucknow", "icon": "fa-map-marker-alt", "link": "/find-tutor/?city=Lucknow", "enabled": True, "order": 1 },
        { "id": "loc2", "name": "Delhi", "icon": "fa-map-marker-alt", "link": "/find-tutor/?city=Delhi", "enabled": True, "order": 2 },
        { "id": "loc3", "name": "Mumbai", "icon": "fa-map-marker-alt", "link": "/find-tutor/?city=Mumbai", "enabled": True, "order": 3 },
        { "id": "loc4", "name": "Bangalore", "icon": "fa-map-marker-alt", "link": "/find-tutor/?city=Bangalore", "enabled": True, "order": 4 },
        { "id": "loc5", "name": "Kolkata", "icon": "fa-map-marker-alt", "link": "/find-tutor/?city=Kolkata", "enabled": True, "order": 5 },
        { "id": "loc6", "name": "Hyderabad", "icon": "fa-map-marker-alt", "link": "/find-tutor/?city=Hyderabad", "enabled": True, "order": 6 },
        { "id": "loc7", "name": "Noida", "icon": "fa-map-marker-alt", "link": "/find-tutor/?city=Noida", "enabled": True, "order": 7 },
        { "id": "loc8", "name": "Patna", "icon": "fa-map-marker-alt", "link": "/find-tutor/?city=Patna", "enabled": True, "order": 8 }
    ],
    "popular_subjects_enabled": True,
    "popular_subjects": [
        { "id": "subj1", "name": "Mathematics", "icon": "fa-calculator", "color": "blue", "desc": "Algebra, Calculus, Geo", "link": "/find-tutor/?subject=Mathematics", "enabled": True, "order": 1 },
        { "id": "subj2", "name": "Physics", "icon": "fa-atom", "color": "purple", "desc": "Mechanics, Optics", "link": "/find-tutor/?subject=Physics", "enabled": True, "order": 2 },
        { "id": "subj3", "name": "Chemistry", "icon": "fa-flask", "color": "cyan", "desc": "Organic, Inorganic", "link": "/find-tutor/?subject=Chemistry", "enabled": True, "order": 3 },
        { "id": "subj4", "name": "Biology", "icon": "fa-dna", "color": "green", "desc": "Botany, Zoology", "link": "/find-tutor/?subject=Biology", "enabled": True, "order": 4 },
        { "id": "subj5", "name": "English", "icon": "fa-book-open", "color": "red", "desc": "Grammar, Literature", "link": "/find-tutor/?subject=English", "enabled": True, "order": 5 },
        { "id": "subj6", "name": "Hindi", "icon": "fa-language", "color": "orange", "desc": "Vyakaran, Sahitya", "link": "/find-tutor/?subject=Hindi", "enabled": True, "order": 6 },
        { "id": "subj7", "name": "Computer Sci.", "icon": "fa-laptop-code", "color": "indigo", "desc": "Basics, Logic", "link": "/find-tutor/?subject=Computer Science", "enabled": True, "order": 7 },
        { "id": "subj8", "name": "Accounts", "icon": "fa-file-invoice-dollar", "color": "yellow", "desc": "Bookkeeping, Tally", "link": "/find-tutor/?subject=Accounts", "enabled": True, "order": 8 },
        { "id": "subj9", "name": "Economics", "icon": "fa-chart-line", "color": "teal", "desc": "Micro, Macro", "link": "/find-tutor/?subject=Economics", "enabled": True, "order": 9 },
        { "id": "subj10", "name": "Programming", "icon": "fa-code", "color": "pink", "desc": "Python, Java, C++", "link": "/find-tutor/?subject=Programming", "enabled": True, "order": 10 }
    ],
    "tutor_cards": {
        "enabled": True,
        "title": "Verified Tutors Directory",
        "subtitle": "Book expert home and online tutors tailored to your class and learning goals.",
        "count": 10,
        "carousel_enabled": True,
        "carousel_speed": 32,
        "show_profile_btn": True,
        "show_free_trial_btn": True,
        "show_rating": True,
        "show_experience": True,
        "show_fee": True,
        "show_location": True,
        "show_subjects": True,
        "show_class": True
    },
    "view_all_btn": {
        "enabled": True,
        "text": "Explore Tutors",
        "icon": "fa-arrow-right",
        "url": "/find-tutor/",
        "target": "_self"
    }
}


def get_find_tutor_config():
    """
    Load Find Tutor CMS configuration from SystemSetting database record.
    Falls back to default config if none exists.
    """
    try:
        obj = SystemSetting.objects.filter(category='homepage', key='hp_find_tutor').first()
        if obj and obj.value:
            loaded = json.loads(obj.value) if isinstance(obj.value, str) else obj.value
            if isinstance(loaded, dict):
                merged = json.loads(json.dumps(DEFAULT_FIND_TUTOR_CONFIG))
                # Merge top level keys
                for k, v in loaded.items():
                    if k in ['filters', 'popular_locations', 'popular_subjects']:
                        merged[k] = v
                    elif isinstance(v, dict) and isinstance(merged.get(k), dict):
                        merged[k].update(v)
                    else:
                        merged[k] = v
                return merged
    except Exception:
        pass
    return json.loads(json.dumps(DEFAULT_FIND_TUTOR_CONFIG))


def get_available_locations_and_subjects():
    """
    Extract existing distinct locations and subjects from the database
    to power Admin selection modals without creating duplicate records.
    """
    # Locations
    t_cities = list(TeacherProfile.objects.exclude(city='').values_list('city', flat=True).distinct())
    s_cities = list(StudentProfile.objects.exclude(city='').values_list('city', flat=True).distinct())
    all_locations = sorted(list(dict.fromkeys([c.strip() for c in (t_cities + s_cities) if c and c.strip()])))
    if not all_locations:
        all_locations = ['Lucknow', 'Delhi', 'Mumbai', 'Bangalore', 'Kolkata', 'Hyderabad', 'Noida', 'Patna', 'Pune', 'Jaipur']

    # Subjects
    acad_subjs = list(AcademicSubject.objects.values_list('name', flat=True).distinct())
    teacher_subjs_raw = list(TeacherProfile.objects.exclude(subjects='').values_list('subjects', flat=True).distinct())
    parsed_t_subjs = []
    for s_str in teacher_subjs_raw:
        if s_str:
            for s in s_str.replace(',', '\n').splitlines():
                clean_s = s.strip()
                if clean_s:
                    parsed_t_subjs.append(clean_s)
    all_subjects = sorted(list(dict.fromkeys([s for s in (acad_subjs + parsed_t_subjs) if s])))
    if not all_subjects:
        all_subjects = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'English', 'Hindi', 'Computer Science', 'Accounts', 'Economics']

    return {
        'locations': all_locations,
        'subjects': all_subjects
    }


CLASS_STREAM_SUBJECTS_MAP = {
    "Nursery": ["English", "Hindi", "Mathematics", "EVS", "GK", "Computer", "All Subjects", "Other"],
    "LKG": ["English", "Hindi", "Mathematics", "EVS", "GK", "Computer", "All Subjects", "Other"],
    "UKG": ["English", "Hindi", "Mathematics", "EVS", "GK", "Computer", "All Subjects", "Other"],
    "Class 1": ["Mathematics", "English", "Hindi", "EVS", "GK", "Computer", "All Subjects", "Other"],
    "Class 2": ["Mathematics", "English", "Hindi", "EVS", "GK", "Computer", "All Subjects", "Other"],
    "Class 3": ["Mathematics", "English", "Hindi", "EVS", "GK", "Computer", "All Subjects", "Other"],
    "Class 4": ["Mathematics", "English", "Hindi", "EVS", "GK", "Computer", "All Subjects", "Other"],
    "Class 5": ["Mathematics", "English", "Hindi", "EVS", "GK", "Computer", "All Subjects", "Other"],
    "Class 6": ["Mathematics", "Science", "English", "Hindi", "Social Science", "Computer", "Sanskrit", "Other"],
    "Class 7": ["Mathematics", "Science", "English", "Hindi", "Social Science", "Computer", "Sanskrit", "Other"],
    "Class 8": ["Mathematics", "Science", "English", "Hindi", "Social Science", "Computer", "Sanskrit", "Other"],
    "Class 9": ["Mathematics", "Science", "Physics", "Chemistry", "Biology", "English", "Hindi", "Social Science", "Computer", "Other"],
    "Class 10": ["Mathematics", "Science", "Physics", "Chemistry", "Biology", "English", "Hindi", "Social Science", "Computer", "Other"],
    "Class 11": {
        "Science": ["Physics", "Chemistry", "Mathematics", "Biology", "English", "Computer Science", "Physical Education", "Other"],
        "Commerce": ["Accountancy", "Business Studies", "Economics", "Mathematics", "English", "Entrepreneurship", "Computer Science", "Other"],
        "Arts / Humanities": ["History", "Political Science", "Geography", "Sociology", "Psychology", "Economics", "English", "Hindi", "Other"],
        "Arts": ["History", "Political Science", "Geography", "Sociology", "Psychology", "Economics", "English", "Hindi", "Other"],
        "all": ["Physics", "Chemistry", "Mathematics", "Biology", "Accountancy", "Business Studies", "Economics", "History", "Political Science", "Geography", "Sociology", "Psychology", "English", "Hindi", "Computer Science", "Physical Education", "Entrepreneurship", "Other"]
    },
    "Class 12": {
        "Science": ["Physics", "Chemistry", "Mathematics", "Biology", "English", "Computer Science", "Physical Education", "Other"],
        "Commerce": ["Accountancy", "Business Studies", "Economics", "Mathematics", "English", "Entrepreneurship", "Computer Science", "Other"],
        "Arts / Humanities": ["History", "Political Science", "Geography", "Sociology", "Psychology", "Economics", "English", "Hindi", "Other"],
        "Arts": ["History", "Political Science", "Geography", "Sociology", "Psychology", "Economics", "English", "Hindi", "Other"],
        "all": ["Physics", "Chemistry", "Mathematics", "Biology", "Accountancy", "Business Studies", "Economics", "History", "Political Science", "Geography", "Sociology", "Psychology", "English", "Hindi", "Computer Science", "Physical Education", "Entrepreneurship", "Other"]
    }
}


def get_find_tutor_template_context(request=None):
    """
    Build rich, ordered, and validated template context for findtutor.html
    respecting active website mode, teaching mode, and CMS settings.
    """
    cfg = get_find_tutor_config()
    
    # Sort popular locations by 'order'
    raw_locs = cfg.get('popular_locations', [])
    sorted_locs = sorted(raw_locs, key=lambda x: x.get('order', 999))
    active_locs = [l for l in sorted_locs if l.get('enabled') is not False]

    # Sort popular subjects by 'order'
    raw_subjs = cfg.get('popular_subjects', [])
    sorted_subjs = sorted(raw_subjs, key=lambda x: x.get('order', 999))
    active_subjs = [s for s in sorted_subjs if s.get('enabled') is not False]

    # Sort filters by 'order'
    raw_filters = cfg.get('filters', [])
    sorted_filters = sorted(raw_filters, key=lambda x: x.get('order', 999))
    
    # Fast filter lookup dict
    filters_map = {f.get('id'): f for f in sorted_filters}

    # Find Tutor Page Cards configuration (strictly for /find-tutor/)
    from .why_choose_config import get_find_tutor_cards_config
    find_tutor_cards_cfg = get_find_tutor_cards_config()

    # Website mode context
    from .website_mode import get_website_mode
    active_mode = get_website_mode()

    return {
        'find_tutor_config': cfg,
        'find_tutor_cards': find_tutor_cards_cfg,
        'why_choose': find_tutor_cards_cfg,
        'popular_locations': active_locs,
        'popular_subjects': active_subjs,
        'ordered_filters': sorted_filters,
        'filters_map': filters_map,
        'filters_enabled': cfg.get('filters_enabled', True),
        'popular_locations_enabled': cfg.get('popular_locations_enabled', True),
        'popular_subjects_enabled': cfg.get('popular_subjects_enabled', True),
        'is_home_tuition_mode': active_mode == 'home_tuition',
        'is_online_tuition_mode': active_mode == 'online_tuition',
        'is_full_lms_mode': active_mode == 'full_lms',
        'website_mode': active_mode,
        'class_subjects_map': CLASS_STREAM_SUBJECTS_MAP,
    }


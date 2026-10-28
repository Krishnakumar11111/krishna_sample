import json
import time
from .models import SystemSetting

_FIND_TUTOR_CARDS_CACHE = None
_FIND_TUTOR_CARDS_CACHE_TIME = 0

_WHY_CHOOSE_CACHE = None
_WHY_CHOOSE_CACHE_TIME = 0

DEFAULT_WHY_CHOOSE_CONFIG = {
    "enabled": True,
    "badge": "Why Choose EduTrust",
    "title": "Why Students Choose EduTrust",
    "subtitle": "Custom verified academic learning environment for students across India.",
    "features_enabled": True,
    "features": [
        {
            "id": "verified_tutors",
            "title": "Verified Tutors",
            "icon": "fa-user-check",
            "color": "blue",
            "desc": "Every tutor completes identity, qualification, and background verification before joining EduTrust, helping students connect with trusted educators.",
            "enabled": True,
            "order": 1
        },
        {
            "id": "home_tuition_option",
            "title": "Home Tuition Option",
            "icon": "fa-home",
            "color": "purple",
            "desc": "Get trusted tutors for personalized one-to-one learning at your home, with flexible schedules designed around your learning needs.",
            "enabled": True,
            "order": 2
        },
        {
            "id": "affordable_fees",
            "title": "Affordable Fees",
            "icon": "fa-wallet",
            "color": "orange",
            "desc": "Choose flexible pricing, monthly plans, and pay-per-class options designed to make quality tutoring accessible for every family.",
            "enabled": True,
            "order": 3
        },
        {
            "id": "progress_tracking",
            "title": "Progress Tracking",
            "icon": "fa-chart-line",
            "color": "pink",
            "desc": "Monitor attendance, test performance, monthly reports, and academic improvement so students and parents can clearly track learning progress.",
            "enabled": True,
            "order": 4
        },
        {
            "id": "support_24x7",
            "title": "24x7 Support",
            "icon": "fa-headset",
            "color": "green",
            "desc": "Get dedicated student support and academic guidance whenever you need assistance throughout your learning journey.",
            "enabled": True,
            "order": 5
        },
        {
            "id": "flexible_learning",
            "title": "Flexible Learning",
            "icon": "fa-laptop-code",
            "color": "indigo",
            "desc": "Choose between home tuition, online classes, or hybrid learning based on your schedule, location, and preferred learning style.",
            "enabled": True,
            "order": 6
        }
    ],
    "why_choose_tutors": {
        "enabled": True,
        "title": "Why Choose EduTrust Tutors?",
        "icon": "fa-award",
        "features": [
            "Verified & Background Checked",
            "Experienced Subject Experts",
            "Affordable Tuition Plans"
        ],
        "cta_text": "Explore Tutors",
        "cta_link": "/find-tutor/"
    },
    "help_banner": {
        "enabled": True,
        "title": "Need Help Finding the Right Tutor?",
        "desc": "Talk to our expert academic advisors for personalized tutor recommendations.",
        "cta_text": "Request Callback",
        "cta_link": "/hire/",
        "icon": "fa-phone-volume"
    },
    "faster_banner": {
        "enabled": True,
        "title": "Find Your Perfect Tutor Faster",
        "desc": "Post your learning requirement in 2 minutes and get calls from top verified tutors.",
        "cta_text": "Post Requirement",
        "cta_link": "/hire/",
        "icon": "fa-bolt"
    },
    "explore_subjects": {
        "enabled": True,
        "badge": "Explore Popular Subjects",
        "badge_icon": "fa-book-open",
        "title": "Explore Popular Subjects",
        "subtitle": "Find expert tutors for any subject, ensuring comprehensive understanding and top grades.",
        "subjects": [
            {
                "id": "subj_1",
                "name": "Mathematics",
                "description": "Algebra, Calculus, Geo",
                "icon": "fa-calculator",
                "color": "blue",
                "enabled": True,
                "display_order": 1
            },
            {
                "id": "subj_2",
                "name": "Physics",
                "description": "Mechanics, Optics",
                "icon": "fa-atom",
                "color": "purple",
                "enabled": True,
                "display_order": 2
            },
            {
                "id": "subj_3",
                "name": "Chemistry",
                "description": "Organic, Inorganic",
                "icon": "fa-flask",
                "color": "cyan",
                "enabled": True,
                "display_order": 3
            },
            {
                "id": "subj_4",
                "name": "Biology",
                "description": "Botany, Zoology",
                "icon": "fa-dna",
                "color": "green",
                "enabled": True,
                "display_order": 4
            },
            {
                "id": "subj_5",
                "name": "English",
                "description": "Grammar, Literature",
                "icon": "fa-book-open",
                "color": "red",
                "enabled": True,
                "display_order": 5
            },
            {
                "id": "subj_6",
                "name": "Hindi",
                "description": "Vyakaran, Sahitya",
                "icon": "fa-language",
                "color": "orange",
                "enabled": True,
                "display_order": 6
            },
            {
                "id": "subj_7",
                "name": "Computer Sci.",
                "description": "Basics, Logic",
                "icon": "fa-laptop-code",
                "color": "indigo",
                "enabled": True,
                "display_order": 7
            },
            {
                "id": "subj_8",
                "name": "Accounts",
                "description": "Bookkeeping, Tally",
                "icon": "fa-file-invoice-dollar",
                "color": "yellow",
                "enabled": True,
                "display_order": 8
            },
            {
                "id": "subj_9",
                "name": "Economics",
                "description": "Micro, Macro",
                "icon": "fa-chart-line",
                "color": "teal",
                "enabled": True,
                "display_order": 9
            },
            {
                "id": "subj_10",
                "name": "Programming",
                "description": "Python, Java, C++",
                "icon": "fa-code",
                "color": "pink",
                "enabled": True,
                "display_order": 10
            }
        ]
    }
}

COLOR_THEME_MAP = {
    'blue': {'bg': 'bg-blue-50', 'text': 'text-blue-600', 'border': 'border-blue-100', 'badge_bg': 'bg-blue-50'},
    'green': {'bg': 'bg-emerald-50', 'text': 'text-emerald-600', 'border': 'border-emerald-100', 'badge_bg': 'bg-emerald-50'},
    'purple': {'bg': 'bg-purple-50', 'text': 'text-purple-600', 'border': 'border-purple-100', 'badge_bg': 'bg-purple-50'},
    'amber': {'bg': 'bg-amber-50', 'text': 'text-amber-600', 'border': 'border-amber-100', 'badge_bg': 'bg-amber-50'},
    'rose': {'bg': 'bg-rose-50', 'text': 'text-rose-600', 'border': 'border-rose-100', 'badge_bg': 'bg-rose-50'},
    'red': {'bg': 'bg-red-50', 'text': 'text-red-600', 'border': 'border-red-100', 'badge_bg': 'bg-red-50'},
    'teal': {'bg': 'bg-teal-50', 'text': 'text-teal-600', 'border': 'border-teal-100', 'badge_bg': 'bg-teal-50'},
    'indigo': {'bg': 'bg-indigo-50', 'text': 'text-indigo-600', 'border': 'border-indigo-100', 'badge_bg': 'bg-indigo-50'},
    'yellow': {'bg': 'bg-yellow-50', 'text': 'text-yellow-600', 'border': 'border-yellow-200', 'badge_bg': 'bg-yellow-50'},
    'cyan': {'bg': 'bg-cyan-50', 'text': 'text-cyan-600', 'border': 'border-cyan-100', 'badge_bg': 'bg-cyan-50'},
    'pink': {'bg': 'bg-pink-50', 'text': 'text-pink-600', 'border': 'border-pink-100', 'badge_bg': 'bg-pink-50'},
    'orange': {'bg': 'bg-orange-50', 'text': 'text-orange-600', 'border': 'border-orange-100', 'badge_bg': 'bg-orange-50'},
}


def get_find_tutor_cards_config():
    """
    Load Find Tutor Page Cards configuration from SystemSetting database record.
    Returns exclusively the 3 cards configured for /find-tutor/:
    - why_choose_tutors (Card 1)
    - help_banner (Card 2)
    - faster_banner (Card 3)
    """
    global _FIND_TUTOR_CARDS_CACHE, _FIND_TUTOR_CARDS_CACHE_TIME
    now = time.time()
    if _FIND_TUTOR_CARDS_CACHE is not None and (now - _FIND_TUTOR_CARDS_CACHE_TIME) < 60:
        return _FIND_TUTOR_CARDS_CACHE

    merged = json.loads(json.dumps(DEFAULT_WHY_CHOOSE_CONFIG))
    try:
        obj = SystemSetting.objects.filter(category='homepage', key='hp_why_choose', is_active=True).first()
        if obj and obj.value:
            loaded = json.loads(obj.value) if isinstance(obj.value, str) else obj.value
            if isinstance(loaded, dict):
                if 'why_choose_tutors' in loaded and isinstance(loaded['why_choose_tutors'], dict):
                    merged['why_choose_tutors'].update(loaded['why_choose_tutors'])
                if 'help_banner' in loaded and isinstance(loaded['help_banner'], dict):
                    merged['help_banner'].update(loaded['help_banner'])
                if 'faster_banner' in loaded and isinstance(loaded['faster_banner'], dict):
                    merged['faster_banner'].update(loaded['faster_banner'])
    except Exception as e:
        print("[FIND TUTOR CARDS CONFIG] Exception reading config:", e)

    def to_bool(v, default=True):
        if v is None:
            return default
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(v)
        if isinstance(v, str):
            return v.strip().lower() not in ['false', '0', 'no', 'off', 'disabled']
        return bool(v)

    wct_data = merged.get('why_choose_tutors', {})
    if not isinstance(wct_data, dict):
        wct_data = {}
    def_wct = DEFAULT_WHY_CHOOSE_CONFIG.get('why_choose_tutors', {})
    raw_wct_features = wct_data.get('features') or def_wct.get('features', [
        "Verified & Background Checked",
        "Experienced Subject Experts",
        "Affordable Tuition Plans"
    ])
    if isinstance(raw_wct_features, str):
        raw_wct_features = [f.strip() for f in raw_wct_features.split('\n') if f.strip()]

    hb_data = merged.get('help_banner', {})
    if not isinstance(hb_data, dict):
        hb_data = {}
    def_hb = DEFAULT_WHY_CHOOSE_CONFIG.get('help_banner', {})

    fb_data = merged.get('faster_banner', {})
    if not isinstance(fb_data, dict):
        fb_data = {}
    def_fb = DEFAULT_WHY_CHOOSE_CONFIG.get('faster_banner', {})

    res = {
        'why_choose_tutors': {
            'enabled': to_bool(wct_data.get('enabled'), def_wct.get('enabled', True)),
            'title': wct_data.get('title') or def_wct.get('title', 'Why Choose EduTrust Tutors?'),
            'icon': wct_data.get('icon') or def_wct.get('icon', 'fa-award'),
            'features': raw_wct_features,
            'cta_text': wct_data.get('cta_text') or def_wct.get('cta_text', 'Explore Tutors'),
            'cta_link': wct_data.get('cta_link') or def_wct.get('cta_link', '/find-tutor/')
        },
        'help_banner': {
            'enabled': to_bool(hb_data.get('enabled'), def_hb.get('enabled', True)),
            'title': hb_data.get('title') or def_hb.get('title', 'Need Help Finding the Right Tutor?'),
            'desc': hb_data.get('desc') or def_hb.get('desc', 'Talk to our expert academic advisors for personalized tutor recommendations.'),
            'cta_text': hb_data.get('cta_text') or def_hb.get('cta_text', 'Request Callback'),
            'cta_link': hb_data.get('cta_link') or def_hb.get('cta_link', '/hire/'),
            'icon': hb_data.get('icon') or def_hb.get('icon', 'fa-phone-volume')
        },
        'faster_banner': {
            'enabled': to_bool(fb_data.get('enabled'), def_fb.get('enabled', True)),
            'title': fb_data.get('title') or def_fb.get('title', 'Find Your Perfect Tutor Faster'),
            'desc': fb_data.get('desc') or def_fb.get('desc', 'Post your learning requirement in 2 minutes and get calls from top verified tutors.'),
            'cta_text': fb_data.get('cta_text') or def_fb.get('cta_text', 'Post Requirement'),
            'cta_link': fb_data.get('cta_link') or def_fb.get('cta_link', '/hire/'),
            'icon': fb_data.get('icon') or def_fb.get('icon', 'fa-bolt')
        }
    }
    _FIND_TUTOR_CARDS_CACHE = res
    _FIND_TUTOR_CARDS_CACHE_TIME = now
    return res


def get_why_choose_config():
    """
    Load Why Choose CMS configuration for Homepage from SystemSetting database record.
    Performs deep merging with DEFAULT_WHY_CHOOSE_CONFIG and formats features & explore_subjects.
    Excludes Find Tutor Page Cards to keep them strictly scoped.
    """
    global _WHY_CHOOSE_CACHE, _WHY_CHOOSE_CACHE_TIME
    now = time.time()
    if _WHY_CHOOSE_CACHE is not None and (now - _WHY_CHOOSE_CACHE_TIME) < 60:
        return _WHY_CHOOSE_CACHE

    merged = json.loads(json.dumps(DEFAULT_WHY_CHOOSE_CONFIG))
    merged.pop('why_choose_tutors', None)
    merged.pop('help_banner', None)
    merged.pop('faster_banner', None)
    try:
        obj = SystemSetting.objects.filter(category='homepage', key='hp_why_choose', is_active=True).first()
        if obj and obj.value:
            loaded = json.loads(obj.value) if isinstance(obj.value, str) else obj.value
            if isinstance(loaded, dict):
                # Merge top level scalar keys
                for key in ['enabled', 'title', 'subtitle', 'features_enabled']:
                    if key in loaded:
                        merged[key] = loaded[key]

                # Deep merge features list
                if 'features' in loaded and isinstance(loaded['features'], list):
                    merged['features'] = loaded['features']

                # Deep merge explore_subjects
                if 'explore_subjects' in loaded and isinstance(loaded['explore_subjects'], dict):
                    es_loaded = loaded['explore_subjects']
                    for k in ['enabled', 'badge', 'badge_label', 'badge_icon', 'title', 'heading', 'subtitle']:
                        if k in es_loaded:
                            merged['explore_subjects'][k] = es_loaded[k]
                    if 'subjects' in es_loaded and isinstance(es_loaded['subjects'], list):
                        merged['explore_subjects']['subjects'] = es_loaded['subjects']
    except Exception as e:
        print("[WHY CHOOSE CONFIG] Exception reading config:", e)

    # Strict boolean coercion
    def to_bool(v, default=True):
        if v is None:
            return default
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(v)
        if isinstance(v, str):
            return v.strip().lower() not in ['false', '0', 'no', 'off', 'disabled']
        return bool(v)

    merged['enabled'] = to_bool(merged.get('enabled'), True)
    merged['features_enabled'] = to_bool(merged.get('features_enabled'), True)

    # Clean, sort and enrich features
    raw_features = merged.get('features', [])
    processed_features = []
    for idx, f in enumerate(raw_features):
        color = f.get('color', 'blue')
        theme = COLOR_THEME_MAP.get(color, COLOR_THEME_MAP['blue'])
        
        # Ensure icon has fontawesome prefix
        raw_icon = f.get('icon', 'fa-award')
        if not raw_icon.startswith('fa-') and not raw_icon.startswith('fas ') and not raw_icon.startswith('fa-solid '):
            raw_icon = f"fa-{raw_icon}"
        if not raw_icon.startswith('fas ') and not raw_icon.startswith('fa-solid ') and not raw_icon.startswith('far '):
            icon_cls = f"fas {raw_icon}"
        else:
            icon_cls = raw_icon

        f_enabled = to_bool(f.get('enabled'), True)

        processed_features.append({
            'id': f.get('id', f'feat_{idx}'),
            'title': f.get('title', ''),
            'icon': f.get('icon', 'fa-award'),
            'icon_class': icon_cls,
            'color': color,
            'color_bg': theme['badge_bg'],
            'color_text': theme['text'],
            'color_border': theme['border'],
            'color_badge_bg': theme['bg'],
            'desc': f.get('desc', ''),
            'enabled': f_enabled,
            'order': int(f.get('order', idx + 1))
        })

    # Sort strictly by order
    processed_features.sort(key=lambda item: item['order'])
    merged['features'] = processed_features
    # Enabled features for direct public template iteration
    merged['active_features'] = [f for f in processed_features if f['enabled']]

    # Prepare heading formatting for main why choose
    title_str = merged.get('title', 'Why Students Trust Us')
    words = title_str.split(' ')
    if len(words) >= 2:
        merged['title_main'] = ' '.join(words[:-2]) if len(words) > 2 else words[0]
        merged['title_highlight'] = ' '.join(words[-2:]) if len(words) > 2 else words[1]
    else:
        merged['title_main'] = title_str
        merged['title_highlight'] = ''

    # Clean, sort and enrich explore_subjects
    es_data = merged.get('explore_subjects', {})
    es_enabled = to_bool(es_data.get('enabled'), True)
    raw_subjects = es_data.get('subjects', [])
    processed_subjects = []

    for idx, s in enumerate(raw_subjects):
        s_color = s.get('color', 'blue')
        s_theme = COLOR_THEME_MAP.get(s_color, COLOR_THEME_MAP['blue'])

        raw_s_icon = s.get('icon', 'fa-book')
        if not raw_s_icon.startswith('fa-') and not raw_s_icon.startswith('fas ') and not raw_s_icon.startswith('fa-solid '):
            raw_s_icon = f"fa-{raw_s_icon}"
        if not raw_s_icon.startswith('fas ') and not raw_s_icon.startswith('fa-solid ') and not raw_s_icon.startswith('far '):
            s_icon_cls = f"fas {raw_s_icon}"
        else:
            s_icon_cls = raw_s_icon

        s_enabled = to_bool(s.get('enabled'), True)

        s_link = s.get('link') or f"/find-tutor/?subject={s.get('name', '')}"

        processed_subjects.append({
            'id': s.get('id', f'subj_{idx + 1}'),
            'name': s.get('name', ''),
            'description': s.get('description', s.get('desc', '')),
            'desc': s.get('description', s.get('desc', '')),
            'icon': s.get('icon', 'fa-book'),
            'icon_class': s_icon_cls,
            'color': s_color,
            'color_bg': s_theme['bg'],
            'color_text': s_theme['text'],
            'color_border': s_theme['border'],
            'bg_class': s_theme['bg'],
            'text_class': s_theme['text'],
            'link': s_link,
            'enabled': s_enabled,
            'display_order': int(s.get('display_order', s.get('order', idx + 1)))
        })

    processed_subjects.sort(key=lambda item: item['display_order'])

    es_title = es_data.get('heading') or es_data.get('title') or 'Explore Popular Subjects'
    es_words = es_title.split(' ')
    if len(es_words) >= 2:
        es_heading_main = ' '.join(es_words[:-2]) if len(es_words) > 2 else es_words[0]
        es_heading_highlight = ' '.join(es_words[-2:]) if len(es_words) > 2 else es_words[1]
    else:
        es_heading_main = es_title
        es_heading_highlight = ''

    es_badge = es_data.get('badge_label') or es_data.get('badge') or 'Explore Popular Subjects'

    merged['explore_subjects'] = {
        'enabled': es_enabled,
        'badge': es_badge,
        'badge_label': es_badge,
        'badge_icon': es_data.get('badge_icon', 'fa-book-open'),
        'title': es_title,
        'heading': es_title,
        'heading_main': es_heading_main,
        'heading_highlight': es_heading_highlight,
        'subtitle': es_data.get('subtitle', 'Find expert tutors for any subject, ensuring comprehensive understanding and top grades.'),
        'subjects': processed_subjects,
        'active_subjects': [s for s in processed_subjects if s['enabled']]
    }

    _WHY_CHOOSE_CACHE = merged
    _WHY_CHOOSE_CACHE_TIME = now
    return merged


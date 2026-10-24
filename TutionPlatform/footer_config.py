import json
import copy
from .models import SystemSetting, WebsiteFooterColumn, WebsiteFooterLink

DEFAULT_FOOTER_CONFIG = {
    'general': {
        'enabled': True,
        'title': 'EduTrust',
        'show_description': True,
        'show_on_website': True,
        'show_brand_column': True,
        'show_quick_links': True,
        'show_top_subjects': True,
        'show_social_column': True,
        'show_newsletter_column': True,
        'show_legal_links': True,
        'copyright_text': '© 2026 EduTrust Platform. All rights reserved.',
        'show_bottom_links': True,
        'show_on_mobile': True,
        'show_back_to_top': True,
        'back_to_top_position': 'right',
        'layout_type': 'columns_4',
        'tagline': "India's premier home tuition & learning platform."
    },
    'branding': {
        'show_brand_section': True,
        'show_logo': True,
        'show_company_name': True,
        'company_name': 'Edu',
        'company_name_highlight': 'Trust',
        'logo_badge': 'E',
        'description': "India's most trusted platform for online and home tuition. Empowering students with top-tier education since 2020.",
        'tagline': 'Empowering Next-Gen Education',
        'trust_badge_text': 'Verified Tutors & Safe Learning',
        'established_year': '2020'
    },
    'columns': [
        {
            'id': 'col_quick_links',
            'title': 'Quick Links',
            'icon': 'fas fa-link',
            'order': 1,
            'is_active': True,
            'links': [
                {'id': 'lnk_1', 'label': 'About Us', 'url': '/about/', 'target': '_self', 'is_active': True, 'order': 1, 'badge': ''},
                {'id': 'lnk_2', 'label': 'Courses', 'url': '/courses/', 'target': '_self', 'is_active': True, 'order': 2, 'badge': ''},
                {'id': 'lnk_3', 'label': 'Find Tutor', 'url': '/find-tutor/', 'target': '_self', 'is_active': True, 'order': 3, 'badge': ''},
                {'id': 'lnk_4', 'label': 'Become a Tutor', 'url': '/teacher-registration/', 'target': '_self', 'is_active': True, 'order': 4, 'badge': ''},
                {'id': 'lnk_5', 'label': 'Study Material', 'url': '/study-material/', 'target': '_self', 'is_active': True, 'order': 5, 'badge': ''},
                {'id': 'lnk_6', 'label': 'Success Stories', 'url': '/success-stories/', 'target': '_self', 'is_active': True, 'order': 6, 'badge': ''},
                {'id': 'lnk_7', 'label': 'FAQs', 'url': '/faq/', 'target': '_self', 'is_active': True, 'order': 7, 'badge': ''},
                {'id': 'lnk_8', 'label': 'Contact Support', 'url': '/contact/', 'target': '_self', 'is_active': True, 'order': 8, 'badge': ''}
            ]
        },
        {
            'id': 'col_top_subjects',
            'title': 'Top Subjects',
            'icon': 'fas fa-book-open',
            'order': 2,
            'is_active': True,
            'links': [
                {'id': 'lnk_9', 'label': 'Mathematics Tuition', 'url': '/find-tutor/?subject=math', 'target': '_self', 'is_active': True, 'order': 1, 'badge': ''},
                {'id': 'lnk_10', 'label': 'Physics Classes', 'url': '/find-tutor/?subject=physics', 'target': '_self', 'is_active': True, 'order': 2, 'badge': ''},
                {'id': 'lnk_11', 'label': 'Chemistry Tutors', 'url': '/find-tutor/?subject=chemistry', 'target': '_self', 'is_active': True, 'order': 3, 'badge': ''},
                {'id': 'lnk_12', 'label': 'Spoken English', 'url': '/find-tutor/?subject=english', 'target': '_self', 'is_active': True, 'order': 4, 'badge': ''},
                {'id': 'lnk_13', 'label': 'Coding for Kids', 'url': '/find-tutor/?subject=coding', 'target': '_self', 'is_active': True, 'order': 5, 'badge': ''}
            ]
        }
    ],
    'contact': {
        'show_contact_info': True,
        'email': 'support@edutrust.com',
        'phone': '+91 98765 43210',
        'whatsapp': '+91 98765 43210',
        'address': '123 Education Hub, Sector 5, Salt Lake, Kolkata 700091',
        'working_hours': 'Mon - Sat: 9:00 AM - 8:00 PM',
        'items': [
            {'id': 'ci_1', 'label': 'Email Support', 'value': 'support@edutrust.com', 'icon': 'far fa-envelope', 'action': 'mailto:support@edutrust.com', 'is_active': True},
            {'id': 'ci_2', 'label': 'Phone', 'value': '+91 98765 43210', 'icon': 'fas fa-phone-alt', 'action': 'tel:+919876543210', 'is_active': True}
        ]
    },
    'social': {
        'show_social_icons': True,
        'links': [
            {'platform': 'facebook', 'label': 'Facebook', 'url': 'https://facebook.com', 'icon': 'fab fa-facebook-f', 'is_active': True},
            {'platform': 'twitter', 'label': 'Twitter / X', 'url': 'https://x.com', 'icon': 'fab fa-twitter', 'is_active': True},
            {'platform': 'instagram', 'label': 'Instagram', 'url': 'https://instagram.com', 'icon': 'fab fa-instagram', 'is_active': True},
            {'platform': 'linkedin', 'label': 'LinkedIn', 'url': 'https://linkedin.com', 'icon': 'fab fa-linkedin-in', 'is_active': True},
            {'platform': 'youtube', 'label': 'YouTube', 'url': '', 'icon': 'fab fa-youtube', 'is_active': False},
            {'platform': 'whatsapp', 'label': 'WhatsApp', 'url': '', 'icon': 'fab fa-whatsapp', 'is_active': False}
        ]
    },
    'newsletter': {
        'show_newsletter': True,
        'title': 'Newsletter',
        'description': 'Subscribe to get latest updates and educational tips.',
        'placeholder': 'Enter your email',
        'button_text': 'Subscribe'
    },
    'cta': {
        'show_cta_banner': False,
        'title': "Ready to Start Learning with India's Best Tutors?",
        'subtitle': 'Book your 100% free trial session today and experience personalized learning.',
        'button_text': 'Book Free Trial',
        'button_url': '/book-demo/',
        'button_visible': True,
        'icon': 'fas fa-sparkles'
    },
    'legal': {
        'show_legal_bar': True,
        'show_copyright': True,
        'links': [
            {'label': 'Privacy Policy', 'url': '/privacy-policy/', 'target': '_self', 'is_active': True},
            {'label': 'Terms of Service', 'url': '/terms-of-service/', 'target': '_self', 'is_active': True},
            {'label': 'Cookie Policy', 'url': '/cookie-policy/', 'target': '_self', 'is_active': False}
        ]
    },
    'appearance': {
        'theme': 'dark',
        'bg_color': '#111827',
        'text_color': '#d1d5db',
        'heading_color': '#ffffff',
        'accent_color': '#3b82f6',
        'border_color': '#1f2937'
    },
    'scope': 'all',
    'selected_pages': ['home', 'find_tutor', 'hire_tutor', 'courses', 'about', 'contact', 'faq', 'blog', 'other']
}

def get_default_footer_config():
    return copy.deepcopy(DEFAULT_FOOTER_CONFIG)

def deep_merge(target, source):
    if not source or not isinstance(source, dict):
        return target
    for key, val in source.items():
        if isinstance(val, dict) and key in target and isinstance(target[key], dict):
            target[key] = deep_merge(target[key], val)
        else:
            target[key] = val
    return target

def get_active_footer_config(current_path=None):
    cfg = get_default_footer_config()
    try:
        setting_obj = SystemSetting.objects.filter(key='hp_footer', category='homepage').first()
        if setting_obj and setting_obj.value:
            saved = json.loads(setting_obj.value) if isinstance(setting_obj.value, str) else setting_obj.value
            cfg = deep_merge(cfg, saved)
    except Exception as e:
        print(f"[FOOTER CONFIG ERROR] {e}")

    is_master_enabled = cfg.get('general', {}).get('enabled', True)
    if not is_master_enabled or cfg.get('general', {}).get('show_on_website') is False:
        return cfg, True

    if current_path:
        path = current_path.lower()
        scope = cfg.get('scope', 'all')
        if scope == 'home_only':
            if path not in ['/', '/home', '/home/']:
                return cfg, True
        elif scope == 'selected':
            selected = cfg.get('selected_pages', [])
            page_key = 'other'
            if path in ['/', '/home', '/home/']:
                page_key = 'home'
            elif 'find-tutor' in path or 'findtutor' in path:
                page_key = 'find_tutor'
            elif 'hire-tutor' in path or 'teacher-registration' in path or 'tuition-jobs' in path or 'latest-tution-job' in path:
                page_key = 'hire_tutor'
            elif 'course' in path:
                page_key = 'courses'
            elif 'about' in path:
                page_key = 'about'
            elif 'contact' in path:
                page_key = 'contact'
            elif 'faq' in path:
                page_key = 'faq'
            elif 'blog' in path:
                page_key = 'blog'
            
            if page_key not in selected:
                return cfg, True

    return cfg, False

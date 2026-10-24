# -*- coding: utf-8 -*-
from django import template
from TutionPlatform.website_mode import (
    get_website_mode,
    is_home_tuition_mode,
    is_online_tuition_mode,
    is_full_lms_mode,
    feature_enabled,
    get_feature_matrix
)

register = template.Library()

@register.simple_tag
def current_website_mode():
    return get_website_mode()

@register.filter(name='is_feature_enabled')
def is_feature_enabled_filter(feature_name):
    return feature_enabled(feature_name)

@register.simple_tag
def check_feature(feature_name):
    return feature_enabled(feature_name)

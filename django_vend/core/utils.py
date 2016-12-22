from django.conf import settings

vend_settings = {
    'VEND_DEFAULT_USER_IMAGE': ('https://secure.vendhq.com/images/placeholder'
                                '/customer/no-image-white-standard.png'),
}

def get_vend_setting(name):
    return getattr(settings, name, None) or vend_settings.get(name)

import dateutil.parser

from django.conf import settings

vend_settings = {
    'VEND_DEFAULT_USER_IMAGE': ('https://secure.vendhq.com/images/placeholder'
                                '/customer/no-image-white-standard.png'),
}

def get_vend_setting(name):
    return getattr(settings, name, None) or vend_settings.get(name)


def parse_date(possible_date):
    if not possible_date or possible_date == "null":
        return None
    else:
        return dateutil.parser.parse(possible_date)

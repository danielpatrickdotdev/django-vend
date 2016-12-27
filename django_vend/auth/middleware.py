from django.utils.functional import SimpleLazyObject

from .models import VendUser


def get_session_venduser(request):
    # Can't refer to venduser if not authenticated
    if not request.user.is_authenticated:
        return None

    # If venduser is in session, use it
    pk = request.session.get('venduser_id')
    venduser = VendUser.objects.filter(pk=pk).first()

    # Let's just check we've got a valid venduser for request.user
    if not venduser in request.user.vendprofile.vendusers.all():
        venduser = None
        if 'venduser_id' in request.session:
            del request.session['venduser_id']

    # If not in session, if authenticated user only has one associated venduser
    # we can just use that
    if not venduser:
        vendusers = request.user.vendprofile.vendusers.all()
        if len(vendusers) == 1:
            venduser = vendusers.get()
            request.session['venduser_id'] = venduser.pk

    return venduser

def get_venduser(request):
    if not hasattr(request, '_cached_venduser'):
        request._cached_venduser = get_session_venduser(request)
    return request._cached_venduser

def vend_auth_middleware(get_response):

    def middleware(request):
        request.venduser = SimpleLazyObject(lambda: get_venduser(request))

        response = get_response(request)

        return response

    return middleware

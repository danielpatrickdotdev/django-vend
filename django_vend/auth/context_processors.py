def vendauth(request):
    return {
        'venduser': getattr(request, 'venduser'),
    }

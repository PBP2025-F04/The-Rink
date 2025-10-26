def is_admin(request):
    return {'is_admin': request.session.get('is_admin', False)}

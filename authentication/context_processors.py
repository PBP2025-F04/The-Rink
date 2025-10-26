def is_admin(request):
    return {'is_admin': request.session.get('is_admin', False)}

def is_admin_logged_in(request):
    return {'is_admin_logged_in': request.session.get('admin_logged_in', False)}

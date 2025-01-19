from django.http import HttpResponseForbidden
from functools import wraps

def role_required(required_role):
    """
    A decorator to restrict access to users with a specific role.
    :param required_role: The role required to access the view (e.g., 'buyer', 'seller').
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if hasattr(request.user, 'role') and request.user.role == required_role:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You do not have permission to access this page.")
        return _wrapped_view
    return decorator

buyer_required = role_required('buyer')
seller_required = role_required('seller')

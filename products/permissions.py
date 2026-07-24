from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def seller_or_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role in ("admin", "sales"):
            return view_func(request, *args, **kwargs)
        messages.error(request, "You do not have permission to manage products.")
        return redirect("products:list")
    return wrapper

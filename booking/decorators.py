from django.shortcuts import redirect

def role_required(role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if request.user.profile.role != role:
                return redirect('login')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
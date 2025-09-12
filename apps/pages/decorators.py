from django.shortcuts import redirect
from functools import wraps
from .models import UserProfile


def onboarding_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            profile = UserProfile.objects.get(user=request.user)
            if not profile.onboarding_completed:
                return redirect("onboarding")
        except UserProfile.DoesNotExist:
            return redirect("onboarding")
        return view_func(request, *args, **kwargs)

    return _wrapped_view

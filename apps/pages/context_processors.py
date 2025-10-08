from .models import UserProfile


def user_profile(request):
    """Add the authenticated user's profile and display name to the context."""

    user = getattr(request, "user", None)

    if user is None or not user.is_authenticated:
        return {"user_profile": None, "user_display_name": None}

    profile = None

    try:
        profile = UserProfile.objects.select_related("user").get(user=user)
    except UserProfile.DoesNotExist:
        profile = None

    if profile and profile.display_name:
        display_name = profile.display_name
    else:
        display_name = user.get_full_name() or user.get_username()

    return {"user_profile": profile, "user_display_name": display_name}

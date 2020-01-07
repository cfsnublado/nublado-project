from .models import Profile


def get_avatar(backend, strategy, details, response, user=None, *args, **kwargs):
    if backend.name == "google-oauth2":
        image_url = response.get("picture", None)

        if image_url is not None:
            profile = Profile.objects.get(user_id=user.id)
            profile.avatar_url = image_url
            profile.save()

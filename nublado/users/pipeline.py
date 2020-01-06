def get_avatar(backend, strategy, details, response, user=None, *args, **kwargs):
    if backend.name == "google-oauth2":
        user.image_url = response["picture"]


def is_requested_user(user, requested_user, superuser_override=True):
    return (superuser_override and user.is_superuser) or user == requested_user

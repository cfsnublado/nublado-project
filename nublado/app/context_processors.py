from django.conf import settings


def global_settings(request):
    """
    Returns values to be gobally available in templates.
    """
    return {
        "project_name": settings.PROJECT_NAME,
        "sidebar_expanded": "sidebar_locked" in request.session and request.session["sidebar_locked"],
        "session_obj_enabled": False,
        "sidebar_top_panel_expanded": False
    }

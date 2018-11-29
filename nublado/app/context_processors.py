from django.conf import settings


def global_settings(request):
    """
    Returns values to be gobally available in templates.
    """

    session_obj_enabled = any(k in request.session for k in ("vocab_project", "vocab_source", "vocab_entry"))

    return {
        "project_name": settings.PROJECT_NAME,
        "sidebar_expanded": "sidebar_locked" in request.session and request.session["sidebar_locked"],
        "session_obj_enabled": session_obj_enabled,
        "sidebar_top_panel_expanded": session_obj_enabled
    }

# ...existing code...
# app package init - expose UI entrypoints without forcing heavy imports

__all__ = ["run_app", "render_login_page", "render_dashboard"]

# Lazy import helpers: try to bind common UI functions if modules exist
def _try_import(mod_name):
    try:
        return __import__(f"{__package__}.{mod_name}", fromlist=[mod_name])
    except Exception:
        return None

_ui = _try_import("ui")
_login = _try_import("login")
_dashboard = _try_import("dashboard")

if _ui and hasattr(_ui, "run_app"):
    run_app = _ui.run_app

if _login and hasattr(_login, "render_login_page"):
    render_login_page = _login.render_login_page

if _dashboard and hasattr(_dashboard, "render_dashboard"):
    render_dashboard = _dashboard.render_dashboard
# ...existing code...
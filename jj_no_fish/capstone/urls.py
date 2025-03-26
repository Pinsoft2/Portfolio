from django.contrib import admin
from django.urls import path, include
from . import views

# Base URL patterns without prefix
base_patterns = [
    path("", views.jj_no_fish, name="jj_no_fish"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("history/<int:user_id>/", views.history, name="history"),
    path("debug/", views.debug_view, name="debug"),
]

# Main URL patterns - combine base patterns with prefixed patterns
urlpatterns = base_patterns + [
    path("admin/", admin.site.urls),
    # Add prefixed versions of all routes
    path("jj-no-fish/", views.jj_no_fish, name="jj_no_fish_prefixed"),
    path("jj-no-fish/login", views.login_view, name="login_prefixed"),
    path("jj-no-fish/logout", views.logout_view, name="logout_prefixed"),
    path("jj-no-fish/register", views.register, name="register_prefixed"),
    path("jj-no-fish/history/<int:user_id>/", views.history, name="history_prefixed"),
    path("jj-no-fish/debug/", views.debug_view, name="debug_prefixed"),
]
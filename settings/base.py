from pathlib import Path

from django.urls import reverse_lazy

from apps.blog.tab_links import posts_all_link, posts_drafts_link, posts_published_link
from settings import conf

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = conf.SECRET_KEY

ALLOWED_HOSTS: list[str] = []

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.auths",
    "apps.blog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "settings.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "settings.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "auths.User"

UNFOLD = {
    "SITE_TITLE": "Blog API",
    "SITE_HEADER": "Blog API",
    "SITE_SUBHEADER": "Content management",
    "SITE_SYMBOL": "edit_note",
    "COLORS": {
        "primary": {
            "50": "oklch(98.4% 0.014 180.72)",
            "100": "oklch(95.3% 0.051 180.801)",
            "200": "oklch(91% 0.096 180.426)",
            "300": "oklch(85.5% 0.138 181.071)",
            "400": "oklch(77.7% 0.152 181.912)",
            "500": "oklch(70.4% 0.14 182.503)",
            "600": "oklch(60% 0.118 184.704)",
            "700": "oklch(51.1% 0.096 186.391)",
            "800": "oklch(43.7% 0.078 188.216)",
            "900": "oklch(38.6% 0.063 188.416)",
            "950": "oklch(27.7% 0.046 192.524)",
        },
    },
    "ENVIRONMENT": "apps.blog.callbacks.environment_callback",
    "SITE_DROPDOWN": [
        {
            "icon": "code",
            "title": "GitHub repository",
            "link": "https://github.com/FawadHakimi/blog-api",
        },
        {
            "icon": "menu_book",
            "title": "Unfold documentation",
            "link": "https://unfoldadmin.com/docs/",
        },
    ],
    "COMMAND": {
        "search_models": True,
    },
    "DASHBOARD_CALLBACK": "apps.blog.callbacks.dashboard_callback",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Overview",
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": "Content",
                "items": [
                    {
                        "title": "Posts",
                        "icon": "article",
                        "link": reverse_lazy("admin:blog_post_changelist"),
                        "badge": "apps.blog.callbacks.drafts_badge",
                    },
                    {
                        "title": "Comments",
                        "icon": "forum",
                        "link": reverse_lazy("admin:blog_comment_changelist"),
                    },
                    {
                        "title": "Categories",
                        "icon": "category",
                        "link": reverse_lazy("admin:blog_category_changelist"),
                    },
                    {
                        "title": "Tags",
                        "icon": "sell",
                        "link": reverse_lazy("admin:blog_tag_changelist"),
                    },
                ],
            },
            {
                "title": "Users & Access",
                "items": [
                    {
                        "title": "Users",
                        "icon": "person",
                        "link": reverse_lazy("admin:auths_user_changelist"),
                        "permission": "apps.blog.callbacks.superuser_only",
                    },
                    {
                        "title": "Groups",
                        "icon": "groups",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                        "permission": "apps.blog.callbacks.superuser_only",
                    },
                ],
            },
        ],
    },
    "TABS": [
        {
            "models": ["blog.post"],
            "items": [
                {"title": "All", "link": posts_all_link},
                {"title": "Published", "link": posts_published_link},
                {"title": "Drafts", "link": posts_drafts_link},
            ],
        },
    ],
}

# ruff: noqa: ERA001, E501
"""Base settings to build other settings files upon."""
from collections import OrderedDict
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
# dsat/
APPS_DIR = BASE_DIR
env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=True)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(BASE_DIR / ".env"))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)

DEBUG_TOOLBAR_ENABLED = env.bool("DJANGO_DEBUG_TOOLBAR_ENABLED", DEBUG)
SILK_ENABLED = env.bool("DJANGO_SILK_ENABLED", False)

# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "UTC"
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-us"
# https://docs.djangoproject.com/en/dev/ref/settings/#languages
# from django.utils.translation import gettext_lazy as _
# LANGUAGES = [
#     ('en', _('English')),
#     ('fr-fr', _('French')),
#     ('pt-br', _('Portuguese')),
# ]
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [str(BASE_DIR / "locale")]

# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)
# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-DEFAULT_AUTO_FIELD
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CACHES = {
    "memory": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "oneprep-snowflake",
    }
}

REDIS_URL = env.str("REDIS_URL", default="")
if REDIS_URL:
    CACHES["default"] = {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # "IGNORE_EXCEPTIONS": True,
            "PICKLE_VERSION": -1,
        }
    }
    CACHES["redis"] = CACHES["default"]


# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    # "django.contrib.sessions",
    "qsessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize", # Handy template tags

    "django_admin_env_notice",
    "related_admin",

    "django.contrib.admin",
    "django.forms",
]

# TODO https://github.com/trangpham/django-admin-confirm/

THIRD_PARTY_APPS = [
    "django_extensions",
    # "silk",
    "constance",
    *([
          "debug_toolbar",
          "template_profiler_panel"
      ] if DEBUG_TOOLBAR_ENABLED else []),
    *(["silk"] if SILK_ENABLED else []),

    "crispy_forms",
    "crispy_bootstrap5",
    # "crispy_tailwind",

    "django_filters",
    "mathfilters",

    "allauth_ui",

    "django_login_history2",

    "allauth",
    "allauth.account",
    "allauth.socialaccount",

    "widget_tweaks",
    "slippers",

    # Admin
    "import_export",
    "djangoql",
    "django_object_actions",

    # Model
    "taggit",
]

LOCAL_APPS = [
    "core",
    "charts",

    "users",

    "app",

    "programs",
    "questions",
    "exams",


]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
MIGRATION_MODULES = {"sites": "contrib.sites.migrations"}

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
# LOGIN_REDIRECT_URL = "users:redirect"
LOGIN_REDIRECT_URL = "home"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "account_login"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    # "core.middleware.PA2FlyRedirectMiddleware",

    # "django.contrib.sessions.middleware.SessionMiddleware",
    "qsessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    # "silk.middleware.SilkyMiddleware"

    "core.middleware.ProfileMiddleware",

    *(["debug_toolbar.middleware.DebugToolbarMiddleware"] if DEBUG_TOOLBAR_ENABLED else []),
    *(["silk.middleware.SilkyMiddleware"] if SILK_ENABLED else []),
]

SESSION_ENGINE = "qsessions.backends.cached_db"

GEOIP_PATH = env.str('GEOIP_PATH', str(BASE_DIR / "data" / "geoip"))

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(BASE_DIR / "staticfiles")
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(APPS_DIR / "static")]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR / "media")
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#dirs
        "DIRS": [str(APPS_DIR / "templates")],
        # https://docs.djangoproject.com/en/dev/ref/settings/#app-dirs
        "APP_DIRS": True,
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "users.context_processors.allauth_settings",
                "django_admin_env_notice.context_processors.from_settings",

                "utils.context_processors.base_context",
                "utils.context_processors.google_analytics_context",
                "utils.context_processors.theme_context",
                "utils.context_processors.ip_address_context",

                "utils.context_processors.internet_blackout_context",
            ],
        },
    },
]

# https://docs.djangoproject.com/en/dev/ref/settings/#form-renderer
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

DATA_UPLOAD_MAX_NUMBER_FIELDS = env.int("DJANGO_DATA_UPLOAD_MAX_NUMBER_FIELDS", default=1024 * 10)
DATA_UPLOAD_MAX_MEMORY_SIZE = env.int("DJANGO_DATA_UPLOAD_MAX_MEMORY_SIZE", default=1024 * 1024 * 10)

# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
# CRISPY_TEMPLATE_PACK = "bootstrap5"
# CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "tailwind"
CRISPY_ALLOWED_TEMPLATE_PACKS = ("tailwind", "bootstrap5")

DAISYUI_THEME = ALLAUTH_UI_THEME = env.str("DAISYUI_THEME", default="light")

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR / "fixtures"),)

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [("""Abdullah Mallik""", "mdn522@gmail.com")]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
# https://cookiecutter-django.readthedocs.io/en/latest/settings.html#other-environment-settings
# Force the `admin` sign in process to go through the `django-allauth` workflow
DJANGO_ADMIN_FORCE_ALLAUTH = env.bool("DJANGO_ADMIN_FORCE_ALLAUTH", default=False)

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}


# django-allauth
# ------------------------------------------------------------------------------
ACCOUNT_ALLOW_REGISTRATION = env.bool("DJANGO_ACCOUNT_ALLOW_REGISTRATION", True)
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_AUTHENTICATION_METHOD = "username_email"  # "username"
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_EMAIL_REQUIRED = True
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_USERNAME_REQUIRED = True
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_LOGOUT_ON_GET = True
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_ADAPTER = "users.adapters.AccountAdapter"
# https://docs.allauth.org/en/latest/account/forms.html
ACCOUNT_FORMS = {
    "signup": "users.forms.UserSignupForm"
}
# https://docs.allauth.org/en/latest/socialaccount/configuration.html
SOCIALACCOUNT_ADAPTER = "users.adapters.SocialAccountAdapter"
# https://docs.allauth.org/en/latest/socialaccount/configuration.html
SOCIALACCOUNT_FORMS = {"signup": "users.forms.UserSocialSignupForm"}

ACCOUNT_USERNAME_VALIDATORS = "users.validators.custom_username_validators"

ACCOUNT_USERNAME_BLACKLIST = [
    'www', 'ns1', 'ns2', 'ns3', 'ns4', 'ns5', 'dns', 'http', 'https',
    'news', 'nntp', 'ftp', 'sftp', 'file', 'mail', 'imap', 'pop3', 'smtp', 'ssh', 'tel', 'admin', 'registration', 'register', 'about', 'help', 'support', 'staff', 'root', 'feed', 'blog', 'noreply', 'media', 'static',
    "administrator", "administrators", "admins",
    "abdullahmallik", "abdullah", "mallik", "abdullah_mallik", "abdullah-mallik"
]

# https://github.com/marteinn/The-Big-Username-Blocklist
# 2024-08-17
ACCOUNT_USERNAME_BLACKLIST += [".git", ".htaccess", ".htpasswd", ".well-known", "400", "401", "403", "404", "405", "406", "407", "408", "409", "410", "411", "412", "413", "414", "415", "416", "417", "421", "422", "423", "424", "426", "428", "429", "431", "500", "501", "502", "503", "504", "505", "506", "507", "508", "509", "510", "511", "_domainkey", "about", "about-us", "abuse", "access", "account", "accounts", "ad", "add", "admin", "administration", "administrator", "ads", "ads.txt", "advertise", "advertising", "aes128-ctr", "aes128-gcm", "aes192-ctr", "aes256-ctr", "aes256-gcm", "affiliate", "affiliates", "ajax", "alert", "alerts", "alpha", "amp", "analytics", "api", "app", "app-ads.txt", "apps", "asc", "assets", "atom", "auth", "authentication", "authorize", "autoconfig", "autodiscover", "avatar", "backup", "banner", "banners", "bbs", "beta", "billing", "billings", "blog", "blogs", "board", "bookmark", "bookmarks", "broadcasthost", "business", "buy", "cache", "calendar", "campaign", "captcha", "careers", "cart", "cas", "categories", "category", "cdn", "cgi", "cgi-bin", "chacha20-poly1305", "change", "channel", "channels", "chart", "chat", "checkout", "clear", "client", "close", "cloud", "cms", "com", "comment", "comments", "community", "compare", "compose", "config", "connect", "contact", "contest", "cookies", "copy", "copyright", "count", "cp", "cpanel", "create", "crossdomain.xml", "css", "curve25519-sha256", "customer", "customers", "customize", "dashboard", "db", "deals", "debug", "delete", "desc", "destroy", "dev", "developer", "developers", "diffie-hellman-group-exchange-sha256", "diffie-hellman-group14-sha1", "disconnect", "discuss", "dns", "dns0", "dns1", "dns2", "dns3", "dns4", "docs", "documentation", "domain", "download", "downloads", "downvote", "draft", "drop", "ecdh-sha2-nistp256", "ecdh-sha2-nistp384", "ecdh-sha2-nistp521", "edit", "editor", "email", "enterprise", "error", "errors", "event", "events", "example", "exception", "exit", "explore", "export", "extensions", "false", "family", "faq", "faqs", "favicon.ico", "features", "feed", "feedback", "feeds", "file", "files", "filter", "follow", "follower", "followers", "following", "fonts", "forgot", "forgot-password", "forgotpassword", "form", "forms", "forum", "forums", "friend", "friends", "ftp", "get", "git", "go", "graphql", "group", "groups", "guest", "guidelines", "guides", "head", "header", "help", "hide", "hmac-sha", "hmac-sha1", "hmac-sha1-etm", "hmac-sha2-256", "hmac-sha2-256-etm", "hmac-sha2-512", "hmac-sha2-512-etm", "home", "host", "hosting", "hostmaster", "htpasswd", "http", "httpd", "https", "humans.txt", "icons", "images", "imap", "img", "import", "index", "info", "insert", "investors", "invitations", "invite", "invites", "invoice", "is", "isatap", "issues", "it", "jobs", "join", "js", "json", "keybase.txt", "learn", "legal", "license", "licensing", "like", "limit", "live", "load", "local", "localdomain", "localhost", "lock", "login", "logout", "lost-password", "m", "mail", "mail0", "mail1", "mail2", "mail3", "mail4", "mail5", "mail6", "mail7", "mail8", "mail9", "mailer-daemon", "mailerdaemon", "map", "marketing", "marketplace", "master", "me", "media", "member", "members", "message", "messages", "metrics", "mis", "mobile", "moderator", "modify", "more", "mx", "mx1", "my", "net", "network", "new", "news", "newsletter", "newsletters", "next", "nil", "no-reply", "nobody", "noc", "none", "noreply", "notification", "notifications", "ns", "ns0", "ns1", "ns2", "ns3", "ns4", "ns5", "ns6", "ns7", "ns8", "ns9", "null", "oauth", "oauth2", "offer", "offers", "online", "openid", "order", "orders", "overview", "owa", "owner", "page", "pages", "partners", "passwd", "password", "pay", "payment", "payments", "paypal", "photo", "photos", "pixel", "plans", "plugins", "policies", "policy", "pop", "pop3", "popular", "portal", "portfolio", "post", "postfix", "postmaster", "poweruser", "preferences", "premium", "press", "previous", "pricing", "print", "privacy", "privacy-policy", "private", "prod", "product", "production", "profile", "profiles", "project", "projects", "promo", "public", "purchase", "put", "quota", "redirect", "reduce", "refund", "refunds", "register", "registration", "remove", "replies", "reply", "report", "request", "request-password", "reset", "reset-password", "response", "return", "returns", "review", "reviews", "robots.txt", "root", "rootuser", "rsa-sha2-2", "rsa-sha2-512", "rss", "rules", "sales", "save", "script", "sdk", "search", "secure", "security", "select", "services", "session", "sessions", "settings", "setup", "share", "shift", "shop", "signin", "signup", "site", "sitemap", "sites", "smtp", "sort", "source", "sql", "ssh", "ssh-rsa", "ssl", "ssladmin", "ssladministrator", "sslwebmaster", "stage", "staging", "stat", "static", "statistics", "stats", "status", "store", "style", "styles", "stylesheet", "stylesheets", "subdomain", "subscribe", "sudo", "super", "superuser", "support", "survey", "sync", "sysadmin", "sysadmin", "system", "tablet", "tag", "tags", "team", "telnet", "terms", "terms-of-use", "test", "testimonials", "theme", "themes", "today", "tools", "topic", "topics", "tour", "training", "translate", "translations", "trending", "trial", "true", "umac-128", "umac-128-etm", "umac-64", "umac-64-etm", "undefined", "unfollow", "unlike", "unsubscribe", "update", "upgrade", "usenet", "user", "username", "users", "uucp", "var", "verify", "video", "view", "void", "vote", "vpn", "webmail", "webmaster", "website", "widget", "widgets", "wiki", "wpad", "write", "www", "www-data", "www1", "www2", "www3", "www4", "you", "yourname", "yourusername", "zlib"]

# https://github.com/flurdy/bad_usernames
# 2024-08-17
ACCOUNT_USERNAME_BLACKLIST += ["abuse", "account", "adm", "admin", "admins", "administrator", "administrators", "all", "ceo", "cfo", "contact", "coo", "customer", "document", "documents", "download", "downloads", "faq", "file", "files", "ftp", "help", "home", "host_master", "host-master", "hostmaster", "http", "https", "imap", "info", "ldap", "list", "list-request", "mail", "majordomo", "manager", "marketing", "member", "membership", "mis", "news", "noreply", "office", "owner", "password", "pop", "post_master", "post-master", "postfix", "postmaster", "register", "registration", "root", "sales", "secure", "security", "sftp", "site", "shop", "smtp", "ssl", "ssl_admin", "ssl-admin", "ssladmin", "ssl_administrator", "ssl-administrator", "ssladministrator", "ssl_webmaster", "ssl-webmaster", "sslwebmaster", "support", "sysadmin", "test", "trouble", "usenet", "user", "username", "users", "web", "web_master", "web-master", "webmaster", "web_admin", "web-admin", "webadmin", "webmail", "webserver", "website", "wheel", "vww", "wvw", "wwv", "www", "www-data", "wwww"]

ACCOUNT_USERNAME_BLACKLIST = list(set(ACCOUNT_USERNAME_BLACKLIST))

# django-debug-toolbar
# ------------------------------------------------------------------------------
def show_toolbar(request):
    return request.user.is_authenticated and request.user.is_superuser
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": [
        # "debug_toolbar.panels.profiling.ProfilingPanel",  # additional one
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ],
    "SHOW_TEMPLATE_CONTEXT": True,
    'SHOW_TOOLBAR_CALLBACK': 'config.settings.base.show_toolbar',
}

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'template_profiler_panel.panels.template.TemplateProfilerPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

# Your stuff...
# ------------------------------------------------------------------------------
ENVIRONMENT_NAME = env.str("ENVIRONMENT_NAME", default="development")
ENVIRONMENT_COLOR = env.str("ENVIRONMENT_COLOR", default="black")

IS_BLACKOUT = env.bool('IS_BLACKOUT', default=False)  # TODO remove someday

Q_LOADER_BASE_PATH = env.str('Q_LOADER_BASE_PATH', default=None)
Q_LOADER_BASE_PATH = Path(Q_LOADER_BASE_PATH) if Q_LOADER_BASE_PATH is not None else Q_LOADER_BASE_PATH


GOOGLE_ANALYTICS_ID = env.str('GOOGLE_ANALYTICS_ID', default='')

# Django Silk
# SILKY_MIDDLEWARE_CLASS = 'path.to.your.middleware.MyCustomSilkyMiddleware'
SILKY_AUTHENTICATION = env.bool('SILKY_AUTHENTICATION', default=True)  # True  # User must login
SILKY_AUTHORISATION = env.bool('SILKY_AUTHORISATION', default=True)  # True  # User must have permissions
SILKY_PERMISSIONS = lambda user: user.is_superuser  # lambda user: user.is_staff  # Custom permissions
SILKY_META = env.bool('SILKY_META', default=True)  # True  # Record the request/response headers
SILKY_INTERCEPT_PERCENT = env.int('SILKY_INTERCEPT_PERCENT', default=100)  # 100  # Capture 100% of requests
SILKY_PYTHON_PROFILER = env.bool('SILKY_PYTHON_PROFILER', default=True)  # True  # Use Python's built-in cProfile

SILKY_MAX_REQUEST_BODY_SIZE = env.int('SILKY_MAX_REQUEST_BODY_SIZE', default=-1)  # -1  # Silk takes anything <0 as no limit
SILKY_MAX_RESPONSE_BODY_SIZE = env.int('SILKY_MAX_RESPONSE_BODY_SIZE', default=1024)  # 1024  # If response body>1024kb, ignore
SILKY_MAX_RECORDED_REQUESTS = env.int('SILKY_MAX_RECORDED_REQUESTS', default=None)  # 1000  # Keep only the last 1000 requests

SILKY_DYNAMIC_PROFILING = [
    {'module': 'questions.views', 'function': 'QuestionListView.get'},
    {'module': 'questions.views', 'function': 'question_set_first_question_view'},
    {'module': 'questions.views', 'function': 'CollegeBoardQuestionBankCategoryListView.get'},
    {'module': 'exams.views', 'function': 'ExamListView.get'},
]


LOGIN_HISTORY_GEOLOCATION_METHOD = env.str('LOGIN_HISTORY_GEOLOCATION_METHOD', default='')

DOC_PREFETCH_QUESTION = env.bool('DOC_PREFETCH_QUESTION', default=False)


# Constance
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
# CONSTANCE_DATABASE_CACHE_BACKEND = 'memory'
CONSTANCE_IGNORE_ADMIN_VERSION_CHECK = True
CONSTANCE_CONFIG = OrderedDict([
    ('DONATION_NOTICE_ENABLED', (False, 'Enable Donation Notice', bool)),
    ('DONATION_NOTICE_TEXT', ('', """""", str)),
    ('DONATION_TARGET', (0, 'Donation Target', int)),
    ('DONATION_AMOUNT', (0, 'Donation Amount', int)),

])

CONSTANCE_CONFIG_FIELDSETS = OrderedDict([
    ('Donation', {
        'fields': [
            'DONATION_NOTICE_ENABLED', 'DONATION_NOTICE_TEXT',
            'DONATION_AMOUNT', 'DONATION_TARGET',
        ],
        'collapse': True
    }),
])

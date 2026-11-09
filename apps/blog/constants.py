CATEGORY_NAME_MAX_LENGTH = 100
TAG_NAME_MAX_LENGTH = 50
POST_TITLE_MAX_LENGTH = 200
POST_STATUS_MAX_LENGTH = 10


# Seed command: defaults for the command-line arguments
DEFAULT_USERS = 20
DEFAULT_POSTS = 100
DEFAULT_COMMENTS = 500

# Seed command: users
SEED_PASSWORD = "SeedPass123!"
SEED_EMAIL_DOMAIN = "example.com"
INACTIVE_USER_RATIO = 0.15
STAFF_USER_RATIO = 0.10

# Seed command: posts
POST_SLUG_MAX_LENGTH = 50
SLUG_SUFFIX_START = 2
TITLE_WORD_COUNT = 6
MIN_POST_PARAGRAPHS = 3
MAX_POST_PARAGRAPHS = 6
PUBLISHED_POST_RATIO = 0.70
NO_CATEGORY_POST_RATIO = 0.10
MIN_TAGS_PER_POST = 0
MAX_TAGS_PER_POST = 5

# Seed command: comments
MIN_COMMENT_SENTENCES = 1
MAX_COMMENT_SENTENCES = 3

# Seed command: database and output
BULK_BATCH_SIZE = 500
SUMMARY_LABEL_WIDTH = 11
SUMMARY_COUNT_WIDTH = 4
SUMMARY_TIME_DECIMALS = 2

CATEGORY_NAMES = [
    "Python",
    "Django",
    "DevOps",
    "Databases",
    "Frontend",
    "Testing",
    "Security",
    "Career",
]

TAG_NAMES = [
    "Tutorial",
    "Beginner",
    "Advanced",
    "Tips",
    "Best Practices",
    "REST API",
    "Docker",
    "Git",
    "PostgreSQL",
    "Redis",
    "Celery",
    "Linux",
    "CI/CD",
    "Performance",
    "Debugging",
    "Deployment",
    "Authentication",
    "Open Source",
    "Productivity",
    "Architecture",
]


# Admin: environment badge (BLOG_ENV_ID decides which one is shown)
ENV_ID_PROD = "prod"
ENV_LABEL_LOCAL = "Local"
ENV_LABEL_PROD = "Production"
ENV_TYPE_LOCAL = "warning"  # orange
ENV_TYPE_PROD = "danger"  # red

# Admin: URL names and query strings
POST_CHANGELIST_URL_NAME = "admin:blog_post_changelist"
POST_STATUS_FILTER_PARAM = "status__exact"

# Post status values (used by the model and by the admin tab links)
POST_STATUS_DRAFT = "draft"
POST_STATUS_PUBLISHED = "published"

# Admin: Category and Tag
POSTS_SECTION_HEIGHT = 300
POSTS_COUNT_DESCRIPTION = "Posts"

# Admin: Comment
COMMENT_BODY_PREVIEW_LENGTH = 60

# Admin: label colors (Unfold label types)
LABEL_SUCCESS = "success"
LABEL_WARNING = "warning"
LABEL_DANGER = "danger"
LABEL_INFO = "info"
LABEL_NEUTRAL = "default"

# Admin: users
USER_ACTIVE_TEXT = "Active"
USER_INACTIVE_TEXT = "Inactive"
USER_STAFF_TEXT = "Staff"
USER_REGULAR_TEXT = "Regular"
USERS_ACTIVATED_MESSAGE = "{count} user(s) activated."
USERS_DEACTIVATED_MESSAGE = "{count} user(s) deactivated. Your own account was skipped."

# Admin: posts
TAGS_DROPDOWN_HEIGHT = 200
COMMENTS_INLINE_PER_PAGE = 10
COMMENT_LIST_URL_NAME = "admin:blog_comment_changelist"
COMMENT_POST_FILTER_PARAM = "post__id__exact"
POSTS_PUBLISHED_MESSAGE = "{count} post(s) published."
POSTS_MOVED_TO_DRAFTS_MESSAGE = "{count} post(s) moved to drafts."
POST_PUBLISHED_MESSAGE = "Post '{title}' is now published."
POST_UNPUBLISHED_MESSAGE = "Post '{title}' is now a draft."

# Dashboard
DASHBOARD_TOP_AUTHORS_LIMIT = 5
DASHBOARD_CHART_HEIGHT = 320
DASHBOARD_CHART_COLOR = "var(--color-primary-600)"
PERCENT_TOTAL = 100
PERCENT_DECIMALS = 1
POSTS_COMMENT_SECTION_TITLE = "Comments on this post"
USER_LIST_URL_NAME = "admin:auths_user_changelist"

import os
import sys
from pathlib import Path

from decouple import Config, RepositoryEnv

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / "settings" / ".env"
ENV_ID_KEY = "BLOG_ENV_ID"
DEFAULT_ENV_ID = "local"
SETTINGS_MODULE_TEMPLATE = "settings.env.{env_id}"


def main() -> None:
    env_config = Config(RepositoryEnv(str(ENV_FILE)))
    env_id = env_config(ENV_ID_KEY, default=DEFAULT_ENV_ID)
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        SETTINGS_MODULE_TEMPLATE.format(env_id=env_id),
    )
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Could not import Django. Is your virtual environment activated?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
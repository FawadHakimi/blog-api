from decouple import config, Csv
ENV_ID: str = config("BLOG_ENV_ID", default="local")
SECRET_KEY: str = config("BLOG_SECRET_KEY")

ALLOWED_HOSTS: list[str] = config("BLOG_ALLOWED_HOSTS", default="", cast=Csv())

DB_NAME: str = config("BLOG_DB_NAME", default="blog")
DB_USER: str = config("BLOG_DB_USER", default="postgres")
DB_PASSWORD: str = config("BLOG_DB_PASSWORD", default="")
DB_HOST: str = config("BLOG_DB_HOST", default="localhost")
DB_PORT: str = config("BLOG_DB_PORT", default="5432")
from datetime import timedelta
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import connection
from django.db.models import Count, Model, QuerySet
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from django.utils.text import slugify

from apps.auths.models import User
from apps.blog.constants import (
    CATEGORY_NAMES,
    MUTATING_QUERIES,
    PREVIEW_ROWS,
    SEED_EMAIL_DOMAIN,
    TAG_NAMES,
)
from apps.blog.models import Post
from apps.blog.queries import QUERIES

UNKNOWN_QUERY_ERROR = "Query #{number} does not exist. Available numbers: {available}."
INDENT = "  "

# Sample values for the queries that take arguments.
SAMPLE_PAGE = 2
SAMPLE_TITLE_WORD = "a"
SAMPLE_SLUG_COUNT = 2
SAMPLE_DAYS = 30
TAG_PAIR_SIZE = 2
SAMPLE_MIN_POSTS = 10


def two_tags_of_one_post() -> dict[str, str]:
    """Return slugs of two tags that belong to the same post, so query 21 has a result."""
    post = (
        Post.objects.annotate(tag_count=Count("tags"))
        .filter(tag_count__gte=TAG_PAIR_SIZE)
        .first()
    )
    if post is None:
        return {"first_slug": "", "second_slug": ""}
    first, second = post.tags.values_list("slug", flat=True)[:TAG_PAIR_SIZE]
    return {"first_slug": first, "second_slug": second}


def build_sample_arguments() -> dict[int, dict[str, Any]]:
    """Return sample arguments for the queries that take parameters: {number: {name: value}}."""
    now = timezone.now()
    today = timezone.localdate()
    author_email = (
        User.objects.filter(posts__status=Post.Status.PUBLISHED)
        .values_list("email", flat=True)
        .first()
    )
    return {
        4: {"slug": Post.objects.values_list("slug", flat=True).first()},
        7: {"page": SAMPLE_PAGE},
        8: {"word": SAMPLE_TITLE_WORD},
        9: {"domain": SEED_EMAIL_DOMAIN},
        11: {"slugs": [slugify(name) for name in CATEGORY_NAMES[:SAMPLE_SLUG_COUNT]]},
        12: {"year": now.year, "month": now.month},
        13: {"days": SAMPLE_DAYS},
        14: {"start": today - timedelta(days=SAMPLE_DAYS), "end": today},
        15: {"email": author_email},
        16: {"tag_slug": slugify(TAG_NAMES[0])},
        17: {"category_slug": slugify(CATEGORY_NAMES[0])},
        21: two_tags_of_one_post(),
        22: {"text": SAMPLE_TITLE_WORD},
        34: {"min_posts": SAMPLE_MIN_POSTS},
    }


class Command(BaseCommand):
    help = "Run the ORM queries and show the result and the number of SQL queries."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--number", type=int, help="Run only the query with this number")
        parser.add_argument("--sql", action="store_true", help="Also print the SQL text")

    def handle(self, *args: Any, **options: Any) -> None:
        number: int | None = options["number"]
        show_sql: bool = options["sql"]

        if number is not None:
            if number not in QUERIES:
                available = ", ".join(str(key) for key in sorted(QUERIES))
                raise CommandError(UNKNOWN_QUERY_ERROR.format(number=number, available=available))
            numbers = [number]
        else:
            numbers = [key for key in sorted(QUERIES) if key not in MUTATING_QUERIES]

        sample_arguments = build_sample_arguments()
        for query_number in numbers:
            self._run_query(query_number, show_sql, sample_arguments)

    def _run_query(
        self, number: int, show_sql: bool, sample_arguments: dict[int, dict[str, Any]]
    ) -> None:
        function = QUERIES[number]
        arguments = sample_arguments.get(number, {})
        annotation_names: list[str] = []

        with CaptureQueriesContext(connection) as context:
            result = function(**arguments)
            if isinstance(result, QuerySet):
                annotation_names = list(result.query.annotations)
                result = list(result)  # a QuerySet is lazy: this line sends the SQL

        sql_count = len(context.captured_queries)
        noun = "query" if sql_count == 1 else "queries"
        self.stdout.write(f"#{number} {function.__name__} — {sql_count} SQL {noun}")
        if show_sql:
            for captured in context.captured_queries:
                self.stdout.write(captured["sql"])
        self._print_result(result, annotation_names)

    def _print_result(self, result: Any, annotation_names: list[str]) -> None:
        if not isinstance(result, list):
            self.stdout.write(f"{INDENT}{result}")
            return
        for row in result[:PREVIEW_ROWS]:
            self.stdout.write(f"{INDENT}{self._format_row(row, annotation_names)}")
        self.stdout.write(f"{INDENT}({len(result)} rows)")

    def _format_row(self, row: Any, annotation_names: list[str]) -> str:
        if isinstance(row, Model) and annotation_names:
            values = {name: getattr(row, name) for name in annotation_names}
            return f"{row} {values}"
        return str(row)

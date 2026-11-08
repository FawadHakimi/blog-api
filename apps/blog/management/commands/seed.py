import random
import time
from typing import Any

from faker import Faker

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import transaction
from django.utils.text import slugify

from apps.blog.constants import (
    BULK_BATCH_SIZE,
    CATEGORY_NAMES,
    DEFAULT_COMMENTS,
    DEFAULT_POSTS,
    DEFAULT_USERS,
    INACTIVE_USER_RATIO,
    MAX_COMMENT_SENTENCES,
    MAX_POST_PARAGRAPHS,
    MAX_TAGS_PER_POST,
    MIN_COMMENT_SENTENCES,
    MIN_POST_PARAGRAPHS,
    MIN_TAGS_PER_POST,
    NO_CATEGORY_POST_RATIO,
    POST_SLUG_MAX_LENGTH,
    PUBLISHED_POST_RATIO,
    SEED_EMAIL_DOMAIN,
    SEED_PASSWORD,
    SLUG_SUFFIX_START,
    STAFF_USER_RATIO,
    SUMMARY_COUNT_WIDTH,
    SUMMARY_LABEL_WIDTH,
    SUMMARY_TIME_DECIMALS,
    TAG_NAMES,
    TITLE_WORD_COUNT,
)
from apps.blog.models import Category, Comment, Post, Tag

User = get_user_model()

PARAGRAPH_SEPARATOR = "\n\n"
NEGATIVE_NUMBER_ERROR = "--{name} cannot be negative (got {value})."
NO_USERS_ERROR = "There are no users in the database. Add some with --users N."
NO_PUBLISHED_POSTS_ERROR = "There are no published posts in the database. Add some with --posts N."


def make_unique_slug(title: str, used_slugs: set[str]) -> str:
    """Return a slug for the title that is not in used_slugs: my-post, my-post-2, ..."""
    base = slugify(title)[:POST_SLUG_MAX_LENGTH]
    slug = base
    counter = SLUG_SUFFIX_START
    while slug in used_slugs:
        suffix = f"-{counter}"
        slug = f"{base[: POST_SLUG_MAX_LENGTH - len(suffix)]}{suffix}"
        counter += 1
    return slug


def make_unique_email(first_name: str, last_name: str, used_emails: set[str]) -> str:
    """Return an email built from the names that is not in used_emails."""
    local_part = slugify(f"{first_name} {last_name}").replace("-", ".")
    email = f"{local_part}@{SEED_EMAIL_DOMAIN}"
    counter = SLUG_SUFFIX_START
    while email in used_emails:
        email = f"{local_part}{counter}@{SEED_EMAIL_DOMAIN}"
        counter += 1
    return email


class Command(BaseCommand):
    help = "Fill the database with fake data."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--users", type=int, default=DEFAULT_USERS, help="Number of users to create"
        )
        parser.add_argument(
            "--posts", type=int, default=DEFAULT_POSTS, help="Number of posts to create"
        )
        parser.add_argument(
            "--comments", type=int, default=DEFAULT_COMMENTS, help="Number of comments to create"
        )
        parser.add_argument(
            "--clear", action="store_true", help="Delete existing data before seeding"
        )

    def handle(self, *args: Any, **options: Any) -> None:
        started_at = time.perf_counter()
        users_count: int = options["users"]
        posts_count: int = options["posts"]
        comments_count: int = options["comments"]
        clear: bool = options["clear"]

        self._validate_not_negative(
            users=users_count, posts=posts_count, comments=comments_count
        )

        fake = Faker()
        # One transaction: if anything fails, nothing is saved (and nothing is cleared).
        with transaction.atomic():
            if clear:
                self._clear_data()
            created = {
                "Users": self._create_users(fake, users_count),
                "Categories": self._create_named(Category, CATEGORY_NAMES),
                "Tags": self._create_named(Tag, TAG_NAMES),
                "Posts": self._create_posts(fake, posts_count),
                "Comments": self._create_comments(fake, comments_count),
            }

        elapsed = time.perf_counter() - started_at
        self._print_summary(created, elapsed)

    def _validate_not_negative(self, **counts: int) -> None:
        for name, value in counts.items():
            if value < 0:
                raise CommandError(NEGATIVE_NUMBER_ERROR.format(name=name, value=value))

    def _clear_data(self) -> None:
        Comment.objects.all().delete()
        Post.objects.all().delete()
        Tag.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write("Old data deleted (superusers were kept).")

    def _create_users(self, fake: Faker, count: int) -> int:
        if count == 0:
            return 0
        used_emails = set(User.objects.values_list("email", flat=True))
        # Hash the password ONCE: hashing is slow on purpose.
        hashed_password = make_password(SEED_PASSWORD)
        users = []
        for _ in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = make_unique_email(first_name, last_name, used_emails)
            used_emails.add(email)
            users.append(
                User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=hashed_password,
                    is_active=random.random() >= INACTIVE_USER_RATIO,
                    is_staff=random.random() < STAFF_USER_RATIO,
                )
            )
        User.objects.bulk_create(users, batch_size=BULK_BATCH_SIZE)
        return len(users)

    def _create_named(self, model: type[Category] | type[Tag], names: list[str]) -> int:
        """Create categories or tags from a list of names. Existing ones are skipped."""
        used_names = set(model.objects.values_list("name", flat=True))
        used_slugs = set(model.objects.values_list("slug", flat=True))
        new_items = []
        for name in names:
            slug = slugify(name)
            if name in used_names or slug in used_slugs:
                continue
            new_items.append(model(name=name, slug=slug))
        model.objects.bulk_create(new_items)
        return len(new_items)

    def _create_posts(self, fake: Faker, count: int) -> int:
        if count == 0:
            return 0
        user_ids = list(User.objects.values_list("id", flat=True))
        if not user_ids:
            raise CommandError(NO_USERS_ERROR)
        categories = list(Category.objects.all())
        tags = list(Tag.objects.all())
        used_slugs = set(Post.objects.values_list("slug", flat=True))

        posts = []
        for _ in range(count):
            title = fake.sentence(nb_words=TITLE_WORD_COUNT).rstrip(".")
            slug = make_unique_slug(title, used_slugs)
            used_slugs.add(slug)
            paragraphs = fake.paragraphs(
                nb=random.randint(MIN_POST_PARAGRAPHS, MAX_POST_PARAGRAPHS)
            )
            is_published = random.random() < PUBLISHED_POST_RATIO
            has_no_category = random.random() < NO_CATEGORY_POST_RATIO
            posts.append(
                Post(
                    author_id=random.choice(user_ids),
                    title=title,
                    slug=slug,
                    body=PARAGRAPH_SEPARATOR.join(paragraphs),
                    category=None if has_no_category else random.choice(categories),
                    status=Post.Status.PUBLISHED if is_published else Post.Status.DRAFT,
                )
            )
        Post.objects.bulk_create(posts, batch_size=BULK_BATCH_SIZE)

        # bulk_create does not save many-to-many links, so tags are attached one post at a time.
        max_tags = min(MAX_TAGS_PER_POST, len(tags))
        for post in posts:
            post.tags.set(random.sample(tags, random.randint(MIN_TAGS_PER_POST, max_tags)))
        return len(posts)

    def _create_comments(self, fake: Faker, count: int) -> int:
        if count == 0:
            return 0
        user_ids = list(User.objects.values_list("id", flat=True))
        if not user_ids:
            raise CommandError(NO_USERS_ERROR)
        post_ids = list(
            Post.objects.filter(status=Post.Status.PUBLISHED).values_list("id", flat=True)
        )
        if not post_ids:
            raise CommandError(NO_PUBLISHED_POSTS_ERROR)

        comments = [
            Comment(
                post_id=random.choice(post_ids),
                author_id=random.choice(user_ids),
                body=" ".join(
                    fake.sentences(
                        nb=random.randint(MIN_COMMENT_SENTENCES, MAX_COMMENT_SENTENCES)
                    )
                ),
            )
            for _ in range(count)
        ]
        Comment.objects.bulk_create(comments, batch_size=BULK_BATCH_SIZE)
        return len(comments)

    def _print_summary(self, created: dict[str, int], elapsed: float) -> None:
        for name, number in created.items():
            label = f"{name}:"
            self.stdout.write(
                f"{label:<{SUMMARY_LABEL_WIDTH}}{number:>{SUMMARY_COUNT_WIDTH}} created"
            )
        seconds = f"{elapsed:.{SUMMARY_TIME_DECIMALS}f}"
        self.stdout.write(self.style.SUCCESS(f"Done in {seconds} seconds"))

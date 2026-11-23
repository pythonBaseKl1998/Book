from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["name"]
        verbose_name = "жанр"
        verbose_name_plural = "жанры"

    def __str__(self):
        return self.name


class Author(models.Model):
    last_name = models.CharField(max_length=100, db_index=True, blank=True)
    given_name = models.CharField(max_length=100, db_index=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True, default="")
    # photo = models.ImageField(upload_to="authors/", null=True, blank=True)
    slug = models.SlugField(max_length=150, unique=True)

    class Meta:
        ordering = ["last_name", "given_name", "date_of_birth"]
        verbose_name = "автор"
        verbose_name_plural = "авторы"
        indexes = [
            models.Index(fields=["last_name", "given_name"]),
        ]

    def __str__(self):
        full_name = ", ".join(
            part for part in [self.last_name, self.given_name] if part
        ) or "Неизвестный автор"

        if self.date_of_birth and self.date_of_death:
            lifespan = f" ({self.date_of_birth.year}–{self.date_of_death.year})"
        elif self.date_of_birth:
            lifespan = f" (род. {self.date_of_birth.year})"
        elif self.date_of_death:
            lifespan = f" (ум. {self.date_of_death.year})"
        else:
            lifespan = ""

        return f"{full_name}{lifespan}"

    @property
    def full_name(self):
        return f"{self.last_name} {self.given_name}".strip()


class Book(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    subtitle = models.CharField(max_length=200, blank=True, default="")
    authors = models.ManyToManyField(
        Author, related_name="books", verbose_name="авторы"
    )
    description = models.TextField(max_length=1000, blank=True, default="")
    pub_year = models.PositiveSmallIntegerField(
        "год публикации",
        null=True,
        blank=True,
        validators=[MaxValueValidator(timezone.now().year)],
    )
    genres = models.ManyToManyField(
        Genre, related_name="books", verbose_name="жанры", blank=True
    )
    isbn = models.CharField(max_length=13, blank=True, default="", db_index=True)
    page_count = models.PositiveIntegerField(null=True, blank=True)
    # cover = models.ImageField(upload_to="covers/", null=True, blank=True)
    slug = models.SlugField(max_length=250, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "книга"
        verbose_name_plural = "книги"
        indexes = [
            models.Index(fields=["title", "pub_year"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(pub_year__isnull=True) | models.Q(pub_year__lte=timezone.now().year),
                name="book_pub_year_not_future",
            ),
        ]

    @property
    def verbose_title(self):
        subtitle = f": {self.subtitle}" if self.subtitle else ""
        pub_year = f" ({self.pub_year})" if self.pub_year else ""
        return f"{self.title}{subtitle}{pub_year}"

    def __str__(self):
        return self.verbose_title

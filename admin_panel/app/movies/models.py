import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Modified"), auto_now_add=True)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.TextField(_("Title"), blank=False, unique=True)
    description = models.TextField(_("Description"), blank=True)

    class Meta:
        db_table = 'content"."genre'
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")

    def __str__(self):
        return self.name


class GenreFilmWork(UUIDMixin):
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE)
    film_work = models.ForeignKey("FilmWork", on_delete=models.CASCADE)
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        db_table = 'content"."genre_film_work'
        constraints = [
            models.UniqueConstraint(
                name="genre_film_work_idx", fields=["genre_id", "film_work_id"]
            )
        ]


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.TextField(_("Full name"), blank=False)

    class Meta:
        db_table = 'content"."person'
        verbose_name = _("Actor")
        verbose_name_plural = _("Actors")

    def __str__(self):
        return self.full_name


class PersonFilmWork(UUIDMixin):
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    film_work = models.ForeignKey("FilmWork", on_delete=models.CASCADE)
    role = models.TextField(_("Role"), blank=False)
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        db_table = 'content"."person_film_work'
        constraints = [
            models.UniqueConstraint(
                name="person_film_work_role_idx",
                fields=["person_id", "film_work_id", "role"],
            )
        ]


class FilmWork(UUIDMixin, TimeStampedMixin):
    TYPE_CHOICES = [
        ("movie", _("Movie")),
        ("tv show", _("TV Show")),
    ]

    title = models.TextField(_("Title"), blank=False)
    description = models.TextField(_("Description"), blank=True)
    creation_date = models.DateField(_("Creation date"), blank=True, null=True)
    rating = models.FloatField(
        _("Rating"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank=True,
    )
    type = models.CharField(
        _("Type"),
        max_length=10,
        choices=TYPE_CHOICES,
        default=TYPE_CHOICES[0],
        blank=False,
    )
    genres = models.ManyToManyField(Genre, through="GenreFilmWork")
    persons = models.ManyToManyField(Person, through="PersonFilmWork")
    file_path = models.FileField(_("file"), blank=True, null=True, upload_to="movies/")

    class Meta:
        db_table = 'content"."film_work'
        verbose_name = _("Film")
        verbose_name_plural = _("Films")
        indexes = [
            models.Index(
                name="film_work_creat_dat_ratin_idx", fields=["creation_date", "rating"]
            )
        ]

    def __str__(self):
        return self.title

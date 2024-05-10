import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
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
    subscribers_only = models.BooleanField(
        "Only for subscribers", default=True
    )
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
    file_path = models.FileField(
        _("file"), blank=True, null=True, upload_to="movies/"
    )

    class Meta:
        db_table = 'content"."film_work'
        verbose_name = _("Film")
        verbose_name_plural = _("Films")
        indexes = [
            models.Index(
                name="film_work_creat_dat_ratin_idx",
                fields=["creation_date", "rating"],
            )
        ]

    def __str__(self):
        return self.title


class MyUserManager(BaseUserManager):
    def create_user(self, login, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not login:
            raise ValueError("Users must have a login")

        user = self.model(login=login, email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, email=None, password=None):
        if not email:
            email = "superuser@superuser.com"
        user = self.create_user(login, email, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    login = models.TextField("login", max_length=50, unique=True)
    email = models.EmailField(
        verbose_name="email address", max_length=255, unique=True
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    USERNAME_FIELD = "login"
    objects = MyUserManager()

    def __str__(self):
        return f"{self.login} {self.id}"

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

import uuid

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork


class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork


class GenreFilter(admin.SimpleListFilter):
    title = _("Genre")
    parameter_name = "genre"

    def lookups(self, request, model_admin):
        fields = []
        for genre in Genre.objects.all():
            fields.append((genre.id, genre.name))
        return fields

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(genrefilmwork__genre=uuid.UUID(self.value()))


class RatingFilter(admin.SimpleListFilter):
    title = _("Rating")
    parameter_name = "rating"

    def lookups(self, request, model_admin):
        filter_values = []
        for r in range(0, 10, 1):
            filter_values.append((r, (str(r) + "-" + str(r + 1))))
        return filter_values[::-1]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        min_value = float(self.value())  # type: ignore
        max_value = min_value + 0.9
        if max_value == 9.9:
            max_value = 10
        return queryset.filter(rating__range=(min_value, max_value))


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = (
        "name",
        "id",
    )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = [
        PersonFilmWorkInline,
    ]
    list_filter = [
        ("personfilmwork__role"),
    ]
    search_fields = (
        "full_name",
        "id",
    )


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    inlines = (
        GenreFilmWorkInline,
        PersonFilmWorkInline,
    )
    list_display = (
        "title",
        "type",
        "subscribers_only",
        "creation_date",
        "rating",
    )
    list_filter = (
        "subscribers_only",
        "type",
        RatingFilter,
        GenreFilter,
        "creation_date",
    )
    search_fields = (
        "title",
        "description",
        "id",
    )

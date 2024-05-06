from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from django.http import JsonResponse
from django.db.models.query import QuerySet
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q

from movies.models import FilmWork


class MoviesApiMixin:
    model = FilmWork
    ordering = "title"
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('genres', 'persons').all()
        return queryset

    def context_list_insert(self, objects: QuerySet) -> QuerySet:
        return (
            objects.values(
                "id",
                "title",
                "description",
                "creation_date",
                "rating",
                "type",
            )
            .annotate(genres=ArrayAgg("genres__name", distinct=True))
            .annotate(
                actors=ArrayAgg(
                    "persons__full_name",
                    filter=Q(personfilmwork__role="actor"),
                    distinct=True,
                )
            )
            .annotate(
                directors=ArrayAgg(
                    "persons__full_name",
                    filter=Q(personfilmwork__role="director"),
                    distinct=True,
                )
            )
            .annotate(
                writers=ArrayAgg(
                    "persons__full_name",
                    filter=Q(personfilmwork__role="writer"),
                    distinct=True,
                )
            )
        )  # type: ignore

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(
                queryset, page_size
            )
            context = {
                "count": paginator.count,
                "total_pages": paginator.num_pages,
                "prev": page.previous_page_number() if page.has_previous() else None,
                "next": page.next_page_number() if page.has_next() else None,
                "results": list(self.context_list_insert(page.object_list)),
            }
        return context

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get_context_data(self, **kwargs):
        return self.context_list_insert(self.model.objects.filter(id=kwargs['object'].id))[0]

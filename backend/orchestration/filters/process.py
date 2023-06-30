from django.db.models import Q
from django_filters import rest_framework as filters
from orchestration.models import Process


class ProcessFilter(filters.FilterSet):
    owner__or = filters.CharFilter(method="filter_user")
    owner = filters.CharFilter(method="filter_user")
    name__or = filters.CharFilter(method="filter_name")
    name = filters.CharFilter(method="filter_name")
    pipeline_name__or = filters.CharFilter(method="filter_pipeline_name")
    pipeline_name = filters.CharFilter(method="filter_pipeline_name")

    class Meta:
        model = Process
        fields = ["pipeline_name", "name", "owner"]

    def filter_user(self, queryset, name, value):
        query = self.format_query_to_char(
            name, value, ["user__username", "user__first_name", "user__last_name"]
        )

        return queryset.filter(query)

    def filter_name(self, queryset, name, value):
        query = self.format_query_to_char(name, value, ["name"])

        return queryset.filter(query)

    def filter_pipeline_name(self, queryset, name, value):
        query = self.format_query_to_char(name, value, ["pipeline_name"])

        return queryset.filter(query)

    @staticmethod
    def format_query_to_char(key, value, fields):
        condition = Q.OR if key.endswith("__or") else Q.AND
        values = value.split(",")
        query = Q()

        for value in values:
            subfilter = Q()
            for field in fields:
                subfilter.add(Q(**{f"{field}__icontains": value}), Q.OR)

            query.add(subfilter, condition)

        return query

from core.models import Pipeline, Process
from core.serializers import ProcessSerializer
from core.utils import format_query_to_char
from core.views.create_product import CreateProduct
from django_filters import rest_framework as filters
from rest_framework import exceptions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class ProcessFilter(filters.FilterSet):
    release__isnull = filters.BooleanFilter(
        field_name="release", lookup_expr="isnull")
    pipeline__or = filters.CharFilter(method="filter_type_name")
    pipeline = filters.CharFilter(method="filter_type_name")
    release_name__or = filters.CharFilter(method="filter_release")
    release_name = filters.CharFilter(method="filter_release")

    class Meta:
        model = Process
        fields = [
            "pipeline",
            "status",
            "release",
            "user",
        ]

    def filter_user(self, queryset, name, value):
        query = format_query_to_char(
            name, value, 
            ["user__username", "user__first_name", "user__last_name"]
        )

        return queryset.filter(query)

    def filter_pipeline(self, queryset, name, value):
        query = format_query_to_char(
            name, value,
            ["pipeline__display_name", "pipeline__name"]
        )

        return queryset.filter(query)

    def filter_release(self, queryset, name, value):
        query = format_query_to_char(
            name, value, ["release__display_name"])
        return queryset.filter(query)


class ProcessViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    search_fields = [
        "pipeline_name",
        "pipeline_display_name",
        "user__username",
        "user__first_name",
        "user__last_name",
    ]
    filterset_class = ProcessFilter
    ordering_fields = [
        "id",
        "created_at",
    ]
    ordering = ["-created_at"]

    def create(self, request):
        print("USER: ", request.user)
        print("PROCESS: ", request.data)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            instance = self.perform_create(serializer)

            print("INSTANCE: ", instance)
            print("INSTANCE type: ", type(instance))

            process = Process.objects.get(pk=instance.pk)
            process.save()

            data = self.get_serializer(instance=process).data
            return Response(data, status=status.HTTP_201_CREATED)

        except Exception as e:
            content = {"error": str(e)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        """Add user and upload"""

        owned_by = self.request.user
        upload = self.create_initial_upload(serializer, owned_by)
        return serializer.save(user=owned_by, upload=upload)

    def create_initial_upload(self, serializer, user):
        """_summary_"""
        data = serializer.initial_data
        pipeline = Pipeline.objects.get(pk=data.get('pipeline'))
        upload_data = {
            "display_name": data.get("display_name"),
            "release": data.get("release", None),
            "pz_code": data.get("pz_code", None),
            "official_product": data.get("official_product", False),
            "description": data.get("description", None),
            "product_type": pipeline.output_product_type.pk,
        }
        product = CreateProduct(upload_data, user)
        check_prodtype = product.check_product_types()

        if not check_prodtype.get("success"):
            raise ValueError(check_prodtype.get("message"))

        product.save()
        return product.data

    @action(methods=["GET"], detail=True)
    def api_schema(self, request):
        meta = self.metadata_class()
        data = meta.determine_metadata(request, self)
        return Response(data)

    def destroy(self, request, pk=None, *args, **kwargs):
        """Product can only be deleted by the OWNER or if the user 
        has an admin profile.
        """

        instance = self.get_object()
        if instance.can_delete(self.request.user):
            return super(ProcessViewSet, self).destroy(request, pk, *args, **kwargs)
        else:
            raise exceptions.PermissionDenied()
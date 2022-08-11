import os

from core.models import ProductFile
from core.serializers import ProductFileSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response


class ProductFileViewSet(viewsets.ModelViewSet):
    queryset = ProductFile.objects.all()
    serializer_class = ProductFileSerializer
    filter_fields = ("id", "product_id")
    ordering_fields = ["id", "role"]
    ordering = ["id"]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)

        try:
            # TODO: Validar o arquivo enviado aplicar regras de negocio e retornar mensagens de erro
            error = False
            msg = "Mensagem de erro do arquivo"
            if error:
                # Neste ponto o arquivo já foi feito o upload
                # Remover o arquivo enviado e excluir o model
                instance.delete()
                return Response({"error": str(msg)}, status=status.HTTP_400_BAD_REQUEST)

            data = self.get_serializer(instance=instance).data
            return Response(data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Neste ponto o arquivo já foi feito o upload
            # Remover o arquivo enviado e excluir o model
            instance.delete()
            content = {"error": str(e)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        """Adiciona size, name, extension."""

        file = self.request.data.get("file")
        size = file.size
        filename, extension = os.path.splitext(file.name)

        return serializer.save(
            size=size,
            name=file.name,
            extension=extension,
        )

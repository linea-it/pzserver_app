from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import ProductContent
from django.views.decorators.csrf import csrf_exempt

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def update_aliases(request):
    data = request.data
    product_id = data.get('productId')
    updates = data.get('updates', [])

    try:
        product_contents = ProductContent.objects.filter(product_id=product_id)
        for update in updates:
            content_id = update.get('id')
            alias = update.get('alias')
            if content_id and alias:
                content = product_contents.get(pk=content_id)
                content.alias = alias
                content.save()

        return Response({'message': 'Aliases updated successfully.'})
    except ProductContent.DoesNotExist:
        return Response({'error': 'Product not found.'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

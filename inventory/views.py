from .models import  Branch,Stock,Product,StockTransfer
from .serializers import BranchSerializer,ProductSerializer,StockSerializer,StockTransferSerializer,BranchStockSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.permissions import IsAdminOrManager
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from rest_framework.generics import ListAPIView


class AddBranchView(APIView):

    permission_classes = [IsAdminOrManager]
    def post(self,request):
        serializer = BranchSerializer(data=request.data)
        # print(request.data,serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AddProductView(APIView):

    permission_classes = [IsAdminOrManager]
    def post(self,request):
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddStockView(APIView):

    permission_classes = [IsAdminOrManager]
    def post(self,request):
        
        branch_id = request.data.get('branch')
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 0))

        if quantity <= 0:
            return Response({"error": "Quantity must be > 0"}, status=400)

        try:
            stock, created = Stock.objects.get_or_create(
                branch_id=branch_id,
                product_id=product_id,
                defaults={
                    'quantity': 0,
                    'reserved_quantity': 0
                }
            )
            stock.quantity += quantity
            stock.save()
            return Response({
                "message": "Stock added successfully",
                "data": StockSerializer(stock).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class BranchStockView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            branch = Branch.objects.get(id=pk)
        except Branch.DoesNotExist:
            return Response({"error": "Branch not found"}, status=status.HTTP_404_BAD_REQUEST)

        stocks = Stock.objects.filter(branch=branch).select_related('product')

        serializer = BranchStockSerializer(stocks, many=True)

        return Response({
            "branch": branch.name,
            "total_products": stocks.count(),
            "data": serializer.data
        })
    
class CreateStockTransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StockTransferSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        from_branch = data['from_branch']
        to_branch = data['to_branch']
        product = data['product']
        quantity = data['quantity']

        if from_branch == to_branch:
            return Response({"error": "Cannot transfer within same branch"}, status=status.HTTP_400_BAD_REQUEST)

        if quantity <= 0:
            return Response({"error": "Quantity must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            stock = Stock.objects.get(branch=from_branch, product=product)
        except Stock.DoesNotExist:
            return Response({"error": "Stock not found"}, status = status.HTTP_404_NOT_FOUND)

        if stock.available_quantity < quantity:
            return Response({"error": "Insufficient stock"}, status = status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            
            stock.reserved_quantity += quantity
            stock.save()

            serializer.save(
                requested_by=request.user,
                status='PENDING'
            )

        return Response({
            "message": "Transfer created",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

class ApproveTransferView(APIView):
    permission_classes = [IsAdminOrManager]

    def post(self, request, pk):
        try:
            transfer = StockTransfer.objects.get(transfer_id=pk)
        except StockTransfer.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        if transfer.status != 'PENDING':
            return Response({"error": "Only pending transfers allowed"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            from_stock = Stock.objects.get(branch=transfer.from_branch,product=transfer.product)
            to_stock = Stock.objects.get(branch=transfer.to_branch,product = transfer.product)

            from_stock.quantity -= transfer.quantity
            from_stock.reserved_quantity -= transfer.quantity
            from_stock.save()

            to_stock.quantity += transfer.quantity
            to_stock.save()
            
            transfer.status = 'COMPLETED'
            transfer.approved_by = request.user
            transfer.completed_at = timezone.now()
            transfer.save()

        return Response({"message": "Transfer approved"})

class StockTransferListView(ListAPIView):
    serializer_class = StockTransferSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = StockTransfer.objects.all().order_by('-requested_at')

        
        status      = self.request.query_params.get('status')
        from_branch = self.request.query_params.get('from_branch')
        to_branch   = self.request.query_params.get('to_branch')
        product     = self.request.query_params.get('product')
        requested_by = self.request.query_params.get('requested_by')
        start_date  = self.request.query_params.get('start_date')
        end_date    = self.request.query_params.get('end_date')

        if status:
            queryset = queryset.filter(status=status)

        if from_branch:
            queryset = queryset.filter(from_branch_id=from_branch)

        if to_branch:
            queryset = queryset.filter(to_branch_id=to_branch)

        if product:
            queryset = queryset.filter(product_id=product)

        if requested_by:
            queryset = queryset.filter(requested_by_id=requested_by)

        if start_date and end_date:
            queryset = queryset.filter(
                requested_at__date__range=[start_date, end_date]
            )

        return queryset

class CancelTransferView(APIView):
    permission_classes = [IsAdminOrManager]

    def post(self, request, pk):
        try:
            transfer = StockTransfer.objects.get(transfer_id=pk)
        except StockTransfer.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        if transfer.status != 'PENDING':
            return Response({"error": "Only pending transfers allowed"}, status=status.HTTP_400_BAD_REQUEST)

        stock = Stock.objects.get_or_create(
            branch=transfer.from_branch,
            product=transfer.product,
            defaults={"quantity":0,"reserved_quantity":0}
        )

        with transaction.atomic():
            stock.reserved_quantity -= transfer.quantity
            stock.save()
            
            transfer.status = 'CANCELLED'
            transfer.cancelled_by = request.user
            transfer.save()

        return Response({"message": "Transfer cancelled"})
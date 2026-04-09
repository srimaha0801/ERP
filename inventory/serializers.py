from rest_framework import serializers
from .models import Branch,Product,Stock,StockTransfer


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'
        read_only_fields = ['reserved_quantity']

    def validate(self, data):
        if data['reserved_quantity'] > data['quantity']:
            raise serializers.ValidationError(f'Reserved quantity ({self.reserved_quantity}) cannot exceed total quantity ({self.quantity})')
        return data

class BranchStockSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    available_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = [
            'product',
            'product_name',
            'quantity',
            'reserved_quantity',
            'available_quantity'
        ]

    def get_available_quantity(self, obj):
        return obj.available_quantity

class StockTransferSerializer(serializers.ModelSerializer):
    available_quantity = serializers.SerializerMethodField()
    class Meta:
        model = StockTransfer
        fields = '__all__'
        read_only_fields = ['transfer_id','status','requested_by','approved_by', 'cancelled_by']
    
    def get_available_quantity(self, obj):
        try:
            stock = Stock.objects.get(
                branch=obj.from_branch,
                product=obj.product
            )
            return stock.available_quantity
        except Stock.DoesNotExist:
            return 0

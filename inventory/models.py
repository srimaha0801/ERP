from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Branch(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    code        = models.CharField(max_length=10, unique=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.code}"

class Product(models.Model):
    sku             = models.CharField(max_length=10, unique=True)
    name            = models.CharField(max_length=100)
    unit            = models.CharField(max_length=20, default='pcs')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sku} - {self.name}"
    
class Stock(models.Model):
    branch              = models.ForeignKey(Branch, on_delete = models.PROTECT, related_name='stocks')
    product             = models.ForeignKey(Product, on_delete = models.PROTECT, related_name='stocks')
    quantity            = models.IntegerField(default=0) # total quantity
    reserved_quantity   = models.IntegerField(default=0) # for pending transfers
    last_updated        = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['branch', 'product']]  # to ensure only one stock record
        indexes         = [
                             models.Index(fields=['branch', 'product']),
                          ]

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity

    def __str__(self):
        return f"{self.branch.code} - {self.product.sku} - Quantity: {self.quantity}"


class StockTransfer(models.Model):

    class Status(models.TextChoices):
        PENDING   = 'PENDING','Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        FAILED    = 'FAILED', 'Failed'

    transfer_id  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quantity     = models.IntegerField(default=0)
    from_branch  = models.ForeignKey(Branch, on_delete = models.PROTECT, related_name="transfers_out")
    to_branch    = models.ForeignKey(Branch, on_delete = models.PROTECT, related_name="transfers_in" )
    product      = models.ForeignKey(Product, on_delete = models.PROTECT)
    status       = models.CharField(max_length=20, choices=Status, default=Status.PENDING)

    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True,blank=True)
    
    requested_by = models.ForeignKey(User, on_delete = models.PROTECT, related_name="transfers_requested")
    approved_by  = models.ForeignKey(User, on_delete = models.SET_NULL, null= True, blank= True, related_name= "transfers_approved")
    cancelled_by = models.ForeignKey(User, on_delete = models.SET_NULL, null= True, blank= True, related_name= "transfers_cancelled")

    def __str__(self):
        return f"{self.transfer_id} - {self.status}"
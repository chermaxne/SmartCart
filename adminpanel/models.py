from django.db import models
from storefront.models import Product, Customer, Recommendation

# Optional: Admin settings like thresholds for inventory alerts
class InventoryThreshold(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    threshold = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"{self.product.name} threshold: {self.threshold}"

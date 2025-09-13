from django.db import models


class InventoryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name


class InventoryItem(models.Model):
    category = models.ForeignKey(
        InventoryCategory, on_delete=models.PROTECT, related_name="items"
    )
    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=50, unique=True)
    quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=20, default="pcs")

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"


class StockMovement(models.Model):
    IN = "IN"
    OUT = "OUT"
    KIND_CHOICES = ((IN, "In"), (OUT, "Out"))

    item = models.ForeignKey(
        InventoryItem, on_delete=models.CASCADE, related_name="movements"
    )
    kind = models.CharField(max_length=3, choices=KIND_CHOICES)
    quantity = models.IntegerField()
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)


# Create your models here.

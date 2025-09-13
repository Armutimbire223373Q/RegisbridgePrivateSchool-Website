from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from students.models import StudentProfile


class InventoryCategory(models.Model):
    """Categories for inventory items"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_library = models.BooleanField(
        default=False, help_text="Mark as library category for books"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Inventory Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """Suppliers for inventory items"""

    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    """Enhanced inventory item model"""

    BOOK = "BOOK"
    UNIFORM = "UNIFORM"
    LAB = "LAB"
    BOARDING = "BOARDING"
    SUPPLIES = "SUPPLIES"
    EQUIPMENT = "EQUIPMENT"

    CATEGORY_CHOICES = [
        (BOOK, "Book"),
        (UNIFORM, "Uniform"),
        (LAB, "Lab Equipment"),
        (BOARDING, "Boarding Supply"),
        (SUPPLIES, "Office Supplies"),
        (EQUIPMENT, "Equipment"),
    ]

    UNIT_CHOICES = [
        ("PCS", "Pieces"),
        ("KG", "Kilograms"),
        ("L", "Liters"),
        ("M", "Meters"),
        ("SET", "Sets"),
        ("BOX", "Boxes"),
        ("BOOK", "Books"),
    ]

    # Basic information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        InventoryCategory, on_delete=models.CASCADE, related_name="items"
    )
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit")
    barcode = models.CharField(max_length=100, blank=True, unique=True, null=True)

    # Quantity and units
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="PCS")
    min_stock_level = models.PositiveIntegerField(
        default=10, help_text="Minimum stock level for alerts"
    )
    max_stock_level = models.PositiveIntegerField(
        default=1000, help_text="Maximum stock level"
    )

    # Pricing
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Library specific fields
    isbn = models.CharField(max_length=20, blank=True, help_text="For books")
    author = models.CharField(max_length=200, blank=True, help_text="For books")
    publisher = models.CharField(max_length=200, blank=True, help_text="For books")
    publication_year = models.PositiveIntegerField(null=True, blank=True)

    # Supplier and location
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True
    )
    location = models.CharField(
        max_length=100, blank=True, help_text="Storage location"
    )

    # Status and dates
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["barcode"]),
            models.Index(fields=["category", "name"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def is_low_stock(self):
        """Check if item is below minimum stock level"""
        return self.quantity <= self.min_stock_level

    @property
    def is_out_of_stock(self):
        """Check if item is out of stock"""
        return self.quantity == 0

    @property
    def available_quantity(self):
        """Get available quantity (not checked out for library items)"""
        if self.category.is_library:
            checked_out = self.checkouts.filter(returned_date__isnull=True).count()
            return self.quantity - checked_out
        return self.quantity


class StockMovement(models.Model):
    """Stock movement tracking"""

    IN = "IN"
    OUT = "OUT"
    ADJUSTMENT = "ADJUSTMENT"
    TRANSFER = "TRANSFER"
    DAMAGED = "DAMAGED"

    MOVEMENT_TYPES = [
        (IN, "Stock In"),
        (OUT, "Stock Out"),
        (ADJUSTMENT, "Adjustment"),
        (TRANSFER, "Transfer"),
        (DAMAGED, "Damaged/Lost"),
    ]

    item = models.ForeignKey(
        InventoryItem, on_delete=models.CASCADE, related_name="movements"
    )
    movement_type = models.CharField(max_length=15, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()  # Can be negative for OUT movements
    reference_number = models.CharField(max_length=50, blank=True)
    reason = models.CharField(max_length=200)
    notes = models.TextField(blank=True)

    # Cost tracking
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Who and when
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.item.name} - {self.movement_type} - {self.quantity}"

    def save(self, *args, **kwargs):
        # Calculate total cost
        if self.unit_cost and self.quantity:
            self.total_cost = self.unit_cost * abs(self.quantity)

        super().save(*args, **kwargs)

        # Update item quantity
        if self.movement_type == self.IN:
            self.item.quantity += self.quantity
        elif self.movement_type in [self.OUT, self.DAMAGED]:
            self.item.quantity = max(0, self.item.quantity - abs(self.quantity))
        elif self.movement_type == self.ADJUSTMENT:
            self.item.quantity = max(0, self.item.quantity + self.quantity)

        self.item.save()


class LibraryCheckout(models.Model):
    """Library book checkout system"""

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("OVERDUE", "Overdue"),
        ("RETURNED", "Returned"),
        ("LOST", "Lost"),
        ("DAMAGED", "Damaged"),
    ]

    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name="checkouts",
        limit_choices_to={"category__is_library": True},
    )
    borrower = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="library_checkouts"
    )

    # Dates
    checkout_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    returned_date = models.DateTimeField(null=True, blank=True)

    # Status and tracking
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="ACTIVE")
    renewal_count = models.PositiveIntegerField(default=0)
    max_renewals = models.PositiveIntegerField(default=2)

    # Fines
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fine_paid = models.BooleanField(default=False)

    # Notes
    checkout_notes = models.TextField(blank=True)
    return_notes = models.TextField(blank=True)

    # Staff tracking
    checked_out_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="checkouts_processed"
    )
    returned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="returns_processed",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-checkout_date"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["borrower"]),
        ]

    def __str__(self):
        return f"{self.borrower.user.get_full_name()} - {self.item.name}"

    @property
    def is_overdue(self):
        """Check if checkout is overdue"""
        if self.status == "RETURNED":
            return False
        return timezone.now().date() > self.due_date

    @property
    def days_overdue(self):
        """Calculate days overdue"""
        if not self.is_overdue:
            return 0
        return (timezone.now().date() - self.due_date).days

    def calculate_fine(self, daily_fine_rate=1.00):
        """Calculate fine for overdue items"""
        if self.is_overdue:
            return self.days_overdue * daily_fine_rate
        return 0

    def can_renew(self):
        """Check if item can be renewed"""
        return (
            self.renewal_count < self.max_renewals
            and self.status == "ACTIVE"
            and not self.is_overdue
        )

    def renew(self, days=14):
        """Renew the checkout"""
        if self.can_renew():
            self.due_date = timezone.now().date() + timezone.timedelta(days=days)
            self.renewal_count += 1
            self.save()
            return True
        return False

    def return_item(self, returned_to=None, return_notes=""):
        """Return the item"""
        self.returned_date = timezone.now()
        self.status = "RETURNED"
        self.returned_to = returned_to
        if return_notes:
            self.return_notes = return_notes

        # Calculate final fine
        if self.is_overdue:
            self.fine_amount = self.calculate_fine()

        self.save()

        # Create stock movement
        StockMovement.objects.create(
            item=self.item,
            movement_type=StockMovement.IN,
            quantity=1,
            reason="Library book returned",
            notes=f"Returned by {self.borrower.user.get_full_name()}",
            created_by=returned_to,
        )


class ProcurementRequest(models.Model):
    """Procurement requests for inventory items"""

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("SUBMITTED", "Submitted"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("ORDERED", "Ordered"),
        ("RECEIVED", "Received"),
        ("CANCELLED", "Cancelled"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("URGENT", "Urgent"),
    ]

    # Request details
    request_number = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()

    # Status and priority
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="DRAFT")
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="MEDIUM"
    )

    # Dates
    requested_date = models.DateTimeField(default=timezone.now)
    required_date = models.DateField(help_text="When is this needed by?")
    approved_date = models.DateTimeField(null=True, blank=True)

    # People
    requested_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="procurement_requests"
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_procurements",
    )

    # Budget
    estimated_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    actual_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Notes
    justification = models.TextField(help_text="Why is this procurement needed?")
    approval_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-requested_date"]
        permissions = [
            ("can_approve_procurement", "Can approve procurement requests"),
            ("can_view_all_procurements", "Can view all procurement requests"),
        ]

    def __str__(self):
        return f"{self.request_number} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.request_number:
            # Generate request number
            year = timezone.now().year
            count = ProcurementRequest.objects.filter(created_at__year=year).count() + 1
            self.request_number = f"PR{year}{count:04d}"

        super().save(*args, **kwargs)


class ProcurementRequestItem(models.Model):
    """Items in a procurement request"""

    request = models.ForeignKey(
        ProcurementRequest, on_delete=models.CASCADE, related_name="items"
    )
    item = models.ForeignKey(
        InventoryItem, on_delete=models.CASCADE, null=True, blank=True
    )

    # Item details (for new items or items not in inventory)
    description = models.CharField(max_length=200)
    specifications = models.TextField(blank=True)

    # Quantities and pricing
    quantity_requested = models.PositiveIntegerField()
    estimated_unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_total = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False
    )

    # Supplier preference
    preferred_supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.estimated_total = self.quantity_requested * self.estimated_unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} - {self.quantity_requested} units"


class InventoryAudit(models.Model):
    """Inventory audit records"""

    STATUS_CHOICES = [
        ("PLANNED", "Planned"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    audit_number = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Scope
    category = models.ForeignKey(
        InventoryCategory, on_delete=models.CASCADE, null=True, blank=True
    )
    location = models.CharField(max_length=100, blank=True)

    # Status and dates
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="PLANNED")
    planned_date = models.DateField()
    start_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)

    # People
    auditor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="inventory_audits"
    )

    # Summary
    items_audited = models.PositiveIntegerField(default=0)
    discrepancies_found = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-planned_date"]

    def __str__(self):
        return f"{self.audit_number} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.audit_number:
            year = timezone.now().year
            count = InventoryAudit.objects.filter(created_at__year=year).count() + 1
            self.audit_number = f"AUD{year}{count:03d}"

        super().save(*args, **kwargs)


class InventoryAuditItem(models.Model):
    """Individual item audit records"""

    audit = models.ForeignKey(
        InventoryAudit, on_delete=models.CASCADE, related_name="audit_items"
    )
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)

    # Counts
    system_quantity = models.PositiveIntegerField(help_text="Quantity in system")
    physical_quantity = models.PositiveIntegerField(help_text="Actual counted quantity")

    # Analysis
    variance = models.IntegerField(editable=False)  # physical - system
    variance_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Notes
    notes = models.TextField(blank=True)
    action_required = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.variance = self.physical_quantity - self.system_quantity
        self.variance_value = abs(self.variance) * self.item.cost_price
        self.action_required = abs(self.variance) > 0

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - Variance: {self.variance}"
